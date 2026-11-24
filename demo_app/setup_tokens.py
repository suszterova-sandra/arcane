"""Copy the persona API tokens into demo_app/.tokens.json and write web/src/personas.json, the persona list the
static GitHub Pages build uses (same shape as server.py's PERSONAS, from ../exzeo/personas.csv).

    python3 demo_app/setup_tokens.py

The Exzeo personas are two existing demo users moved from Arcane (arc.routeo.marketing, arc.autonova.marketing);
their tokens come from ../tenancy/.tokens.json. Each has access to one Exzeo carrier workspace only; none is an
organization admin. The carrier tokens are committed and compiled into the static build on purpose, so visitors can switch users.
"""
import json
from pathlib import Path

import server

HERE = Path(__file__).resolve().parent
tokens = json.loads((HERE.parent / "tenancy" / ".tokens.json").read_text())
assert all(not u.startswith(("sandra", "admin")) for u in tokens), "never embed a real admin token"
# the admin's token stays local (server.py reads it from ../tenancy/.tokens.json); on GitHub Pages the admin is a GoodData sign-in
public = [p for p in server.PERSONAS if p["id"] != "admin"]
(HERE / ".tokens.json").write_text(json.dumps({p["userId"]: tokens[p["userId"]] for p in public}, indent=2) + "\n")
(HERE / "web" / "src" / "personas.json").write_text(json.dumps(server.PERSONAS, indent=1, ensure_ascii=False) + "\n")
print(f"{len(server.PERSONAS)} personas, tokens -> {HERE / '.tokens.json'}, list -> web/src/personas.json")
