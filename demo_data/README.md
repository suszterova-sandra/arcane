# Arcane – GoodData demo data source

Demo data for [Arcane](https://www.arcane.run), a Paris-based media & data agency (SEA, SMA, retail media, video,
feed engineering, measurement). Their setup today: **Adverity → BigQuery → scheduled queries → one Looker Studio
report per client**, plus a separate BigQuery conversational-analytics page.
The demo shows the same data in **GoodData**: one white-labelled workspace per advertiser, **one shared semantic layer**
split into data products, with object-level permissions per client package, per-client business definitions and an AI assistant on top. This is the same
pattern as the Primelis migration.

```
python3 generate.py                       # deterministic (seed), ~25 s → csv/*.csv (~1.1 M rows, ~140 MB) + ddl/*.sql + data_products.json
pip install duckdb==1.5.6                 # MotherDuck doesn't support duckdb 2.x
export motherduck_token=...
python3 load_motherduck.py                # → MotherDuck database `arcane` (schema main)
python3 load_motherduck.py --local x.duckdb   # local test
```

`ddl/` has `postgresql.sql` (also DuckDB/MotherDuck), **`bigquery.sql`** (Arcane's real warehouse: `bq load` commands
included) and `snowflake.sql`. Data covers **2024-01-01 → 2026-11-15**. Media budgets are planned through Dec 2026.
There are no NULLs: "not applicable" dates are `1900-01-01`, text is `N/A` and numbers are `0`.

## One shared model, split into data products

All clients use **one shared model** in the parent workspace. There are no per-client LDM extensions. Each client
workspace is filtered to its own data by `wdf__client_id`. What a client *sees* is controlled by **object-level permissions
(OLP) per data product**, so each top-account "custom recipe" becomes an add-on that is switched on per client.

| Data product | Package | Datasets | User group |
|---|---|---|---|
| *Shared Dimensions* | always | `clients`, `platforms`, `markets`, `campaigns` (+ date dimensions) | everyone |
| **Paid Media Performance** | Core | `ad_performance_daily` | `dp_paid_media_performance` |
| **Social Creatives** | Standard | `creatives`, `creative_performance_daily` | `dp_social_creatives` |
| **Web Analytics & GEO** | Standard | `web_analytics_daily` | `dp_web_analytics_and_geo` |
| **Budget & Pacing** | Standard | `media_budgets` | `dp_budget_and_pacing` |
| **Product Feed & Shopping** | Premium add-on | `products`, `product_performance_weekly` | `dp_product_feed_and_shopping` |
| **CRM & Offline Sales** | Premium add-on | `business_locations`, `crm_leads` | `dp_crm_and_offline_sales` |
| **Measurement & Incrementality** | Premium add-on | `incrementality_tests` | `dp_measurement_and_incrementality` |
| **Arcane Operations** | Internal (Arcane only) | `data_requests`, `client_data_products` | `dp_arcane_operations` |

**Rules for building on the model.** `generate.py` checks the first two and fails if they're broken:
1. A dataset references only *Shared Dimensions* or datasets of its own data product.
2. There is exactly one join path between any two datasets. `products` and `business_locations` carry `wdf__client_id`
   but don't reference `clients`.
3. A product's metrics may also use **Core** facts, e.g. cost per sold car = CRM won deals + ad cost. Core is visible to
   every client and every Arcane user, so cross-product metrics never break.
4. Each metric, visualisation and dashboard belongs to exactly one product (tag = product name). Then the product's
   user group gets VIEW and *all workspace users* lose it. This is the same pattern as `viventium/gooddata/apply_permissions.py`.

**Entitlements** are data: `client_data_products` (client × product, package, enabled, since, user group). The same
information is in `data_products.json`, which also lists the dataset references for the LDM builder:

| Client | Core + Standard | Product Feed | CRM & Offline Sales | Measurement |
|---|---|---|---|---|
| `secondevie` (Top Account) | ✓ | ✓ | ✓ (Seconde Vie Pro B2B) | ✓ |
| `autonova` (Top Account) | ✓ | – | ✓ (dealer leads) | ✓ |
| `routeo` (Standard, long tail) | ✓ | – | – | – (upsell: tests exist in the data, but Routéo can't see them) |

Users are added to the `dp_*` groups of their client's enabled products. Arcane consultants get every product, including Arcane Operations.

## Tenants (fictional advertisers, modelled on Arcane's case-study sectors)

| Client ID | Advertiser | Industry | Tier | Markets | Add-ons |
|---|---|---|---|---|---|
| `secondevie` | Seconde Vie | Refurbished electronics marketplace | Top Account | FR DE ES IT GB US | Product feed (SmartFeeds), B2B CRM (Seconde Vie Pro), incrementality |
| `autonova` | AutoNova Automobiles | Dealer network (12 dealerships) | Top Account | FR | CRM leads & offline sales (SmartConversion), incrementality |
| `routeo` | Routéo Location | Car & van rental | Standard (long tail) | FR ES IT DE GB | – |

`clients` holds each client's **business KPI definition** (e.g. *"Lead qualifié = CRM status reached 'Qualified'"*,
*"Réservations = confirmed bookings, cancellations excluded"*), its target (ROAS or CPA), and the assigned media and
data consultants. This is the material for per-client metric definitions and AI memory.

## Tables

| Table | Grain | Notes |
|---|---|---|
| `platforms` *(global)* | ad platform | Google Ads, Microsoft, Meta, TikTok, Pinterest, Amazon, DV360, Non-paid; Adverity connector name |
| `markets` *(global)* | country | currency, FX, capital lat/long (geo charts) |
| `clients` | advertiser | tier, KPI definition, target, consultants |
| `campaigns` | campaign | Arcane naming convention `SV_FR_GADS_SEA_Generic_Smar`, type, channel group, funnel stage, product line, bidding. Non-paid "campaigns" (`*_NonPaid_OrganicDirect`) hold organic CRM leads |
| `ad_performance_daily` | campaign × day × device | impressions, clicks, cost (EUR + local), platform conversions & value, video views, engagements, **search impression share** columns (eligible / lost to budget / lost to rank) |
| `creatives` / `creative_performance_daily` | social creative × day | Meta, TikTok. Format, theme, production source (incl. *AI-generated (Arcane AI Lab)* from Jun 2025), fatigue built in |
| `products` / `product_performance_weekly` | product × campaign × week | Shopping, PMax, Microsoft Shopping, Amazon. `feed_optimized` = SmartFeeds |
| `web_analytics_daily` | client × market × day × channel group | GA4 + backend: sessions, transactions, revenue, margin, new customers, leads. Includes the **AI Assistants (ChatGPT, Perplexity, Gemini)** channel (GEO) |
| `business_locations` | dealership / sales office | AutoNova's 12 dealerships, Seconde Vie Pro's 5 B2B sales offices (lat/long) |
| `crm_leads` | lead | Generic funnel: lead → contacted → qualified → opportunity → won, plus deal value, gross profit, offline conversion uploaded. AutoNova: test drive → car sold. Seconde Vie Pro: quote sent → device fleet deal. Paid leads come from campaigns with objective *Leads*: AutoNova's non-awareness campaigns, and Seconde Vie's *Search - B2B Leads* and *LinkedIn - Lead Gen Forms* |
| `media_budgets` | client × platform × market × month | planned budget, target ROAS / CPA (pacing) |
| `incrementality_tests` | test | geo-lift / conversion-lift results, iROAS, significance, recommendation |
| `data_requests` | request | Arcane's current "Google Form → project tool → data consultant" loop: type, summary, days to deliver |
| `client_data_products` | client × data product | entitlements that drive the OLP groups |

## LDM (single join path)

```
ad_performance_daily ──────────┐
creative_perf → creatives ─────┤→ campaigns → clients, platforms, markets
product_perf  → products ──────┤
crm_leads     → business_locations ─┘ (crm_leads → campaigns)
web_analytics_daily → clients, markets
media_budgets, incrementality_tests → clients, platforms, markets
data_requests, client_data_products → clients
```
Every fact has its own date (`date`, `week_start_date`, `lead_date`, `budget_month`, ...). WDF is `wdf__client_id` on
every tenant table. `platforms` and `markets` are global.

