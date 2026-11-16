"""Copy the persona API tokens (created by ../tenancy/reconcile.py --tokens) into demo_app/.tokens.json and write
web/src/personas.json, the persona list the static GitHub Pages build uses (same shape as server.py's PERSONAS).

    python3 tenancy/reconcile.py --tokens     # (re)create tokens for every persona incl. arc.admin
    python3 demo_app/setup_tokens.py

The tokens belong to demo users (arc.*) with access to the Arcane demo workspaces only; none is an organization
admin. They are committed and compiled into the static build on purpose, so visitors can switch users.
"""
import json
from pathlib import Path

import server

HERE = Path(__file__).resolve().parent
tokens = json.loads((HERE.parent / "tenancy" / ".tokens.json").read_text())
assert all(not u.startswith(("sandra", "admin")) for u in tokens), "never embed a real admin token"
(HERE / ".tokens.json").write_text(json.dumps({p["userId"]: tokens[p["userId"]] for p in server.PERSONAS}, indent=2) + "\n")
(HERE / "web" / "src" / "personas.json").write_text(json.dumps(server.PERSONAS, indent=1, ensure_ascii=False) + "\n")
print(f"{len(server.PERSONAS)} personas, tokens -> {HERE / '.tokens.json'}, list -> web/src/personas.json")
