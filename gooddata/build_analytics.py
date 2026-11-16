#!/usr/bin/env python3
"""
Build the Arcane GoodData parent workspace as code (gd CLI / analytics-as-code YAML).

    python3 build_analytics.py      -> ../analytics/{datasets,metrics,visualisations,dashboards}/*.yaml
                                       + data_products.json (objects per data product, for apply_permissions.py)

One shared model for every client, split into data products (see ../demo_data/data_products.json):
  * a dataset references only Shared Dimensions or datasets of its own data product (single join path)
  * every metric / visualisation / dashboard belongs to one data product (tag) and may use
    Shared Dimensions, its own product and Core ("Paid Media Performance") - Core is visible to everybody
  * one shared date dimension `activity_date` ("Date") is the main date of every fact, so one dashboard
    date filter works everywhere
  * every tenant table carries the workspace data filter `client_id` on column wdf__client_id
"""
import json
import os
import re
import shutil

import yaml

from descriptions import DATE_DESC, DESC, METRIC_DESC, VIS_DESC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "analytics")
DP = json.load(open(os.path.join(ROOT, "demo_data", "data_products.json")))
WDF = [{"filter_id": "client_id", "source_column": "wdf__client_id", "data_type": "STRING"}]
DATE = "activity_date"
SHARED = "Shared Dimensions"
CORE = "Paid Media Performance"
GRAN = ["DAY", "DAY_OF_WEEK", "DAY_OF_MONTH", "DAY_OF_YEAR", "WEEK", "WEEK_OF_YEAR", "MONTH", "MONTH_OF_YEAR",
        "QUARTER", "QUARTER_OF_YEAR", "YEAR"]
DATES = {
    DATE: ("Date", "Main date of every dataset: performance day, week start (products), lead date (CRM), budget "
                   "month, test start date, request submitted date."),
    "won_date": ("Won Date", "Date a CRM lead was won (car sold / B2B deal signed); 1900-01-01 = not won."),
}
S, I, N, D = "STRING", "INT", "NUMERIC", "DATE"


def _schema():
    src = open(os.path.join(ROOT, "demo_data", "generate.py")).read()
    head = src.split("# ---------------------------------------------------------------------------\n# Reference data")[0]
    ns = {"__file__": os.path.join(ROOT, "demo_data", "generate.py"), "__name__": "schema"}
    exec(compile(head, "generate.py", "exec"), ns)
    return {t: dict(cols) for t, cols in ns["SCHEMA"].items()}


PHYS = _schema()


def gd_type(table, col):
    t = PHYS[table][col].upper()
    return S if t.startswith("VARCHAR") else I if (t.startswith("INT") or t.startswith("BIGINT")) else \
        N if t.startswith("NUMERIC") else D


