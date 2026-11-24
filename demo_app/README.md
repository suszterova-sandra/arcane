# Exzeo demo app

React (Vite + TypeScript) portal around the **Exzeo** workspaces on `sandrasuszterova.demo.cloud.gooddata.com`:
the Exzeo template workspace (`e74a1eaa18f74706b94e39f91552efe7`, "Exzeo Carrier Analytics (template)") and one
white-labelled workspace per carrier (Homeowners Choice, TypTap Insurance, CORE). Switch between demo users in one
click. Every number, dashboard and AI answer comes back with that user's own GoodData permissions and data filters.
Ported from the Arcane portal; Exzeo workspaces, themes and the AI Publisher report come from `../exzeo/setup.py`.

**Live (GitHub Pages):** https://suszterova-sandra.github.io/arcane/ (still the Arcane build until this is pushed)

## Personas (`../exzeo/personas.csv`)

| User | Carrier workspace | Access | What to show |
|---|---|---|---|
| Elena Ruiz (`arc.routeo.marketing`) | Homeowners Choice | VIEW + USE_AI_ASSISTANT | Standard dashboards in the carrier's brand, AI briefing, AI Assistant; no authoring |
| Marc Fontaine (`arc.autonova.marketing`) | TypTap Insurance | ANALYZE + USE_AI_ASSISTANT | Everything Elena has + Analyze, New dashboard, AI-built visualizations |

Both are existing demo users moved over from Arcane (no new users: the org is at its user limit). Each sees only its
own carrier workspace. The AI Publisher report (`business_performance_report`) is only readable with the
CREATE_DOCUMENT permission, so the app hides the AI Report tab for users without it; PDF export needs EXPORT.
There is no admin persona, so the Control Center screen is not reachable.

**Tokens:** the two users' existing API tokens (from `../tenancy/.tokens.json`) are copied into
`demo_app/.tokens.json` by `setup_tokens.py` and compiled into the static build, so visitors can switch users
without logging in. Neither user is an organization admin. The organization admin token in `../.env` is used only
locally (`server.py` overview, `snapshot_overview.py`) and is never committed.

## Run / publish

```bash
# once (from arcane/)
python3 exzeo/setup.py                  # Exzeo workspaces, themes, WDFs, custom dashboard
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
