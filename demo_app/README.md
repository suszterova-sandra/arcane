# FranConnect demo app

React (Vite + TypeScript) portal around the **FranConnect** workspaces on `sandrasuszterova.demo.cloud.gooddata.com`:
the FranConnect template workspace (`ecommerce-parent`, "FranConnect Analytics (template)") and one white-labelled
workspace per franchise brand (Arby's, Paris Baguette, Floor Coverings International: FranConnect case-study customers). Switch between demo
users in one click. Every number, dashboard and AI answer comes back with that user's own GoodData permissions and
data filters. Workspaces, themes and analytics come from `../../FranConnect` (setup.py, gd deploy); this portal was
the Exzeo portal before (Exzeo set-up still in `../exzeo/`).

**Live (GitHub Pages):** https://suszterova-sandra.github.io/arcane/

## Personas (`../franconnect/personas.csv`)

| User | Brand workspace | Access | What to show |
|---|---|---|---|
| Elena Ruiz (`arc.routeo.marketing`) | Arby's (`franconnect_brightside`) | VIEW + USE_AI_ASSISTANT | Standard dashboards + PoC must-haves in the brand's theme, AI briefing, AI Assistant; no authoring |
| Marc Fontaine (`arc.autonova.marketing`) | Paris Baguette (`franconnect_flexfit`) | ANALYZE + USE_AI_ASSISTANT | Everything Elena has + Analyze, New dashboard, AI-built visualizations |
| Admin | FranConnect template (`ecommerce-parent`) | GoodData sign-in on Pages; `arc.admin` locally | Control Center: template, brand workspaces, data filters, access |

Both users are existing demo users moved from the Exzeo carriers (no new users: the org is at its user limit). Each
sees only its own brand workspace. There is no AI Publisher report in the FranConnect template yet, and neither user has
CREATE_DOCUMENT, so the AI Report tab is hidden.

**Tokens:** the two users' existing API tokens (from `../tenancy/.tokens.json`) are copied into
`demo_app/.tokens.json` by `setup_tokens.py` and compiled into the static build, so visitors can switch users
without logging in. Neither user is an organization admin. The organization admin token in `../.env` is used only
locally (`server.py` overview, `snapshot_overview.py`) and is never committed.

## Run / publish

```bash
# once (from arcane/)
python3 demo_app/setup_tokens.py        # -> demo_app/.tokens.json + web/src/personas.json
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