# ---------------------------------------------------------------------------
# Logical data model
# ---------------------------------------------------------------------------
MODEL = {
    "platforms": dict(
        title="Platforms", desc="Advertising platforms Arcane buys on (global reference, shared by all clients).",
        pk=("platform_id", "Platform"), labels=[("platform_name", "Platform Name", "TEXT")],
        attrs=[("platform_vendor", "Platform Vendor"), ("platform_category", "Platform Category"),
               ("arcane_practice", "Arcane Practice"), ("adverity_connector", "Adverity Connector"),
               ("is_paid", "Is Paid Platform")], wdf=False),
    "markets": dict(
        title="Markets", desc="Countries / markets the campaigns run in (global reference).",
        pk=("market_id", "Market"), labels=[("country_name", "Country", "TEXT")],
        attrs=[("market_region", "Market Region"), ("currency_code", "Currency"), ("language", "Language"),
               ("capital_city", "Capital City")], facts=[("eur_fx_rate", "EUR FX Rate")], wdf=False),
    "clients": dict(
        title="Clients", desc="Arcane's advertisers (tenants). Each client workspace sees only its own client. "
                              "Holds the client's own KPI definition and target.",
        pk=("client_id", "Client"), labels=[("client_name", "Client Name", "TEXT")],
        attrs=[("industry", "Industry"), ("business_model", "Business Model"), ("client_tier", "Client Tier"),
               ("data_schema", "Data Schema"), ("data_extensions", "Data Extensions"), ("primary_kpi", "Primary KPI"),
               ("primary_kpi_definition", "Primary KPI Definition"), ("target_type", "Target Type"),
               ("headquarters_city", "HQ City"), ("media_consultant", "Media Consultant"),
               ("data_consultant", "Data Consultant")],
        facts=[("target_value", "Target Value"), ("monthly_budget_eur", "Monthly Budget (EUR)")]),
    "campaigns": dict(
        title="Campaigns", desc="Campaigns across all platforms (Arcane naming convention CLIENT_MARKET_PLATFORM_TYPE_LINE). "
                                "Non-paid 'campaigns' hold organic / direct CRM leads.",
        pk=("campaign_id", "Campaign"), labels=[("campaign_name", "Campaign Name", "TEXT")],
        attrs=[("campaign_type", "Campaign Type"), ("channel_group", "Channel Group"), ("funnel_stage", "Funnel Stage"),
               ("objective", "Objective"), ("is_brand", "Is Brand Campaign"), ("product_line", "Product Line"),
               ("bidding_strategy", "Bidding Strategy"), ("campaign_status", "Campaign Status")],
        refs=["clients", "platforms", "markets"]),
    "ad_performance_daily": dict(
        title="Ad Performance", desc="Daily campaign performance by device from the ad platforms (via Adverity): cost, "
                                     "clicks, platform-reported conversions and value, search impression share.",
        pk=("performance_id", "Ad Performance Row"), attrs=[("device", "Device")],
        facts=[("impressions", "Impressions"), ("clicks", "Clicks"), ("cost_eur", "Cost (EUR)"),
               ("cost_local_currency", "Cost (Local Currency)"), ("conversions", "Platform Conversions"),
               ("conversion_value_eur", "Platform Conversion Value (EUR)"), ("video_views", "Video Views"),
               ("engagements", "Engagements"), ("search_impressions", "Search Impressions"),
               ("search_eligible_impressions", "Search Eligible Impressions"),
               ("search_lost_is_budget", "Search Impressions Lost (Budget)"),
               ("search_lost_is_rank", "Search Impressions Lost (Rank)")],
        refs=["campaigns"], date="date"),
    "creatives": dict(
        title="Creatives", desc="Social ad creatives (Meta, TikTok, LinkedIn): format, theme, production source.",
        pk=("creative_id", "Creative"), labels=[("creative_name", "Creative Name", "TEXT")],
        attrs=[("creative_format", "Creative Format"), ("creative_theme", "Creative Theme"),
               ("production_source", "Production Source"), ("is_video", "Is Video"), ("creative_status", "Creative Status")],
        refs=["campaigns"]),
    "creative_performance_daily": dict(
        title="Creative Performance", desc="Daily performance per social creative (sums to the social campaigns).",
        pk=("creative_performance_id", "Creative Performance Row"),
        facts=[("impressions", "Creative Impressions"), ("clicks", "Creative Clicks"), ("cost_eur", "Creative Spend (EUR)"),
               ("video_3s_views", "3-second Video Views"), ("thruplays", "ThruPlays"),
               ("engagements", "Creative Engagements"), ("conversions", "Creative Conversions"),
               ("conversion_value_eur", "Creative Conversion Value (EUR)")],
        refs=["creatives"], date="date"),
    "products": dict(
        title="Products", desc="Product feed items (Shopping / PMax / Amazon). Feed Optimized = SmartFeeds.",
        pk=("product_id", "Product"), labels=[("product_title", "Product Title", "TEXT")],
        attrs=[("sku", "SKU"), ("product_brand", "Product Brand"), ("product_category", "Product Category"),
               ("product_subcategory", "Product Subcategory"), ("product_condition", "Product Condition"),
               ("feed_optimized", "Feed Optimized (SmartFeeds)")],
        facts=[("price_eur", "Price (EUR)"), ("margin_pct", "Product Margin %")]),
    "product_performance_weekly": dict(
        title="Product Performance", desc="Weekly performance per product and shopping campaign.",
        pk=("product_performance_id", "Product Performance Row"),
        facts=[("impressions", "Product Impressions"), ("clicks", "Product Clicks"), ("cost_eur", "Product Cost (EUR)"),
               ("conversions", "Product Conversions"), ("conversion_value_eur", "Product Conversion Value (EUR)")],
        refs=["products", "campaigns"], date="week_start_date"),
    "web_analytics_daily": dict(
        title="Web Analytics", desc="GA4 + backend orders per client, market, day and channel group. Paid channels are "
                                    "de-duplicated (backend truth); includes the AI Assistants channel (GEO).",
        pk=("web_id", "Web Analytics Row"),
        attrs=[("channel_group", "Web Channel Group"), ("is_paid_channel", "Is Paid Channel")],
        facts=[("sessions", "Sessions"), ("engaged_sessions", "Engaged Sessions"), ("new_users", "New Users"),
               ("transactions", "Backend Transactions"), ("revenue_eur", "Backend Revenue (EUR)"),
               ("gross_margin_eur", "Gross Margin (EUR)"), ("new_customers", "New Customers"), ("leads", "Web Leads")],
        refs=["clients", "markets"], date="date"),
    "business_locations": dict(
        title="Business Locations", desc="Dealerships (AutoNova) and B2B sales offices (Seconde Vie Pro) handling CRM leads.",
        pk=("location_id", "Business Location"),
        labels=[("location_name", "Location Name", "TEXT"), ("latitude", "Latitude", "GEO_LATITUDE"),
                ("longitude", "Longitude", "GEO_LONGITUDE")],
        attrs=[("location_type", "Location Type"), ("city", "Location City"), ("region", "Location Region"),
               ("country", "Location Country")]),
    "crm_leads": dict(
        title="CRM Leads", desc="CRM leads with the funnel lead -> contacted -> qualified -> opportunity (test drive / "
                                "quote) -> won (car sold / deal signed), deal value and offline conversion upload.",
        pk=("lead_id", "Lead"),
        attrs=[("lead_type", "Lead Type"), ("product_brand", "Lead Product Brand"), ("product_name", "Lead Product"),
               ("product_line", "Lead Product Line"), ("product_segment", "Lead Segment"),
               ("product_variant", "Lead Variant"), ("is_existing_customer", "Existing Customer"),
               ("lead_status", "Lead Status"), ("opportunity_type", "Opportunity Type"),
               ("offline_conversion_uploaded", "Offline Conversion Uploaded")],
        facts=[("hours_to_first_contact", "Hours to First Contact"), ("days_to_close", "Days to Close"),
               ("deal_value_eur", "Deal Value (EUR)"), ("gross_profit_eur", "Deal Gross Profit (EUR)"),
               ("is_qualified", "Is Qualified"), ("is_opportunity", "Is Opportunity"), ("is_won", "Is Won")],
        refs=["campaigns", "business_locations"], date="lead_date", dates=[("won_date", "won_date")]),
    "media_budgets": dict(
        title="Media Budgets", desc="Monthly media plan per client, platform and market with ROAS / CPA targets.",
        pk=("budget_id", "Budget Line"), attrs=[("budget_owner", "Budget Owner")],
        facts=[("planned_budget_eur", "Planned Budget (EUR)"), ("target_roas", "Target ROAS"),
               ("target_cpa_eur", "Target CPA (EUR)")],
        refs=["clients", "platforms", "markets"], date="budget_month"),
    "incrementality_tests": dict(
        title="Incrementality Tests", desc="Geo-lift and conversion-lift tests run by Arcane's Data & Measurement team.",
        pk=("test_id", "Incrementality Test"), labels=[("test_name", "Test Name", "TEXT")],
        attrs=[("campaign_scope", "Test Campaign Scope"), ("methodology", "Test Methodology"),
               ("test_status", "Test Status"), ("is_significant", "Is Significant"), ("recommendation", "Recommendation")],
        facts=[("test_spend_eur", "Test Spend (EUR)"), ("platform_conversions", "Test Platform Conversions"),
               ("incremental_conversions", "Incremental Conversions"),
               ("incremental_revenue_eur", "Incremental Revenue (EUR)"), ("lift_pct", "Lift %"), ("iroas", "iROAS"),
               ("confidence_level", "Confidence Level")],
        refs=["clients", "platforms", "markets"], date="start_date"),
    "data_requests": dict(
        title="Data Requests", desc="Arcane's current data-support loop (Google Form -> project tool -> data consultant).",
        pk=("request_id", "Data Request"), labels=[("request_summary", "Request Summary", "TEXT")],
        attrs=[("requested_by_role", "Requested By"), ("request_channel", "Request Channel"),
               ("request_type", "Request Type"), ("priority", "Request Priority"), ("assigned_to", "Assigned To"),
               ("request_status", "Request Status")],
        facts=[("days_to_deliver", "Days to Deliver"), ("effort_hours", "Effort Hours"), ("is_delivered", "Is Delivered")],
        refs=["clients"], date="submitted_date"),
    "client_data_products": dict(
        title="Client Data Products", desc="Entitlements: which data products each client has (drives permissions).",
        pk=("entitlement_id", "Entitlement"),
        attrs=[("data_product", "Data Product"), ("package", "Package"), ("audience", "Audience"),
               ("is_enabled", "Is Enabled"), ("user_group", "User Group")],
        refs=["clients"]),
}
assert {t: m.get("refs", []) for t, m in MODEL.items()} == DP["references"], "LDM refs differ from demo_data"
DATASET_PRODUCT = {t: n for n, x in DP["data_products"].items() for t in x["datasets"]}


def product_of_dataset(ds):
    return DATASET_PRODUCT.get(ds, SHARED)


def desc(field_id):
    if field_id not in DESC:
        raise SystemExit(f"no description for {field_id} in descriptions.py")
    return DESC[field_id]


def build_datasets():
    out = {}
    for t, m in MODEL.items():
        tags = [product_of_dataset(t)]
        pk_col, pk_title = m["pk"]
        pk_id = f"{t}.{pk_col}"
        pk = {"type": "attribute", "source_column": pk_col, "data_type": S, "title": pk_title,
              "description": desc(pk_id), "tags": tags}
        if m.get("labels"):
            pk["labels"] = {f"{pk_id}.{c}": {"source_column": c, "data_type": gd_type(t, c), "title": title,
                                             "description": desc(f"{pk_id}.{c}"), "tags": tags, "value_type": vt}
                            for c, title, vt in m["labels"]}
        fields = {pk_id: pk}
        for c, title in m.get("attrs", []):
            fields[f"{t}.{c}"] = {"type": "attribute", "source_column": c, "data_type": gd_type(t, c), "title": title,
                                  "description": desc(f"{t}.{c}"), "tags": tags}
        for c, title in m.get("facts", []):
            fields[f"{t}.{c}"] = {"type": "fact", "source_column": c, "data_type": gd_type(t, c), "title": title,
                                  "description": desc(f"{t}.{c}"), "tags": tags}
        refs = [{"dataset": r, "sources": [{"source_column": MODEL[r]["pk"][0], "data_type": S,
                                            "target": f"{r}.{MODEL[r]['pk'][0]}"}]} for r in m.get("refs", [])]
        if m.get("date"):
            refs.append({"dataset": DATE, "sources": [{"source_column": m["date"], "data_type": D, "target": DATE}]})
        refs += [{"dataset": ds, "sources": [{"source_column": c, "data_type": D, "target": ds}]}
                 for ds, c in m.get("dates", [])]
        doc = {"type": "dataset", "id": t, "table_path": f"main/{t}", "title": m["title"], "description": m["desc"],
               "tags": tags, "primary_key": pk_id, "fields": fields}
        if refs:
            doc["references"] = refs
        if m.get("wdf", True):
            doc["workspace_data_filters"] = WDF
        out[t] = doc
    for d, (title, _) in DATES.items():
        out[d] = {"type": "date", "id": d, "title": title, "description": DATE_DESC[d], "tags": [SHARED],
                  "granularities": GRAN, "title_base": "", "title_pattern": "%titleBase - %granularityTitle"}
    return out


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
PCT, NUM, NUM1, NUM2, EUR, EUR2 = "#,##0.0%", "#,##0", "#,##0.0", "#,##0.00", "€#,##0", "€#,##0.00"
X = "#,##0.00x"
METRICS = []


