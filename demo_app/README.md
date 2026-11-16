# Arcane demo app

React (Vite + TypeScript) portal around the **Arcane** workspaces on `sandrasuszterova.demo.cloud.gooddata.com`:
one template workspace (Arcane) and one white-labelled workspace per advertiser. Switch between demo users in one
click. Every number, dashboard, report and AI answer comes back with that user's own GoodData permissions.
This is a port of the Viventium / conference portal.

**Live (GitHub Pages):** https://suszterova-sandra.github.io/arcane/

## Personas

| User | Workspace | Package | Data products | AI |
|---|---|---|---|---|
| Arcane Admin (`arc.admin`, the app's admin) | template + every client (inherited) | Arcane team | all 8 | ✓ + agents |
| Camille Marchand (`arc.consultant`), media consultant | template (all clients) | Arcane team | all 8 | ✓ + agents |
| Léa Dubois (`arc.secondevie.ecom`), Seconde Vie | `secondevie` | Top Account | 7 (all client-facing) | ✓ + agents |
| Marc Fontaine (`arc.autonova.marketing`), AutoNova | `autonova` | Top Account | 6 (no Product Feed) | ✓ + agents |
| Elena Ruiz (`arc.routeo.marketing`), Routéo | `routeo` | Standard | 4 (Core + Standard) | ✓ + Briefing / Performance agents |

**Tokens:** every persona's API token is compiled into the static build (`demo_app/.tokens.json`, committed on
purpose), so visitors can switch between all users without logging in. They belong to demo users with access to the
Arcane demo workspaces only; none is an organization admin. The organization admin token in `../.env` is used only
locally (`server.py` overview, `setup_agents.py`, `snapshot_overview.py`) and is never committed.
Rotate the tokens with `python3 tenancy/reconcile.py --tokens && python3 demo_app/setup_tokens.py`, then commit.

## Run / publish

```bash
# once (from arcane/)
python3 tenancy/reconcile.py --tokens   # personas + API tokens
python3 demo_app/setup_tokens.py        # -> demo_app/.tokens.json + web/src/personas.json
python3 demo_app/setup_agents.py        # 3 Arcane agents in AI Hub
python3 demo_app/snapshot_overview.py   # Control Center snapshot -> web/public/overview.json
cd demo_app/web && npm install

# local (two terminals)
python3 demo_app/server.py              # backend on 127.0.0.1:8765
cd demo_app/web && npm run dev          # UI on http://localhost:5173 (an allowed origin of the org)

# GitHub Pages: push to main; .github/workflows/pages.yml builds with VITE_STATIC=1 (no backend)
```

## Screens

| Screen | What it shows |
|---|---|
| **Home** | The user's headline KPIs (last full quarter vs the one before), key drivers by **market** and **platform**, an AI briefing and a watch list, all from the user's data products |
| **Control Center** (admin) | The template and client workspaces in their themes, grouped by package (Top Account / Standard), the five access layers, who sees what, and the AI agents |
| **Dashboards** | The user's data-product dashboards, an agentic summary, and **+ New dashboard** for ANALYZE users |
| **AI Report** | The Publisher report of the user's data products, rendered in the client's theme; **Export PDF** runs as the user |
| **Analyze** | Analytical Designer for ANALYZE users; locked for VIEW users |
| **AI Assistant** | GoodData's assistant as the user, plus the agents: Client Briefing, Performance Doctor, Budget & Pacing |
