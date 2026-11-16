#!/usr/bin/env python3
"""
Create / update the Arcane demo personas (personas.csv is the source of truth).

    set -a; . ../.env; set +a
    python3 tenancy/reconcile.py              # users, data-product groups, workspace permissions
    python3 tenancy/reconcile.py --tokens     # also (re)create API tokens -> tenancy/.tokens.json (gitignored)

data_products: ALL = every data product, ENTITLED = the client's entitlements (client_data_products /
gooddata/data_products.json). Core (Paid Media Performance) is open to all workspace users anyway.
Workspace permissions = the tier: VIEW / ANALYZE / EXPORT / CREATE_AUTOMATION / USE_AI_ASSISTANT.
hierarchy = yes: the same permissions are inherited by every child workspace (arc.admin).
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = os.environ.get("GD_HOST", "https://sandrasuszterova.demo.cloud.gooddata.com")
JSONAPI = "application/vnd.gooddata.api+json"
TOKEN_ID = "arcane-demo"
DP = json.load(open(HERE.parent / "gooddata" / "data_products.json"))


def call(method, path, body=None, ctype=JSONAPI):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(6):
        req = urllib.request.Request(HOST + path, method=method, data=data,
                                     headers={"Authorization": f"Bearer {os.environ['GOODDATA_API_TOKEN']}",
                                              "Content-Type": ctype, "Accept": "application/json, " + JSONAPI})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
                continue
            return e.code, e.read().decode()[:500]
    return 429, "rate limited"


def products_of(p):
    if p["data_products"] == "ALL":
        return list(DP["products"])
    if p["data_products"] == "ENTITLED":
        return DP["entitlements"][p["client_id"]]
    return p["data_products"].split("|")


def main():
    personas = list(csv.DictReader(open(HERE / "personas.csv")))
    for p in personas:
        uid = p["user_id"]
        groups = [DP["products"][d]["user_group"] for d in products_of(p)]
        body = {"data": {"id": uid, "type": "user",
                         "attributes": {"firstname": p["first_name"], "lastname": p["last_name"],
                                        "email": f"{uid}@example.com"},
                         "relationships": {"userGroups": {"data": [{"id": g, "type": "userGroup"} for g in groups]}}}}
        s, r = call("POST", "/api/v1/entities/users", body)
        if s == 409:
            s, r = call("PUT", f"/api/v1/entities/users/{uid}", body)
        if s not in (200, 201, 204):
            sys.exit(f"user {uid}: {s} {r}")
        perms = p["workspace_permissions"].split("|")
        s, r = call("POST", f"/api/v1/actions/workspaces/{p['workspace_id']}/managePermissions",
                    [{"assigneeIdentifier": {"id": uid, "type": "user"}, "permissions": perms,
                      "hierarchyPermissions": perms if p.get("hierarchy") == "yes" else []}], "application/json")
        if s not in (200, 204):
            sys.exit(f"permissions {uid}: {s} {r}")
        print(f"  {uid:<26} {p['workspace_id']:<34} {'|'.join(perms):<50} {len(groups)} product groups")

    if "--tokens" in sys.argv:
        out = HERE / ".tokens.json"
        store = {}
        for p in personas:
            uid = p["user_id"]
            call("DELETE", f"/api/v1/entities/users/{uid}/apiTokens/{TOKEN_ID}")
            s, r = call("POST", f"/api/v1/entities/users/{uid}/apiTokens",
                        {"data": {"id": TOKEN_ID, "type": "apiToken", "attributes": {}}})
            if s not in (200, 201):
                sys.exit(f"token {uid}: {s} {r}")
            store[uid] = r["data"]["attributes"]["bearerToken"]
        out.write_text(json.dumps(store, indent=2))
        out.chmod(0o600)
        print(f"tokens -> {out}")


if __name__ == "__main__":
    main()