def metric(mid, title, maql, fmt, desc, tag):
    maql = re.sub(r"(^|[\s/*+-])\((COUNT|SUM|AVG)\(", r"\1(SELECT \2(", maql)
    METRICS.append((mid, title, maql, fmt, desc, tag))


def F(x):
    return "{fact/" + x + "}"


def M(x):
    return "{metric/" + x + "}"


def L(x):
    return "{label/" + x + "}"


def A(x):
    return "{attribute/" + x + "}"


def SUM(x):
    return f"SELECT SUM({F(x)})"


def build_metrics():
    t = CORE
    a = "ad_performance_daily"
    for mid, title, col, fmt, desc in [
            ("pm_cost", "Cost", "cost_eur", EUR, "Media spend in EUR across all platforms."),
            ("pm_impressions", "Impressions", "impressions", NUM, "Ad impressions."),
            ("pm_clicks", "Clicks", "clicks", NUM, "Ad clicks."),
            ("pm_conversions", "Platform Conversions", "conversions", NUM1,
             "Conversions as reported by the ad platforms (purchases, bookings or leads depending on the client)."),
            ("pm_conv_value", "Platform Conversion Value", "conversion_value_eur", EUR,
             "Conversion value reported by the ad platforms in EUR."),
            ("pm_video_views", "Video Views", "video_views", NUM, "Video views (YouTube, DV360, Demand Gen)."),
            ("pm_search_impr", "Search Impressions", "search_impressions", NUM, "Impressions of search & shopping campaigns."),
            ("pm_search_eligible", "Search Eligible Impressions", "search_eligible_impressions", NUM,
             "Impressions the search campaigns were eligible for."),
            ("pm_search_lost_budget", "Search Impressions Lost to Budget", "search_lost_is_budget", NUM,
             "Eligible impressions lost because the budget was capped."),
            ("pm_search_lost_rank", "Search Impressions Lost to Rank", "search_lost_is_rank", NUM,
             "Eligible impressions lost because of ad rank (bids / quality).")]:
        metric(mid, title, SUM(f"{a}.{col}"), fmt, desc, t)
    metric("pm_ctr", "CTR", f"SELECT {M('pm_clicks')} / {M('pm_impressions')}", "#,##0.00%", "Click-through rate.", t)
    metric("pm_cpc", "CPC", f"SELECT {M('pm_cost')} / {M('pm_clicks')}", EUR2, "Cost per click.", t)
    metric("pm_cpm", "CPM", f"SELECT {M('pm_cost')} / {M('pm_impressions')} * 1000", EUR2, "Cost per 1,000 impressions.", t)
    metric("pm_cvr", "Conversion Rate", f"SELECT {M('pm_conversions')} / {M('pm_clicks')}", "#,##0.00%",
           "Platform conversions per click.", t)
    metric("pm_cpa", "CPA", f"SELECT {M('pm_cost')} / {M('pm_conversions')}", EUR2,
           "Cost per platform conversion (cost per order / booking / lead).", t)
    metric("pm_roas", "ROAS", f"SELECT {M('pm_conv_value')} / {M('pm_cost')}", X,
           "Return on ad spend = platform conversion value / cost.", t)
    metric("pm_search_is", "Search Impression Share", f"SELECT {M('pm_search_impr')} / {M('pm_search_eligible')}", PCT,
           "Share of eligible search impressions actually received.", t)
    metric("pm_lost_is_budget", "Lost IS (Budget)", f"SELECT {M('pm_search_lost_budget')} / {M('pm_search_eligible')}",
           PCT, "Share of eligible search impressions lost because of budget caps.", t)
    metric("pm_lost_is_rank", "Lost IS (Rank)", f"SELECT {M('pm_search_lost_rank')} / {M('pm_search_eligible')}", PCT,
           "Share of eligible search impressions lost because of ad rank.", t)
    metric("pm_active_campaigns", "Active Campaigns",
           f"SELECT COUNT({A('campaigns.campaign_id')}, {A(a + '.performance_id')})", NUM,
           "Campaigns with spend or impressions in the period.", t)

    t = "Social Creatives"
    c = "creative_performance_daily"
    for mid, title, col, fmt, desc in [
            ("sc_spend", "Social Spend", "cost_eur", EUR, "Spend on social creatives."),
            ("sc_impressions", "Social Impressions", "impressions", NUM, "Impressions of social creatives."),
            ("sc_clicks", "Social Clicks", "clicks", NUM, "Clicks on social creatives."),
            ("sc_conversions", "Social Conversions", "conversions", NUM1, "Platform conversions attributed to creatives."),
            ("sc_conv_value", "Social Conversion Value", "conversion_value_eur", EUR, "Conversion value of creatives."),
            ("sc_vv3", "3-second Video Views", "video_3s_views", NUM, "Video views of at least 3 seconds."),
            ("sc_thruplays", "ThruPlays", "thruplays", NUM, "Video views to 15 s or completion.")]:
        metric(mid, title, SUM(f"{c}.{col}"), fmt, desc, t)
    metric("sc_ctr", "Social CTR", f"SELECT {M('sc_clicks')} / {M('sc_impressions')}", "#,##0.00%",
           "Click-through rate of social creatives.", t)
    metric("sc_cpa", "Social CPA", f"SELECT {M('sc_spend')} / {M('sc_conversions')}", EUR2, "Cost per conversion.", t)
    metric("sc_roas", "Social ROAS", f"SELECT {M('sc_conv_value')} / {M('sc_spend')}", X, "Conversion value / spend.", t)
    metric("sc_thumbstop", "Thumb-stop Rate", f"SELECT {M('sc_vv3')} / {M('sc_impressions')}", PCT,
           "3-second video views per impression (hook strength).", t)
    metric("sc_hold", "Hold Rate", f"SELECT {M('sc_thruplays')} / {M('sc_vv3')}", PCT,
           "ThruPlays per 3-second view (how well the video keeps attention).", t)
    metric("sc_creatives", "Creatives Live",
           f"SELECT COUNT({A('creatives.creative_id')}, {A(c + '.creative_performance_id')})", NUM,
           "Creatives that delivered impressions in the period.", t)

    t = "Web Analytics & GEO"
    w = "web_analytics_daily"
    paid = f'{L(w + ".is_paid_channel")} = "Yes"'
    ai = f'{L(w + ".channel_group")} = "AI Assistants (ChatGPT, Perplexity, Gemini)"'
    for mid, title, col, fmt, desc in [
            ("wa_sessions", "Sessions", "sessions", NUM, "Website sessions (GA4)."),
            ("wa_transactions", "Backend Transactions", "transactions", NUM,
             "Orders / bookings recorded in the client's backend (de-duplicated, all channels)."),
            ("wa_revenue", "Backend Revenue", "revenue_eur", EUR, "Revenue recorded in the client's backend."),
            ("wa_margin", "Gross Margin", "gross_margin_eur", EUR, "Gross margin of backend revenue."),
            ("wa_new_customers", "New Customers", "new_customers", NUM, "First-time customers."),
            ("wa_leads", "Web Leads", "leads", NUM, "Lead form submissions on the website.")]:
        metric(mid, title, SUM(f"{w}.{col}"), fmt, desc, t)
    metric("wa_cvr", "Site Conversion Rate", f"SELECT {M('wa_transactions')} / {M('wa_sessions')}", "#,##0.00%",
           "Backend transactions per session.", t)
    metric("wa_aov", "Average Order Value", f"SELECT {M('wa_revenue')} / {M('wa_transactions')}", EUR2,
           "Backend revenue per transaction.", t)
    metric("wa_paid_revenue", "Paid Media Revenue (Backend)", f"SELECT {M('wa_revenue')} WHERE {paid}", EUR,
           "Backend revenue from paid channels (de-duplicated).", t)
    metric("wa_paid_transactions", "Paid Media Transactions (Backend)", f"SELECT {M('wa_transactions')} WHERE {paid}",
           NUM, "Backend transactions from paid channels (de-duplicated).", t)
    metric("wa_paid_share", "Paid Share of Revenue", f"SELECT {M('wa_paid_revenue')} / {M('wa_revenue')}", PCT,
           "Share of backend revenue coming from paid media.", t)
    metric("wa_mer", "Blended ROAS (MER)", f"SELECT {M('wa_revenue')} / {M('pm_cost')}", X,
           "Marketing efficiency ratio: total backend revenue / total media cost.", t)
    metric("wa_paid_roas", "Backend ROAS", f"SELECT {M('wa_paid_revenue')} / {M('pm_cost')}", X,
           "Paid backend revenue / media cost - the de-duplicated alternative to platform ROAS.", t)
    metric("wa_overattribution", "Platform Over-attribution",
           f"SELECT {M('pm_conv_value')} / {M('wa_paid_revenue')}", X,
           "Platform-reported conversion value / backend paid revenue (1.0x = platforms agree with the backend).", t)
    metric("wa_ai_sessions", "AI Assistant Sessions", f"SELECT {M('wa_sessions')} WHERE {ai}", NUM,
           "Sessions referred by AI assistants (ChatGPT, Perplexity, Gemini) - GEO.", t)
    metric("wa_ai_share", "AI Assistant Share of Sessions", f"SELECT {M('wa_ai_sessions')} / {M('wa_sessions')}",
           "#,##0.00%", "Share of all sessions coming from AI assistants.", t)

    t = "Budget & Pacing"
    b = "media_budgets"
    metric("bp_planned", "Planned Budget", SUM(f"{b}.planned_budget_eur"), EUR, "Media plan budget.", t)
    metric("bp_pacing", "Budget Pacing", f"SELECT {M('pm_cost')} / {M('bp_planned')}", PCT,
           "Actual cost / planned budget (100% = on plan).", t)
    metric("bp_variance", "Budget Variance", f"SELECT {M('pm_cost')} - {M('bp_planned')}", EUR,
           "Actual cost minus planned budget (negative = under-spending).", t)
    metric("bp_remaining", "Remaining Budget", f"SELECT {M('bp_planned')} - {M('pm_cost')}", EUR,
           "Planned budget not spent yet.", t)
    metric("bp_target_roas", "Target ROAS", f"SELECT AVG({F(b + '.target_roas')})", X, "ROAS target from the media plan.", t)
    metric("bp_target_cpa", "Target CPA", f"SELECT AVG({F(b + '.target_cpa_eur')})", EUR2, "CPA target from the media plan.", t)

    t = "Product Feed & Shopping"
    p = "product_performance_weekly"
    for mid, title, col, fmt, desc in [
            ("pf_impressions", "Product Impressions", "impressions", NUM, "Impressions of product ads."),
            ("pf_clicks", "Product Clicks", "clicks", NUM, "Clicks on product ads."),
            ("pf_cost", "Product Cost", "cost_eur", EUR, "Spend on product ads."),
            ("pf_conversions", "Product Conversions", "conversions", NUM1, "Conversions of product ads."),
            ("pf_value", "Product Conversion Value", "conversion_value_eur", EUR, "Conversion value of product ads.")]:
        metric(mid, title, SUM(f"{p}.{col}"), fmt, desc, t)
    metric("pf_ctr", "Product CTR", f"SELECT {M('pf_clicks')} / {M('pf_impressions')}", "#,##0.00%",
           "Click-through rate of product ads.", t)
    metric("pf_roas", "Product ROAS", f"SELECT {M('pf_value')} / {M('pf_cost')}", X, "Product conversion value / cost.", t)
    metric("pf_products", "Products Advertised",
           f"SELECT COUNT({A('products.product_id')}, {A(p + '.product_performance_id')})",
           NUM, "Products that had product-ad impressions in the period.", t)

    t = "CRM & Offline Sales"
    l = "crm_leads"
    metric("crm_leads", "Leads", f"SELECT COUNT({A(l + '.lead_id')})", NUM, "CRM leads created.", t)
    metric("crm_qualified", "Qualified Leads", SUM(f"{l}.is_qualified"), NUM, "Leads qualified by sales.", t)
    metric("crm_opportunities", "Opportunities", SUM(f"{l}.is_opportunity"), NUM,
           "Leads that reached an opportunity (test drive done / quote sent).", t)
    metric("crm_won", "Won Deals", SUM(f"{l}.is_won"), NUM, "Leads won (car sold / B2B deal signed).", t)
    metric("crm_deal_value", "Deal Value", SUM(f"{l}.deal_value_eur"), EUR, "Value of won deals.", t)
    metric("crm_gross_profit", "Deal Gross Profit", SUM(f"{l}.gross_profit_eur"), EUR, "Gross profit of won deals.", t)
    metric("crm_qual_rate", "Qualification Rate", f"SELECT {M('crm_qualified')} / {M('crm_leads')}", PCT,
           "Qualified leads / leads.", t)
    metric("crm_win_rate", "Win Rate", f"SELECT {M('crm_won')} / {M('crm_qualified')}", PCT, "Won deals / qualified leads.", t)
    metric("crm_contact_hours", "Avg Hours to First Contact", f"SELECT AVG({F(l + '.hours_to_first_contact')}) WHERE "
           f"{L(l + '.lead_status')} <> \"New\"", NUM1, "Average hours until sales first contacted the lead.", t)
    metric("crm_days_to_close", "Avg Days to Close", f"SELECT AVG({F(l + '.days_to_close')}) WHERE {F(l + '.is_won')} = 1",
           NUM1, "Average days from lead to won deal.", t)
    metric("crm_lead_cost", "Lead-gen Media Cost",
           f'SELECT {M("pm_cost")} WHERE {L("campaigns.objective")} = "Leads"', EUR,
           "Media cost of campaigns whose objective is Leads.", t)
    metric("crm_cpl", "Cost per Lead", f"SELECT {M('crm_lead_cost')} / (SELECT {M('crm_leads')} WHERE "
           f"{L('campaigns.objective')} = \"Leads\")", EUR2, "Lead-gen media cost / paid leads.", t)
    metric("crm_cpql", "Cost per Qualified Lead", f"SELECT {M('crm_lead_cost')} / (SELECT {M('crm_qualified')} WHERE "
           f"{L('campaigns.objective')} = \"Leads\")", EUR2, "Lead-gen media cost / qualified paid leads.", t)
    metric("crm_cost_per_won", "Cost per Won Deal", f"SELECT {M('crm_lead_cost')} / (SELECT {M('crm_won')} WHERE "
           f"{L('campaigns.objective')} = \"Leads\")", EUR, "Lead-gen media cost / won deals from paid leads "
           "(cost per car sold / per B2B deal).", t)
    metric("crm_oci_share", "Offline Conversions Uploaded",
           f'SELECT {M("crm_won")} WHERE {L(l + ".offline_conversion_uploaded")} = "Yes"', NUM,
           "Won deals sent back to the ad platforms as offline conversions (SmartConversion).", t)

    t = "Measurement & Incrementality"
    i = "incrementality_tests"
    metric("mi_tests", "Incrementality Tests", f"SELECT COUNT({A(i + '.test_id')})", NUM, "Tests run.", t)
    metric("mi_spend", "Test Spend", SUM(f"{i}.test_spend_eur"), EUR, "Media spend in the test cells.", t)
    metric("mi_inc_revenue", "Incremental Revenue", SUM(f"{i}.incremental_revenue_eur"), EUR,
           "Revenue that would not have happened without the media.", t)
    metric("mi_iroas", "iROAS", f"SELECT {M('mi_inc_revenue')} / {M('mi_spend')}", X,
           "Incremental ROAS = incremental revenue / test spend.", t)
    metric("mi_inc_share", "Incremental Share of Platform Conversions",
           f"SELECT SUM({F(i + '.incremental_conversions')}) / SUM({F(i + '.platform_conversions')})", PCT,
           "Share of platform-reported conversions that were truly incremental.", t)

    t = "Arcane Operations"
    r = "data_requests"
    metric("op_requests", "Data Requests", f"SELECT COUNT({A(r + '.request_id')})", NUM, "Requests submitted.", t)
    metric("op_delivered", "Delivered Requests", SUM(f"{r}.is_delivered"), NUM, "Requests delivered.", t)
    metric("op_days", "Avg Days to Deliver", f"SELECT AVG({F(r + '.days_to_deliver')}) WHERE {F(r + '.is_delivered')} = 1",
           NUM1, "Average days from request to delivery.", t)
    metric("op_effort", "Effort Hours", SUM(f"{r}.effort_hours"), NUM1, "Consultant hours spent on requests.", t)
    metric("op_open", "Open Requests", f'SELECT {M("op_requests")} WHERE {L(r + ".request_status")} IN '
           f'("In Progress", "Backlog")', NUM, "Requests in progress or in the backlog.", t)
    metric("op_entitled", "Enabled Data Products",
           f'SELECT COUNT({A("client_data_products.entitlement_id")}) WHERE '
           f'{L("client_data_products.is_enabled")} = "Yes"', NUM, "Data products enabled for the client.", t)