Useful metrics: ROAS = conversion value / cost. **Blended ROAS (MER)** = backend revenue (web_analytics) / ad cost.
Search impression share = `SUM(search_impressions)/SUM(search_eligible_impressions)`.
**Over-attribution** = platform conversions / backend paid transactions (≈1.1 brand search to ≈2 social).
Cost per qualified lead, cost per won deal and pipeline value come from `crm_leads` combined with Core ad cost.

## Built-in demo stories

1. **Performance drop to diagnose with AI (Seconde Vie, Germany).** From 2026-10-20, DE *Search - Generic* is budget-capped.
   Spend is −40%, impression share falls from 55% to 31%, *lost IS (budget)* rises from 7% to 43%, and conversions are about −35%.
   FR and other markets are stable. `media_budgets` shows DE Google **under-pacing** (Nov plan €353k, ~€160k spent by mid-month),
   just before Black Friday. This is the "performance dropped, let me deep-dive in natural language" scenario from the call.
2. **Tracking outage (Routéo).** Meta-reported conversions collapse 2026-09-15 → 09-19 (CAPI outage).
   Clicks and backend Paid Social transactions are unaffected, so it's a tracking issue, not demand.
3. **SmartFeeds (Seconde Vie).** Feed optimisation went live 2026-03-02. Since then, optimised products' CTR is +25% vs
   non-optimised (0.96% vs 0.77%), just in time for Black Friday.
4. **SmartConversion / CRM (AutoNova).** Offline conversion import started 2025-03-10. The Google lead qualification rate rises from 36% to 50%,
   and cost per sold car falls from ≈€700 to ≈€500. Meta CAPI followed on 2025-06-02. The last ~6 weeks still have open leads.
5. **PMax migration.** All Standard Shopping campaigns were removed on 2025-03-31 and budget moved to Performance Max.
   TikTok launched for Seconde Vie in Sep 2024.
6. **GEO / AI search.** The *AI Assistants* channel grows from ~0.1% to ~3.5% of non-paid sessions and converts 1.7× organic.
7. **Platform vs backend.** Platform-reported revenue exceeds de-duplicated backend paid revenue (brand search ×1.1, PMax ×1.4,
   Meta ×1.6–1.9, video ×3+). Paid channels are ~45% of backend revenue.
8. **Incrementality.** Meta retargeting iROAS 0.7, Routéo ES brand search 0.4, AutoNova DV360 not significant, PMax DE 3.1.
   The GB generic-search test is still running.
9. **Seasonality.** French calendar: soldes (Jan/Jun), Mother's Day, rentrée, Black Friday / Cyber Monday, Christmas,
   Easter for rentals, Mondial de l'Auto for AutoNova, Prime Day for Amazon.
10. **Today's pain (data_requests).** Each request takes ≈6 days to deliver (new data source ≈22 days), slower in Q4. Top accounts send
    ~6 requests a month. Compare this with self-service + AI in GoodData.

## Suggested demo flow (from the intro call, 12 Nov 2026)

* **Today vs GoodData.** Data request → consultant writes SQL → Looker Studio → days. In GoodData, the client or consultant asks the AI and the answer comes in minutes.
* **One template, many clients.** The parent workspace has the standard dashboards (Overview, Search, Social & creatives,
  Shopping & feed, Budget pacing, Web & GEO). Child workspaces per client are white-labelled (themes), and WDF filters each one to its own data.
* **Semantic layer per client.** Shared metrics in the parent. A client-specific "Sales" definition lives in the child workspace (e.g. AutoNova
  *Cost per sold car* from CRM), and AI memory holds the client's KPI definitions.
* **Top account add-on.** CRM & Offline Sales is in the shared model, and OLP turns it on for AutoNova and Seconde Vie only. Federation (BigQuery + CRM + spreadsheet)
  answers Theo's "next they'll want CRM / first-party data".
* **Reporting automation.** Scheduled exports / slides replace the Google Slides automation built on BigQuery agents.
