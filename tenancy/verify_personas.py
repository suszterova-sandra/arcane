#!/usr/bin/env python3
"""
Act as each persona (own API token from tenancy/.tokens.json) and check the multitenancy + permission design:
  - only the persona's own client's data is visible (workspace data filter)
  - the dashboards the persona sees = their data products
  - a metric of every data product the persona is NOT entitled to is refused (object-level permissions)

    set -a; . ../.env; set +a
    python3 tenancy/verify_personas.py
"""
import csv
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = os.environ.get("GD_HOST", "https://sandrasuszterova.demo.cloud.gooddata.com")
TOKENS = json.loads((HERE / ".tokens.json").read_text())
DP = json.load(open(HERE.parent / "gooddata" / "data_products.json"))
PROBE = {"Paid Media Performance": "pm_cost", "Social Creatives": "sc_spend", "Web Analytics & GEO": "wa_sessions",
         "Budget & Pacing": "bp_planned", "Product Feed & Shopping": "pf_cost", "CRM & Offline Sales": "crm_leads",
         "Measurement & Incrementality": "mi_tests", "Arcane Operations": "op_requests"}


def call(token, method, path, body=None):
    req = urllib.request.Request(HOST + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def execute(token, ws, metric, label=None):
    attrs = [{"localIdentifier": "a", "label": {"identifier": {"id": label, "type": "label"}}}] if label else []
    body = {"execution": {"attributes": attrs, "filters": [],
                          "measures": [{"localIdentifier": "m", "definition": {"measure": {"item": {"identifier": {
                              "id": metric, "type": "metric"}}}}}]},
            "resultSpec": {"dimensions": ([{"localIdentifier": "d0", "itemIdentifiers": ["a"]}] if label else [])
                           + [{"localIdentifier": "d1", "itemIdentifiers": ["measureGroup"]}]}}
    s, r = call(token, "POST", f"/api/v1/actions/workspaces/{ws}/execution/afm/execute", body)
    if s != 200:
        return None, s
    s, res = call(token, "GET", f"/api/v1/actions/workspaces/{ws}/execution/afm/execute/result/"
                                f"{r['executionResponse']['links']['executionResult']}")
    if s != 200:
        return None, s
    if not label:
        return res["data"], 200
    return [h["attributeHeader"]["labelValue"] for h in res["dimensionHeaders"][0]["headerGroups"][0]["headers"]], 200


def main():
    all_ok = True
    for p in csv.DictReader(open(HERE / "personas.csv")):
        tok, ws = TOKENS[p["user_id"]], p["workspace_id"]
        own = (list(DP["products"]) if p["data_products"] == "ALL" else DP["entitlements"][p["client_id"]])
        print(f"\n=== {p['first_name']} {p['last_name']} · {p['role']} ({p['user_id']})")
        s, r = call(tok, "GET", f"/api/v1/entities/workspaces/{ws}/analyticalDashboards?size=100")
        dashes = sorted(d["attributes"]["title"] for d in r["data"]) if s == 200 else f"HTTP {s}"
        print(f"  dashboards: {dashes}")
        clients, _ = execute(tok, ws, "pm_cost", "clients.client_id")
        print(f"  clients visible: {clients}")
        expected = ["autonova", "routeo", "secondevie"] if p["client_id"] == "ALL" else [p["client_id"]]
        if p.get("hierarchy") == "yes":
            s, r = call(tok, "GET", "/api/v1/entities/workspaces?size=100")
            seen = {w["id"] for w in r["data"]} if s == 200 else set()
            print(f"  workspaces (inherited): {sorted(seen)}")
        checks = [("own client(s) only", sorted(clients or []) == expected),
                  (f"{len(own)} dashboards (= data products)", isinstance(dashes, list) and len(dashes) == len(own))]
        for prod, metric in PROBE.items():
            _, s = execute(tok, ws, metric)
            if prod in own:
                checks.append((f"{prod}: usable", s == 200))
            else:
                checks.append((f"{prod}: refused (HTTP {s})", s != 200))
        # publisher reports: documents have no permissions of their own - a report is usable only if the persona
        # can read every visualization in it (object-level permissions of the data product)
        s, r = call(tok, "GET", f"/api/v1/entities/workspaces/{ws}/documents?size=100")
        usable, blocked = [], []
        for d in (r["data"] if s == 200 else []):
            vis = set(re.findall(r'"identifier": "([a-z0-9_]+)", "type": "insight"', json.dumps(d["attributes"]["content"])))
            ok = all(call(tok, "GET", f"/api/v1/entities/workspaces/{ws}/visualizationObjects/{v}")[0] == 200 for v in vis)
            (usable if ok else blocked).append(d["attributes"]["title"])
        print(f"  reports usable: {sorted(usable)}")
        print(f"  reports blocked (content restricted): {sorted(blocked)}")
        checks.append((f"{len(own)} usable reports (= data products)", len(usable) == len(own)))
        for name, passed in checks:
            all_ok &= passed
            print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print("\nALL CHECKS PASSED" if all_ok else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