# ---------------------------------------------------------------------------
# Visualisations & dashboards
# ---------------------------------------------------------------------------
VIS = {}
DASHBOARDS = []
MONTH = f"label/{DATE}.month"
WEEK = f"label/{DATE}.week"
CLIENT = "label/clients.client_id.client_name"
PLATFORM = "label/platforms.platform_id.platform_name"
MARKET = "label/markets.market_id.country_name"
BOTTOM = {"legend_position": "bottom"}


def fid(ref):
    return ref.split("/", 1)[1].replace(".", "_")


def headline(vid, title, m, desc, compare=True):
    q = {"fields": {"primary": f"metric/{m}"}}
    v = {"type": "headline_chart", "id": vid, "title": title, "description": desc, "query": q}
    if compare:
        q["fields"]["secondary"] = {"title": "Previous period", "type": "PREVIOUS_PERIOD", "date_filter": DATE,
                                    "using": "primary"}
        q["filter_by"] = {f"{DATE}_year": {"type": "date_filter", "granularity": "YEAR", "from": 0, "to": 0,
                                           "using": DATE}}
        v["metrics"] = ["primary", "secondary"]
        v["config"] = {"comparison_type": "change", "indicator_arrow": True, "indicator_colors": True,
                       "label_default": "vs previous period", "label_conditional": True}
    else:
        v["metrics"] = ["primary"]
    VIS[vid] = v


