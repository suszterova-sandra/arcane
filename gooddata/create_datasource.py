#!/usr/bin/env python3
"""Create / update the GoodData data source `arcane-motherduck` (MotherDuck database `arcane`, schema main).

The MotherDuck token comes from arcane/.env (motherduck_token=...). If it's missing, a MotherDuck browser login is
started (confirm the printed code within 1 minute), and the token is saved to arcane/.env (gitignored, chmod 600).
The token is never printed.

    python3 create_datasource.py          # needs GOODDATA_API_TOKEN in arcane/.env or the environment
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(HERE, "..", ".env")
HOST = os.environ.get("GD_HOST", "https://sandrasuszterova.demo.cloud.gooddata.com")
DS_ID = "arcane-motherduck"
JSONAPI = "application/vnd.gooddata.api+json"


def read_env():
    vals = {}
    if os.path.exists(ENV):
        for line in open(ENV):
            k, _, v = line.strip().partition("=")
            if k and v:
                vals[k] = v.strip().strip('"\'')
    return vals


def save_env(key, value):
    vals = read_env()
    vals[key] = value
    with open(ENV, "w") as f:
        f.write("".join(f"{k}={v}\n" for k, v in vals.items()))
    os.chmod(ENV, 0o600)


def md_token():
    tok = read_env().get("motherduck_token") or os.environ.get("motherduck_token")
    if tok:
        return tok
    import duckdb
    import contextlib, io
    con = duckdb.connect("md:")             # browser SSO
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):   # PRAGMA PRINT_MD_TOKEN prints the token - never let it reach the log
        row = con.execute("PRAGMA PRINT_MD_TOKEN").fetchone()
    tok = row[0] if row else next(l.split("=", 1)[1].strip() for l in buf.getvalue().splitlines()
                                  if "motherduck_token=" in l)
    save_env("motherduck_token", tok)
    print("MotherDuck token saved to arcane/.env")
    return tok


def call(method, path, body=None, ctype=JSONAPI):
    gd = os.environ.get("GOODDATA_API_TOKEN") or read_env().get("GOODDATA_API_TOKEN")
    req = urllib.request.Request(HOST + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {gd}", "Content-Type": ctype,
                                          "Accept": ctype})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


def main():
    tok = md_token()
    body = {"data": {"id": DS_ID, "type": "dataSource", "attributes": {
        "name": "Arcane (MotherDuck)", "type": "MOTHERDUCK", "url": "jdbc:duckdb:md:arcane", "schema": "main",
        "token": base64.b64encode(tok.encode()).decode()}}}   # GoodData expects the MotherDuck token base64-encoded
    status, resp = call("GET", f"/api/v1/entities/dataSources/{DS_ID}")
    if status == 200:
        status, resp = call("PUT", f"/api/v1/entities/dataSources/{DS_ID}", body)
    else:
        status, resp = call("POST", "/api/v1/entities/dataSources", body)
    if status not in (200, 201):
        sys.exit(f"data source: {status} {resp}")
    print(f"data source {DS_ID}: ok")
    status, resp = call("POST", f"/api/v1/actions/dataSources/{DS_ID}/scan",
                        {"separator": "__", "scanTables": True, "scanViews": False}, "application/json")
    if status != 200:
        sys.exit(f"scan failed: {status} {resp}")
    tables = sorted(t["path"][-1] for t in resp["pdm"]["tables"])
    print(f"connection ok - {len(tables)} tables: {', '.join(tables)}")


if __name__ == "__main__":
    main()
