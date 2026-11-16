#!/usr/bin/env python3
"""Load csv/*.csv into MotherDuck database `arcane` (schema main).

    pip install duckdb==1.5.6          # MotherDuck does not support duckdb 2.x yet
    export motherduck_token=...         # or MOTHERDUCK_TOKEN
    python3 load_motherduck.py [--db arcane]

Tables are created from ddl/postgresql.sql types (NOT NULL + PK), then filled from the CSVs.
"""
import argparse
import os

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="arcane")
    ap.add_argument("--local", help="load into a local DuckDB file instead of MotherDuck (for testing)")
    args = ap.parse_args()

    # read the schema from generate.py without re-running the generator
    src = open(os.path.join(HERE, "generate.py")).read()
    head = src.split("# ---------------------------------------------------------------------------\n# Reference data")[0]
    ns = {"__file__": os.path.join(HERE, "generate.py"), "__name__": "schema"}
    exec(compile(head, "generate.py", "exec"), ns)
    schema, pks = ns["SCHEMA"], ns["PRIMARY_KEYS"]

    # token from env, or from arcane/.env (gitignored): motherduck_token=...
    env_file = os.path.join(HERE, "..", ".env")
    if not (os.environ.get("motherduck_token") or os.environ.get("MOTHERDUCK_TOKEN")) and os.path.exists(env_file):
        for line in open(env_file):
            k, _, v = line.strip().partition("=")
            if k.lower() == "motherduck_token" and v:
                os.environ["motherduck_token"] = v.strip().strip('"\'')

    if args.local:
        con = duckdb.connect(args.local)
    else:
        con = duckdb.connect("md:")
        con.execute(f"CREATE DATABASE IF NOT EXISTS {args.db}")
        con.execute(f"USE {args.db}")
    for t, cols in schema.items():
        body = ", ".join(f"{c} {typ} NOT NULL" for c, typ in cols) + f", PRIMARY KEY ({', '.join(pks[t])})"
        con.execute(f"CREATE OR REPLACE TABLE {t} ({body})")
        path = os.path.join(HERE, "csv", f"{t}.csv")
        con.execute(f"INSERT INTO {t} SELECT * FROM read_csv('{path}', header=true, all_varchar=false, "
                    f"columns={{{', '.join(repr(c) + ': ' + repr(typ) for c, typ in cols)}}})")
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"  {t:<22}{n:>10,}")


if __name__ == "__main__":
    main()