def chart(vid, typ, title, desc, metrics, view=None, segment=None, sort=True, filters=None, config=None,
          axes=None, totals=False):
    fields, mkeys = {}, []
    for m in metrics:
        fields[m] = f"metric/{m}"
        mkeys.append(m)
    v = {"type": typ, "id": vid, "title": title, "description": desc, "query": {"fields": fields}}
    vk, sk = [fid(x) for x in (view or [])], [fid(x) for x in (segment or [])]
    for ref in (view or []) + (segment or []):
        fields[fid(ref)] = ref
    if filters:
        v["query"]["filter_by"] = filters
    if sort and view and typ in ("bar_chart", "table", "column_chart") and not view[0].startswith(f"label/{DATE}"):
        v["query"]["sort_by"] = [{"type": "metric_sort", "direction": "DESC", "metrics": [mkeys[0]]}]
    v["metrics"] = [{"field": k, "axis": a} for k, a in zip(mkeys, axes)] if axes else mkeys
    if vk:
        v["view_by"] = ([{"field": vk[0], "totals": [{"title": "Total", "type": "SUM", "using": k} for k in mkeys
                                                     if totals is True or k in totals]}] + vk[1:]) if totals else vk
    if sk:
        v["segment_by"] = sk
    if config:
        v["config"] = config
    VIS[vid] = v


def incl(label, *values):
    return {fid(label) + "_f": {"type": "attribute_filter", "using": label, "state": {"include": list(values)}}}


def excl(label, *values):
    return {fid(label) + "_f": {"type": "attribute_filter", "using": label, "state": {"exclude": list(values)}}}


FILTERS = {
    "client": {"type": "attribute_filter", "title": "Client", "using": CLIENT},
    "market": {"type": "attribute_filter", "title": "Market", "using": MARKET},
    "platform": {"type": "attribute_filter", "title": "Platform", "using": PLATFORM},
}


def dashboard(did, product, title, desc, rows, filters=("client", "market", "platform"), months=(-11, 0)):
    sections = []
    for stitle, widgets in rows:
        ws = []
        for vid, cols, h, use_date in widgets:
            w = {"id": f"w_{vid}", "visualization": vid, "title": VIS[vid]["title"], "columns": cols, "rows": h}
            if VIS[vid].get("tags") and VIS[vid]["tags"] != [product]:
                raise SystemExit(f"{vid} is used by two data products")
            VIS[vid]["tags"] = [product]
            if use_date:
                w["date"] = DATE
            ws.append(w)
        s = {"widgets": ws}
        if stitle:
            s["title"] = stitle
        sections.append(s)
    f = {"date": {"type": "date_filter", "granularity": "MONTH", "from": months[0], "to": months[1]}}
    f.update({k: FILTERS[k] for k in filters})
    pkg = DP["data_products"][product]["package"]
    who = {"Core": "visible to every client and Arcane user", "Internal": "Arcane staff only"}.get(
        pkg, "visible to clients who have this data product")
    desc = f"{desc} Data product: {product} ({pkg}, {who})."
    DASHBOARDS.append({"type": "dashboard", "id": did, "title": title, "description": desc, "tags": [product],
                       "sections": sections, "filters": f})


def kpis(*items):
    return [(v, 2, 8, d) for v, d in items]


def build_visuals():
    # 1. Paid Media Performance (Core) -----------------------------------------
    for vid, title, m, desc in [("pm_k_cost", "Cost", "pm_cost", "Media spend."),
                                ("pm_k_conv", "Conversions", "pm_conversions", "Platform-reported conversions."),
                                ("pm_k_value", "Conversion Value", "pm_conv_value", "Platform conversion value."),
                                ("pm_k_roas", "ROAS", "pm_roas", "Platform ROAS."),
                                ("pm_k_cpa", "CPA", "pm_cpa", "Cost per conversion."),
                                ("pm_k_ctr", "CTR", "pm_ctr", "Click-through rate.")]:
        headline(vid, title, m, desc)
    chart("pm_trend", "combo_chart", "Cost & ROAS by Month", "Monthly cost (columns) and ROAS (line).",
          ["pm_cost", "pm_roas"], view=[MONTH], axes=["primary", "secondary"], config=BOTTOM)
    chart("pm_by_platform", "donut_chart", "Cost by Platform", "Share of spend per platform.", ["pm_cost"],
          view=[PLATFORM], config={"legend_position": "right"})
    chart("pm_by_type", "table", "Performance by Campaign Type", "Cost, conversions, CPA and ROAS per campaign type.",
          ["pm_cost", "pm_clicks", "pm_conversions", "pm_cpa", "pm_roas"], view=["label/campaigns.campaign_type"],
          totals=["pm_cost", "pm_clicks", "pm_conversions"])
    chart("pm_by_market", "bar_chart", "Cost & Conversions by Market", "Where the budget goes and what it returns.",
          ["pm_cost", "pm_conversions"], view=[MARKET], config=BOTTOM)
    chart("pm_by_funnel", "column_chart", "Cost by Funnel Stage by Month", "Awareness / consideration / conversion mix.",
          ["pm_cost"], view=[MONTH], segment=["label/campaigns.funnel_stage"], config={**BOTTOM, "stack_measures": True})
    chart("pm_device", "column_chart", "CPA by Device", "Cost per conversion per device.", ["pm_cpa", "pm_cvr"],
          view=["label/ad_performance_daily.device"], config=BOTTOM)
    chart("pm_is_trend", "line_chart", "Search Impression Share by Week",
          "Impression share and the share lost to budget / rank (search & shopping).",
          ["pm_search_is", "pm_lost_is_budget", "pm_lost_is_rank"], view=[WEEK], config=BOTTOM)
    chart("pm_is_market", "table", "Search Impression Share by Market",
          "Impression share and lost share per market - budget caps show up as Lost IS (Budget).",
          ["pm_cost", "pm_search_is", "pm_lost_is_budget", "pm_lost_is_rank", "pm_conversions"], view=[MARKET])
    chart("pm_top_campaigns", "table", "Top Campaigns", "Campaigns ranked by cost.",
          ["pm_cost", "pm_conversions", "pm_cpa", "pm_roas", "pm_ctr"],
          view=["label/campaigns.campaign_id.campaign_name", PLATFORM])
    dashboard("d1_paid_media", CORE, "1. Paid Media Performance",
              "Cross-platform media performance: spend, conversions, ROAS / CPA, markets, devices and search health.",
              [(None, kpis(("pm_k_cost", 1), ("pm_k_conv", 1), ("pm_k_value", 1), ("pm_k_roas", 1), ("pm_k_cpa", 1),
                           ("pm_k_ctr", 1))),
               ("Trend & Mix", [("pm_trend", 8, 16, 1), ("pm_by_platform", 4, 16, 1), ("pm_by_funnel", 6, 16, 1),
                                ("pm_by_market", 6, 16, 1)]),
               ("Campaigns", [("pm_by_type", 7, 16, 1), ("pm_device", 5, 16, 1), ("pm_top_campaigns", 12, 18, 1)]),
               ("Search Health", [("pm_is_trend", 7, 16, 1), ("pm_is_market", 5, 16, 1)])])

    # 2. Social Creatives -------------------------------------------------------
    for vid, title, m, desc in [("sc_k_spend", "Social Spend", "sc_spend", "Spend on social creatives."),
                                ("sc_k_ctr", "Social CTR", "sc_ctr", "Click-through rate."),
                                ("sc_k_cpa", "Social CPA", "sc_cpa", "Cost per conversion."),
                                ("sc_k_thumb", "Thumb-stop Rate", "sc_thumbstop", "3-second views per impression."),
                                ("sc_k_hold", "Hold Rate", "sc_hold", "ThruPlays per 3-second view."),
                                ("sc_k_live", "Creatives Live", "sc_creatives", "Creatives that delivered.")]:
        headline(vid, title, m, desc)
    chart("sc_by_format", "bar_chart", "CTR & CPA by Creative Format", "Which formats win (UGC, Reels, carousel ...).",
          ["sc_ctr", "sc_cpa"], view=["label/creatives.creative_format"], config=BOTTOM)
    chart("sc_by_source", "column_chart", "CPA by Production Source", "In-house vs UGC creators vs AI-generated (Arcane AI Lab).",
          ["sc_cpa", "sc_ctr"], view=["label/creatives.production_source"], axes=["primary", "secondary"], config=BOTTOM)
    chart("sc_trend", "column_chart", "Social Spend by Platform by Month", "Meta / TikTok / LinkedIn spend.",
          ["sc_spend"], view=[MONTH], segment=[PLATFORM], config={**BOTTOM, "stack_measures": True})
    chart("sc_by_theme", "bar_chart", "Conversions by Creative Theme", "Message themes that convert.",
          ["sc_conversions"], view=["label/creatives.creative_theme"])
    chart("sc_top", "table", "Top Creatives", "Creatives ranked by spend.",
          ["sc_spend", "sc_impressions", "sc_ctr", "sc_thumbstop", "sc_conversions", "sc_cpa"],
          view=["label/creatives.creative_id.creative_name", "label/creatives.creative_format"])
    dashboard("d2_social_creatives", "Social Creatives", "2. Social & Creatives",
              "Creative analytics for Meta, TikTok and LinkedIn: formats, themes, production source, fatigue.",
              [(None, kpis(("sc_k_spend", 1), ("sc_k_ctr", 1), ("sc_k_cpa", 1), ("sc_k_thumb", 1), ("sc_k_hold", 1),
                           ("sc_k_live", 1))),
               ("Formats & Production", [("sc_by_format", 6, 16, 1), ("sc_by_source", 6, 16, 1)]),
               ("Trend", [("sc_trend", 7, 16, 1), ("sc_by_theme", 5, 16, 1)]),
               ("Creatives", [("sc_top", 12, 20, 1)])])

    # 3. Web Analytics & GEO -----------------------------------------------------
    for vid, title, m, desc in [("wa_k_rev", "Backend Revenue", "wa_revenue", "Revenue in the client's backend."),
                                ("wa_k_mer", "Blended ROAS (MER)", "wa_mer", "Total revenue / media cost."),
                                ("wa_k_paidshare", "Paid Share of Revenue", "wa_paid_share", "Revenue share of paid media."),
                                ("wa_k_cvr", "Site Conversion Rate", "wa_cvr", "Transactions per session."),
                                ("wa_k_newc", "New Customers", "wa_new_customers", "First-time customers."),
                                ("wa_k_ai", "AI Assistant Sessions", "wa_ai_sessions", "Sessions from ChatGPT, Perplexity, Gemini.")]:
        headline(vid, title, m, desc)
    chart("wa_rev_channel", "column_chart", "Backend Revenue by Channel by Month", "Revenue mix per channel group.",
          ["wa_revenue"], view=[MONTH], segment=["label/web_analytics_daily.channel_group"],
          config={**BOTTOM, "stack_measures": True})
    chart("wa_channels", "table", "Channel Performance", "Sessions, conversion rate, revenue and new customers per channel.",
          ["wa_sessions", "wa_transactions", "wa_cvr", "wa_revenue", "wa_aov", "wa_new_customers"],
          view=["label/web_analytics_daily.channel_group"], totals=["wa_sessions", "wa_transactions", "wa_revenue",
                                                                     "wa_new_customers"])
    chart("wa_ai_trend", "combo_chart", "AI Assistant Traffic (GEO)", "Sessions from AI assistants and their share.",
          ["wa_ai_sessions", "wa_ai_share"], view=[MONTH], axes=["primary", "secondary"], config=BOTTOM)
    chart("wa_attrib", "line_chart", "Platform vs Backend ROAS", "Platform-reported ROAS vs de-duplicated backend ROAS.",
          ["pm_roas", "wa_paid_roas", "wa_mer"], view=[MONTH], config=BOTTOM)
    chart("wa_market", "table", "Revenue & Efficiency by Market", "Backend revenue, media cost and MER per market.",
          ["wa_revenue", "pm_cost", "wa_mer", "wa_paid_roas", "wa_overattribution"], view=[MARKET])
    dashboard("d3_web_geo", "Web Analytics & GEO", "3. Web, Sales & GEO",
              "Backend truth: revenue by channel, blended ROAS (MER), platform over-attribution and AI-assistant traffic.",
              [(None, kpis(("wa_k_rev", 1), ("wa_k_mer", 1), ("wa_k_paidshare", 1), ("wa_k_cvr", 1), ("wa_k_newc", 1),
                           ("wa_k_ai", 1))),
               ("Channels", [("wa_rev_channel", 7, 16, 1), ("wa_channels", 5, 16, 1)]),
               ("Attribution & GEO", [("wa_attrib", 6, 16, 1), ("wa_ai_trend", 6, 16, 1), ("wa_market", 12, 14, 1)])],
              filters=("client", "market"))

    # 4. Budget & Pacing -----------------------------------------------------------
    headline("bp_k_planned", "Planned Budget (This Month)", "bp_planned", "Media plan for the current month.", compare=False)
    headline("bp_k_actual", "Spend (This Month)", "pm_cost", "Cost so far this month.", compare=False)
    headline("bp_k_pacing", "Pacing (This Month)", "bp_pacing", "Spend / plan for the current month.", compare=False)
    headline("bp_k_remaining", "Remaining (This Month)", "bp_remaining", "Budget left this month.", compare=False)
    this_month = {f"{DATE}_m": {"type": "date_filter", "granularity": "MONTH", "from": 0, "to": 0, "using": DATE}}
    for vid in ("bp_k_planned", "bp_k_actual", "bp_k_pacing", "bp_k_remaining"):
        VIS[vid]["query"]["filter_by"] = dict(this_month)
    chart("bp_trend", "combo_chart", "Planned vs Actual by Month", "Planned budget and actual cost (columns), pacing (line).",
          ["bp_planned", "pm_cost", "bp_pacing"], view=[MONTH], axes=["primary", "primary", "secondary"], config=BOTTOM)
    chart("bp_table", "table", "Pacing by Market & Platform (This Month)", "Where spend is ahead of or behind plan.",
          ["bp_planned", "pm_cost", "bp_pacing", "bp_variance"], view=[MARKET, PLATFORM], filters=dict(this_month),
          totals=["bp_planned", "pm_cost", "bp_variance"])
    chart("bp_platform", "bar_chart", "Pacing by Platform (This Month)", "Spend / plan per platform this month.",
          ["bp_pacing"], view=[PLATFORM], filters=dict(this_month))
    headline("bp_p_planned", "Planned Budget", "bp_planned", "", compare=False)
    headline("bp_p_actual", "Spend", "pm_cost", "", compare=False)
    headline("bp_p_pacing", "Budget Pacing", "bp_pacing", "", compare=False)
    headline("bp_p_variance", "Budget Variance", "bp_variance", "", compare=False)
    chart("bp_p_table", "table", "Plan vs Actual by Market & Platform", "",
          ["bp_planned", "pm_cost", "bp_pacing", "bp_variance"], view=[MARKET, PLATFORM],
          totals=["bp_planned", "pm_cost", "bp_variance"])
    dashboard("d4_budget_pacing", "Budget & Pacing", "4. Budget & Pacing",
              "Media plan vs actual spend: current-month under / over-spend, monthly pacing by market and platform, and "
              "plan vs actual for the selected period.",
              [(None, kpis(("bp_k_planned", None), ("bp_k_actual", None), ("bp_k_pacing", None),
                           ("bp_k_remaining", None))),
               ("This Month", [("bp_table", 7, 18, None), ("bp_platform", 5, 18, None)]),
               ("Selected Period", kpis(("bp_p_planned", 1), ("bp_p_actual", 1), ("bp_p_pacing", 1), ("bp_p_variance", 1))
                + [("bp_trend", 12, 16, 1), ("bp_p_table", 12, 18, 1)])],
              months=(-11, 1))

    # 5. Product Feed & Shopping ----------------------------------------------------
    for vid, title, m, desc in [("pf_k_cost", "Product Cost", "pf_cost", "Spend on product ads."),
                                ("pf_k_value", "Product Conversion Value", "pf_value", "Value of product-ad conversions."),
                                ("pf_k_roas", "Product ROAS", "pf_roas", "Value / cost."),
                                ("pf_k_ctr", "Product CTR", "pf_ctr", "Click-through rate."),
                                ("pf_k_products", "Products Advertised", "pf_products", "Products with impressions.")]:
        headline(vid, title, m, desc)
    chart("pf_feed", "line_chart", "CTR: SmartFeeds-optimized vs Not", "Weekly product CTR split by feed optimization.",
          ["pf_ctr"], view=[WEEK], segment=["label/products.feed_optimized"], config=BOTTOM)
    chart("pf_category", "bar_chart", "ROAS by Product Category", "Product ROAS per category.", ["pf_roas", "pf_cost"],
          view=["label/products.product_category"], config=BOTTOM)
    chart("pf_platform", "donut_chart", "Product Cost by Platform", "Google vs Microsoft vs Amazon.", ["pf_cost"],
          view=[PLATFORM], config={"legend_position": "right"})
    chart("pf_top", "table", "Top Products", "Products ranked by conversion value.",
          ["pf_value", "pf_cost", "pf_roas", "pf_ctr", "pf_conversions"],
          view=["label/products.product_id.product_title", "label/products.feed_optimized"])
    dashboard("d5_product_feed", "Product Feed & Shopping", "5. Product Feed & Shopping",
              "Shopping, Performance Max and Amazon at product level; impact of feed optimization (SmartFeeds).",
              [(None, kpis(("pf_k_cost", 1), ("pf_k_value", 1), ("pf_k_roas", 1), ("pf_k_ctr", 1), ("pf_k_products", 1))),
               ("Feed Optimization", [("pf_feed", 8, 16, 1), ("pf_platform", 4, 16, 1)]),
               ("Products", [("pf_category", 5, 18, 1), ("pf_top", 7, 18, 1)])])

    # 6. CRM & Offline Sales ---------------------------------------------------------
    for vid, title, m, desc in [("crm_k_leads", "Leads", "crm_leads", "CRM leads."),
                                ("crm_k_qual", "Qualification Rate", "crm_qual_rate", "Qualified / leads."),
                                ("crm_k_won", "Won Deals", "crm_won", "Cars sold / deals signed."),
                                ("crm_k_value", "Deal Value", "crm_deal_value", "Value of won deals."),
                                ("crm_k_cpl", "Cost per Lead", "crm_cpl", "Lead-gen cost / paid leads."),
                                ("crm_k_cpw", "Cost per Won Deal", "crm_cost_per_won", "Lead-gen cost / won deals.")]:
        headline(vid, title, m, desc)
    chart("crm_funnel", "funnel_chart", "Lead Funnel", "Leads -> qualified -> opportunity -> won.",
          ["crm_leads", "crm_qualified", "crm_opportunities", "crm_won"])
    chart("crm_trend", "combo_chart", "Leads & Qualification Rate by Month", "Lead volume (columns) and quality (line).",
          ["crm_leads", "crm_qual_rate"], view=[MONTH], axes=["primary", "secondary"], config=BOTTOM)
    chart("crm_cost_trend", "line_chart", "Cost per Lead & per Won Deal by Month",
          "Cost efficiency of lead generation - offline conversion import (SmartConversion) lowers cost per sale.",
          ["crm_cpql", "crm_cost_per_won"], view=[MONTH], config=BOTTOM)
    chart("crm_platform", "table", "Lead Quality by Platform", "Volume, qualification, win rate and value per platform.",
          ["crm_leads", "crm_qual_rate", "crm_win_rate", "crm_won", "crm_deal_value"], view=[PLATFORM])
    chart("crm_location", "table", "Performance by Location", "Dealerships / sales offices.",
          ["crm_leads", "crm_qual_rate", "crm_won", "crm_deal_value", "crm_contact_hours"],
          view=["label/business_locations.location_id.location_name"], totals=["crm_leads", "crm_won", "crm_deal_value"])
    chart("crm_status", "donut_chart", "Lead Status", "Where leads end up.", ["crm_leads"],
          view=["label/crm_leads.lead_status"], config={"legend_position": "right"})
    dashboard("d6_crm_offline", "CRM & Offline Sales", "6. CRM & Offline Sales",
              "First-party CRM: lead quality, conversion to sales, cost per sold car / B2B deal and offline conversion import.",
              [(None, kpis(("crm_k_leads", 1), ("crm_k_qual", 1), ("crm_k_won", 1), ("crm_k_value", 1), ("crm_k_cpl", 1),
                           ("crm_k_cpw", 1))),
               ("Funnel", [("crm_funnel", 4, 16, 1), ("crm_trend", 8, 16, 1)]),
               ("Efficiency", [("crm_cost_trend", 6, 16, 1), ("crm_platform", 6, 16, 1)]),
               ("Locations", [("crm_location", 8, 18, 1), ("crm_status", 4, 18, 1)])],
              months=(-23, 0))

    # 7. Measurement & Incrementality ---------------------------------------------------
    headline("mi_k_tests", "Tests", "mi_tests", "Incrementality tests started.", compare=False)
    headline("mi_k_iroas", "iROAS", "mi_iroas", "Incremental revenue / test spend.", compare=False)
    headline("mi_k_rev", "Incremental Revenue", "mi_inc_revenue", "Revenue caused by the media.", compare=False)
    headline("mi_k_share", "Truly Incremental", "mi_inc_share", "Share of platform conversions that were incremental.",
             compare=False)
    chart("mi_scope", "bar_chart", "iROAS by Campaign Scope", "Which channels really drive incremental revenue.",
          ["mi_iroas"], view=["label/incrementality_tests.campaign_scope"])
    chart("mi_table", "table", "Test Results", "All tests with result and recommendation.",
          ["mi_spend", "mi_iroas", "mi_inc_revenue"],
          view=["label/incrementality_tests.test_id.test_name", "label/incrementality_tests.test_status",
                "label/incrementality_tests.is_significant", "label/incrementality_tests.recommendation"])
    dashboard("d7_measurement", "Measurement & Incrementality", "7. Measurement & Incrementality",
              "Geo-lift and conversion-lift tests: iROAS per channel versus platform-reported results.",
              [(None, kpis(("mi_k_tests", 1), ("mi_k_iroas", 1), ("mi_k_rev", 1), ("mi_k_share", 1))),
               ("Results", [("mi_scope", 5, 18, 1), ("mi_table", 7, 18, 1)])], months=(-35, 0))

    # 8. Arcane Operations (internal) ---------------------------------------------------
    for vid, title, m, desc, cmp_ in [("op_k_req", "Data Requests", "op_requests", "Requests submitted.", True),
                                      ("op_k_days", "Avg Days to Deliver", "op_days", "Request to delivery.", True),
                                      ("op_k_open", "Open Requests", "op_open", "In progress + backlog.", False),
                                      ("op_k_effort", "Effort Hours", "op_effort", "Consultant hours.", True)]:
        headline(vid, title, m, desc, compare=cmp_)
    chart("op_trend", "column_chart", "Requests by Type by Month", "What clients and media consultants ask for.",
          ["op_requests"], view=[MONTH], segment=["label/data_requests.request_type"],
          config={**BOTTOM, "stack_measures": True})
    chart("op_days_type", "bar_chart", "Days to Deliver by Request Type", "Lead time per request type.", ["op_days"],
          view=["label/data_requests.request_type"])
    chart("op_list", "table", "Request Log", "Latest requests with status and delivery time.",
          ["op_days", "op_effort"], view=["label/data_requests.request_id.request_summary", CLIENT,
                                          "label/data_requests.request_status"], sort=False)
    chart("op_entitlements", "table", "Client Data Products", "Data products enabled per client (drives permissions).",
          ["op_entitled"], view=[CLIENT, "label/client_data_products.data_product", "label/client_data_products.package"],
          filters=incl("label/client_data_products.is_enabled", "Yes"), sort=False)
    dashboard("d8_arcane_ops", "Arcane Operations", "8. Arcane Operations (internal)",
              "Today's data-support loop: request volume, delivery time and effort - plus client data-product entitlements.",
              [(None, kpis(("op_k_req", 1), ("op_k_days", 1), ("op_k_open", None), ("op_k_effort", 1))),
               ("Requests", [("op_trend", 7, 16, 1), ("op_days_type", 5, 16, 1), ("op_list", 12, 18, 1)]),
               ("Entitlements", [("op_entitlements", 12, 14, None)])], filters=("client",))


# ---------------------------------------------------------------------------
# Checks, manifest, output
# ---------------------------------------------------------------------------
REF = re.compile(r"\{?(fact|label|attribute|dataset|metric)/([A-Za-z0-9_.]+)\}?")


def check_and_manifest():
    ds_ids = set(MODEL) | set(DATES)
    metric_product = {m[0]: m[5] for m in METRICS}
    ok_for = lambda product: (SHARED, CORE, product)

    def check(owner, product, text):
        for kind, ident in REF.findall(text):
            if kind == "metric":
                if metric_product[ident] not in ok_for(product):
                    raise SystemExit(f"{owner} ({product}) uses metric {ident} of {metric_product[ident]}")
                continue
            ds = ident.split(".")[0]
            if ds not in ds_ids:
                raise SystemExit(f"{owner}: unknown reference {kind}/{ident}")
            if product_of_dataset(ds) not in ok_for(product):
                raise SystemExit(f"{owner} ({product}) uses {kind}/{ident} of {product_of_dataset(ds)}")

    for mid, _, maql, _, _, tag in METRICS:
        check(f"metric {mid}", tag, maql)
    for vid, v in VIS.items():
        if "tags" not in v:
            raise SystemExit(f"visualisation {vid} is not on any dashboard")
        check(f"visualisation {vid}", v["tags"][0], yaml.safe_dump(v))
    for d in DASHBOARDS:
        check(f"dashboard {d['id']}", d["tags"][0], yaml.safe_dump(d))

    manifest = {}
    for product, x in DP["data_products"].items():
        facts, attrs, labels = [], [], []
        for t in x["datasets"]:
            m = MODEL[t]
            pk_id = f"{t}.{m['pk'][0]}"
            attrs.append(pk_id)
            labels += [f"{pk_id}.{c}" for c, _, _ in m.get("labels", [])]
            attrs += [f"{t}.{c}" for c, _ in m.get("attrs", [])]
            facts += [f"{t}.{c}" for c, _ in m.get("facts", [])]
        manifest[product] = {
            "user_group": x["user_group"], "package": x["package"], "datasets": x["datasets"], "facts": facts,
            "attributes": attrs, "labels": labels, "metrics": [m[0] for m in METRICS if m[5] == product],
            "visualizations": [v for v, d in VIS.items() if d["tags"] == [product]],
            "dashboards": [d["id"] for d in DASHBOARDS if d["tags"] == [product]]}
    with open(os.path.join(HERE, "data_products.json"), "w") as f:
        json.dump({"entitlements": DP["entitlements"], "products": manifest}, f, indent=2, ensure_ascii=False)
    return manifest


def dump(folder, name, doc):
    with open(os.path.join(OUT, folder, f"{name}.yaml"), "w") as f:
        f.write("# Generated by gooddata/build_analytics.py - edit the generator, not this file.\n\n")
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=120)


def main():
    for folder in ("datasets", "metrics", "visualisations", "dashboards"):
        p = os.path.join(OUT, folder)
        if os.path.isdir(p):
            shutil.rmtree(p)
        os.makedirs(p)
    for name, doc in build_datasets().items():
        dump("datasets", name, doc)
    build_metrics()
    missing = [m[0] for m in METRICS if m[0] not in METRIC_DESC]
    if missing:
        raise SystemExit(f"no description in descriptions.METRIC_DESC for metrics {missing}")
    for mid, title, maql, fmt, desc, tag in METRICS:
        desc = METRIC_DESC[mid]
        dump("metrics", mid, {"type": "metric", "id": mid, "title": title, "description": desc, "tags": [tag],
                              "maql": maql, "format": fmt})
    build_visuals()
    missing = [v for v in VIS if v not in VIS_DESC]
    if missing:
        raise SystemExit(f"no description in descriptions.VIS_DESC for visualisations {missing}")
    for vid, v in VIS.items():
        v["description"] = VIS_DESC[vid]
    manifest = check_and_manifest()
    for vid, doc in VIS.items():
        dump("visualisations", vid, doc)
    for d in DASHBOARDS:
        dump("dashboards", d["id"], d)
    for product, x in manifest.items():
        print(f"  {product:<30} {x['user_group']:<36} metrics {len(x['metrics']):>2}  vis {len(x['visualizations']):>2}")
    print(f"datasets {len(MODEL) + len(DATES)}, metrics {len(METRICS)}, visualisations {len(VIS)}, "
          f"dashboards {len(DASHBOARDS)}")


if __name__ == "__main__":
    main()
