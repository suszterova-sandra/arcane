#!/usr/bin/env python3
"""
Arcane demo data generator for GoodData Cloud (multitenant, white-labelled agency analytics).

Arcane (https://www.arcane.run) is a Paris media & data agency (SEA, SMA, retail media, video,
feed engineering, measurement). Today: Adverity -> BigQuery -> scheduled queries -> one Looker
Studio report per client. This data source mimics that "standardised marketing schema" plus the
custom extensions Arcane builds for top accounts (product feed, CRM / offline sales, incrementality).

Multitenancy: every tenant table carries `wdf__client_id` (= GoodData child workspace client ID).
Global reference tables (platforms, markets) have none.

Consistency:
  * social campaign rows in ad_performance_daily = sum of creative_performance_daily
  * product_performance_weekly sums to the weekly totals of the shopping / PMax / Amazon campaigns
  * web_analytics_daily paid channels are derived from the ad clicks / conversions (de-duplicated,
    i.e. platform-reported conversions are over-attributed vs the client's backend)
  * crm_leads (AutoNova dealer leads, Seconde Vie Pro B2B leads) are generated from campaign clicks / conversions
  * media_budgets plan vs actual spend; incrementality_tests spend = actual campaign spend in window

Usage:  python3 generate.py      -> ./csv/*.csv and ./ddl/*.sql   (deterministic)
"""
import csv
import datetime as dt
import math
import os
import random
from collections import defaultdict

SEED = 20261116
START = dt.date(2024, 1, 1)
END = dt.date(2026, 11, 15)            # last day with actuals (yesterday)
NA_DATE = "1900-01-01"                 # "not applicable" date sentinel (no NULLs anywhere)
NA = "N/A"
WDF = "wdf__client_id"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(HERE, "csv")
OUT_DDL = os.path.join(HERE, "ddl")

rng = random.Random(SEED)
SPAN = (END - START).days
DAYS = [START + dt.timedelta(days=i) for i in range(SPAN + 1)]


def progress(d):
    return min(1.0, max(0.0, (d - START).days / SPAN))


def poisson(lam):
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


cnt = poisson


def lognorm(sig):
    return math.exp(rng.gauss(0, sig) - sig * sig / 2)


def wchoice(pairs):
    tot = sum(w for _, w in pairs)
    r = rng.random() * tot
    for v, w in pairs:
        r -= w
        if r <= 0:
            return v
    return pairs[-1][0]


def r2(x):
    return round(x + 0.0, 2)


def yn(b):
    return "Yes" if b else "No"


def ramp(d, start, days):
    """0 before start, linear to 1 over `days`."""
    if d < start:
        return 0.0
    return min(1.0, (d - start).days / days)


def split_int(total, ws):
    s = sum(ws)
    if total <= 0 or s <= 0:
        return [0] * len(ws)
    raw = [total * w / s for w in ws]
    out = [int(x) for x in raw]
    rem = total - sum(out)
    for i in sorted(range(len(ws)), key=lambda i: raw[i] - out[i], reverse=True)[:rem]:
        out[i] += 1
    return out


def split_money(total, ws):
    s = sum(ws)
    if s <= 0:
        return [0.0] * len(ws)
    out = [round(total * w / s, 2) for w in ws]
    big = max(range(len(ws)), key=lambda i: ws[i])
    out[big] = round(out[big] + total - sum(out), 2)
    return out


def week_start(d):
    return d - dt.timedelta(days=d.weekday())


def month_start(d):
    return d.replace(day=1)


# ---------------------------------------------------------------------------
# Schema (column order = CSV order)
# ---------------------------------------------------------------------------
K = "VARCHAR(64)"
T = "VARCHAR(160)"
D = "DATE"
M = "NUMERIC(14,2)"
N = "NUMERIC(12,2)"
P = "NUMERIC(6,4)"
I = "INTEGER"
B = "BIGINT"
GEO = "NUMERIC(9,6)"
YN = "VARCHAR(3)"

SCHEMA = {
    # ---- global reference (no WDF) ----
    "platforms": [("platform_id", K), ("platform_name", T), ("platform_vendor", T), ("platform_category", T),
                  ("arcane_practice", T), ("adverity_connector", T), ("is_paid", YN)],
    "markets": [("market_id", "VARCHAR(2)"), ("country_name", T), ("market_region", T), ("currency_code", "VARCHAR(3)"),
                ("eur_fx_rate", P), ("language", T), ("capital_city", T), ("latitude", GEO), ("longitude", GEO)],
    # ---- tenant dimensions ----
    "clients": [("client_id", K), ("client_name", T), ("industry", T), ("business_model", T), ("client_tier", T),
                ("data_schema", T), ("data_extensions", T), ("primary_kpi", T), ("primary_kpi_definition", T),
                ("target_type", T), ("target_value", N), ("headquarters_city", T), ("arcane_client_since", D),
                ("media_consultant", T), ("data_consultant", T), ("monthly_budget_eur", M), (WDF, K)],
    "campaigns": [("campaign_id", K), ("campaign_name", T), ("client_id", K), ("platform_id", K), ("market_id", "VARCHAR(2)"),
                  ("campaign_type", T), ("channel_group", T), ("funnel_stage", T), ("objective", T), ("is_brand", YN),
                  ("product_line", T), ("bidding_strategy", T), ("start_date", D), ("end_date", D),
                  ("campaign_status", T), (WDF, K)],
    "creatives": [("creative_id", K), ("creative_name", T), ("campaign_id", K), ("creative_format", T),
                  ("creative_theme", T), ("production_source", T), ("is_video", YN), ("launch_date", D),
                  ("end_date", D), ("creative_status", T), (WDF, K)],
    "products": [("product_id", K), ("sku", K), ("product_title", T), ("product_brand", T), ("product_category", T),
                 ("product_subcategory", T), ("product_condition", T), ("price_eur", M), ("margin_pct", P),
                 ("launch_date", D), ("feed_optimized", YN), ("feed_optimized_date", D), (WDF, K)],
    "business_locations": [("location_id", K), ("location_name", T), ("location_type", T), ("city", T), ("region", T),
                           ("country", T), ("postal_code", "VARCHAR(10)"), ("latitude", GEO), ("longitude", GEO),
                           (WDF, K)],
    # ---- facts ----
    "ad_performance_daily": [("performance_id", K), ("campaign_id", K), ("date", D), ("device", T),
                             ("impressions", B), ("clicks", B), ("cost_eur", M), ("cost_local_currency", M),
                             ("conversions", N), ("conversion_value_eur", M), ("video_views", B), ("engagements", B),
                             ("search_impressions", B), ("search_eligible_impressions", B),
                             ("search_lost_is_budget", B), ("search_lost_is_rank", B), (WDF, K)],
    "creative_performance_daily": [("creative_performance_id", K), ("creative_id", K), ("date", D), ("impressions", B),
                                   ("clicks", B), ("cost_eur", M), ("video_3s_views", B), ("thruplays", B),
                                   ("engagements", B), ("conversions", N), ("conversion_value_eur", M), (WDF, K)],
    "product_performance_weekly": [("product_performance_id", K), ("product_id", K), ("campaign_id", K),
                                   ("week_start_date", D), ("impressions", B), ("clicks", B), ("cost_eur", M),
                                   ("conversions", N), ("conversion_value_eur", M), (WDF, K)],
    "web_analytics_daily": [("web_id", K), ("client_id", K), ("market_id", "VARCHAR(2)"), ("date", D),
                            ("channel_group", T), ("is_paid_channel", YN), ("sessions", B), ("engaged_sessions", B),
                            ("new_users", B), ("transactions", I), ("revenue_eur", M), ("gross_margin_eur", M),
                            ("new_customers", I), ("leads", I), (WDF, K)],
    "crm_leads": [("lead_id", K), ("campaign_id", K), ("location_id", K), ("lead_date", D), ("lead_type", T),
                  ("product_brand", T), ("product_name", T), ("product_line", T), ("product_segment", T),
                  ("product_variant", T), ("is_existing_customer", YN), ("lead_status", T), ("contacted_date", D),
                  ("hours_to_first_contact", N), ("opportunity_type", T), ("opportunity_date", D), ("won_date", D),
                  ("days_to_close", I), ("deal_value_eur", M), ("gross_profit_eur", M),
                  ("offline_conversion_uploaded", YN), ("is_qualified", I), ("is_opportunity", I), ("is_won", I),
                  (WDF, K)],
    "media_budgets": [("budget_id", K), ("client_id", K), ("platform_id", K), ("market_id", "VARCHAR(2)"),
                      ("budget_month", D), ("planned_budget_eur", M), ("target_roas", N), ("target_cpa_eur", N),
                      ("budget_owner", T), (WDF, K)],
    "incrementality_tests": [("test_id", K), ("client_id", K), ("platform_id", K), ("market_id", "VARCHAR(2)"),
                             ("test_name", T), ("campaign_scope", T), ("methodology", T), ("start_date", D),
                             ("end_date", D), ("test_status", T), ("test_spend_eur", M), ("platform_conversions", N),
                             ("incremental_conversions", N), ("incremental_revenue_eur", M), ("lift_pct", N),
                             ("iroas", N), ("confidence_level", N), ("is_significant", YN), ("recommendation", T),
                             (WDF, K)],
    "data_requests": [("request_id", K), ("client_id", K), ("submitted_date", D), ("requested_by_role", T),
                      ("request_channel", T), ("request_type", T), ("request_summary", T), ("priority", T),
                      ("assigned_to", T), ("request_status", T), ("delivered_date", D), ("days_to_deliver", I),
                      ("effort_hours", N), ("is_delivered", I), (WDF, K)],
    # ---- entitlements (which data products each client has; drives object-level permissions) ----
    "client_data_products": [("entitlement_id", K), ("client_id", K), ("data_product", T), ("package", T),
                             ("audience", T), ("is_enabled", YN), ("enabled_since", D), ("user_group", K), (WDF, K)],
}

PRIMARY_KEYS = {
    "platforms": ["platform_id"], "markets": ["market_id"], "clients": ["client_id"], "campaigns": ["campaign_id"],
    "creatives": ["creative_id"], "products": ["product_id"], "business_locations": ["location_id"],
    "ad_performance_daily": ["performance_id"], "creative_performance_daily": ["creative_performance_id"],
    "product_performance_weekly": ["product_performance_id"], "web_analytics_daily": ["web_id"],
    "crm_leads": ["lead_id"], "media_budgets": ["budget_id"], "incrementality_tests": ["test_id"],
    "data_requests": ["request_id"], "client_data_products": ["entitlement_id"],
}

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
PLATFORMS = [
    ("google_ads", "Google Ads", "Google", "Search, Shopping & Video", "SEA", "Google Ads", "Yes"),
    ("microsoft_ads", "Microsoft Advertising", "Microsoft", "Search & Shopping", "SEA", "Microsoft Advertising", "Yes"),
    ("meta_ads", "Meta Ads", "Meta", "Social", "SMA", "Facebook Ads", "Yes"),
    ("tiktok_ads", "TikTok Ads", "TikTok", "Social", "SMA", "TikTok Ads", "Yes"),
    ("linkedin_ads", "LinkedIn Ads", "LinkedIn", "Social", "SMA", "LinkedIn Ads", "Yes"),
    ("pinterest_ads", "Pinterest Ads", "Pinterest", "Social", "SMA", "Pinterest Ads", "Yes"),
    ("amazon_ads", "Amazon Ads", "Amazon", "Retail Media", "Retail Media", "Amazon Advertising", "Yes"),
    ("dv360", "Display & Video 360", "Google", "Programmatic", "Programmatic & Video", "Display & Video 360", "Yes"),
    ("non_paid", "Non-paid (Organic / Direct)", "N/A", "Non-paid", "SEO / CRM", "GA4 / CRM", "No"),
]

MARKETS = {  # id: name, region, currency, eur fx, language, capital, lat, lon, cpc multiplier
    "FR": ("France", "France", "EUR", 1.0, "French", "Paris", 48.856600, 2.352200, 1.00),
    "BE": ("Belgium", "Benelux", "EUR", 1.0, "French / Dutch", "Brussels", 50.850300, 4.351700, 0.90),
    "CH": ("Switzerland", "DACH", "CHF", 0.94, "French / German", "Bern", 46.948000, 7.447400, 1.35),
    "DE": ("Germany", "DACH", "EUR", 1.0, "German", "Berlin", 52.520000, 13.405000, 1.10),
    "ES": ("Spain", "Southern Europe", "EUR", 1.0, "Spanish", "Madrid", 40.416800, -3.703800, 0.75),
    "IT": ("Italy", "Southern Europe", "EUR", 1.0, "Italian", "Rome", 41.902800, 12.496400, 0.80),
    "GB": ("United Kingdom", "UK & Ireland", "GBP", 0.84, "English", "London", 51.507400, -0.127800, 1.20),
    "US": ("United States", "North America", "USD", 1.08, "English", "Washington, D.C.", 38.907200, -77.036900, 1.40),
}

# campaign types: platform, channel group, funnel, objective, brand, cpc, ctr, cvr, value multiplier,
# kind (search/shopping/social/video/retail), naming code, bidding, attribution over-count vs backend, start, end
CT = {
    "Search - Brand": dict(p="google_ads", ch="Paid Search", funnel="Conversion", obj="Sales", brand=True, cpc=0.32,
                           ctr=0.16, cvr=0.085, vm=1.05, kind="search", code="GADS_SEA_Brand",
                           bid="Target Impression Share", attr=1.10, is_=0.92, lb=0.01),
    "Search - Generic": dict(p="google_ads", ch="Paid Search", funnel="Consideration", obj="Sales", brand=False,
                             cpc=1.05, ctr=0.055, cvr=0.032, vm=1.0, kind="search", code="GADS_SEA_Generic",
                             bid="Target ROAS", attr=1.25, is_=0.55, lb=0.07, per_line=True),
    "Shopping": dict(p="google_ads", ch="Paid Shopping", funnel="Conversion", obj="Sales", brand=False, cpc=0.55,
                     ctr=0.011, cvr=0.028, vm=1.0, kind="shopping", code="GADS_Shopping", bid="Target ROAS",
                     attr=1.15, is_=0.6, lb=0.08, per_line=True, end=dt.date(2025, 3, 31)),
    "Performance Max": dict(p="google_ads", ch="Paid Shopping", funnel="Conversion", obj="Sales", brand=False,
                            cpc=0.62, ctr=0.009, cvr=0.030, vm=1.0, kind="pmax", code="GADS_PMax",
                            bid="Target ROAS", attr=1.40),
    "Demand Gen": dict(p="google_ads", ch="Paid Video & Display", funnel="Consideration", obj="Traffic", brand=False,
                       cpc=0.45, ctr=0.006, cvr=0.008, vm=0.9, kind="video", code="GADS_DemandGen",
                       bid="Maximize Conversions", attr=2.2, start=dt.date(2024, 6, 1)),
    "YouTube": dict(p="google_ads", ch="Paid Video & Display", funnel="Awareness", obj="Reach", brand=False, cpc=1.7,
                    ctr=0.0035, cvr=0.004, vm=0.9, kind="video", code="GADS_YT_Reach", bid="Target CPM", attr=3.0),
    "Microsoft Search": dict(p="microsoft_ads", ch="Paid Search", funnel="Conversion", obj="Sales", brand=False,
                             cpc=0.75, ctr=0.05, cvr=0.035, vm=1.05, kind="search", code="MSA_Search",
                             bid="Enhanced CPC", attr=1.2, is_=0.62, lb=0.05),
    "Microsoft Shopping": dict(p="microsoft_ads", ch="Paid Shopping", funnel="Conversion", obj="Sales", brand=False,
                               cpc=0.45, ctr=0.012, cvr=0.026, vm=1.0, kind="shopping", code="MSA_Shopping",
                               bid="Target ROAS", attr=1.15, is_=0.65, lb=0.05),
    "Meta - Prospecting": dict(p="meta_ads", ch="Paid Social", funnel="Consideration", obj="Conversions",
                               brand=False, cpc=0.85, ctr=0.011, cvr=0.012, vm=0.95, kind="social",
                               code="META_Prospecting", bid="Lowest Cost", attr=1.7),
    "Meta - Retargeting": dict(p="meta_ads", ch="Paid Social", funnel="Conversion", obj="Conversions", brand=False,
                               cpc=0.70, ctr=0.016, cvr=0.035, vm=1.0, kind="social", code="META_Retargeting",
                               bid="Cost Cap", attr=1.9),
    "Meta - Advantage+ Shopping": dict(p="meta_ads", ch="Paid Social", funnel="Conversion", obj="Sales",
                                       brand=False, cpc=0.75, ctr=0.013, cvr=0.022, vm=1.0, kind="social",
                                       code="META_ASC", bid="Lowest Cost", attr=1.6, start=dt.date(2024, 4, 1)),
    "Meta - Lead Ads": dict(p="meta_ads", ch="Paid Social", funnel="Conversion", obj="Leads", brand=False, cpc=0.9,
                            ctr=0.012, cvr=0.07, vm=1.0, kind="social", code="META_LeadAds", bid="Cost Cap",
                            attr=1.3),
    "Search - B2B Leads": dict(p="google_ads", ch="Paid Search", funnel="Consideration", obj="Leads", brand=False,
                               cpc=2.2, ctr=0.045, cvr=0.06, vm=1.5, kind="search", code="GADS_SEA_B2B_Pro",
                               bid="Maximize Conversions", attr=1.15, is_=0.5, lb=0.05),
    "LinkedIn - Lead Gen Forms": dict(p="linkedin_ads", ch="Paid Social", funnel="Consideration", obj="Leads",
                                      brand=False, cpc=6.5, ctr=0.006, cvr=0.09, vm=1.5, kind="social",
                                      code="LI_LeadGen_Pro", bid="Cost Cap", attr=1.3),
    "TikTok - Spark Ads": dict(p="tiktok_ads", ch="Paid Social", funnel="Consideration", obj="Conversions",
                               brand=False, cpc=0.55, ctr=0.009, cvr=0.008, vm=0.9, kind="social",
                               code="TT_SparkAds", bid="Lowest Cost", attr=2.0),
    "Pinterest - Shopping": dict(p="pinterest_ads", ch="Paid Social", funnel="Consideration", obj="Catalog Sales",
                                 brand=False, cpc=0.5, ctr=0.007, cvr=0.012, vm=1.1, kind="social",
                                 code="PIN_Shopping", bid="Target ROAS", attr=1.8),
    "Amazon - Sponsored Products": dict(p="amazon_ads", ch="Retail Media", funnel="Conversion", obj="Sales",
                                        brand=False, cpc=0.9, ctr=0.004, cvr=0.10, vm=1.0, kind="retail",
                                        code="AMZ_SponsoredProducts", bid="Dynamic bids - down only", attr=1.0),
    "DV360 - Online Video": dict(p="dv360", ch="Paid Video & Display", funnel="Awareness", obj="Reach",
                                 brand=False, cpc=3.0, ctr=0.0015, cvr=0.002, vm=0.9, kind="video",
                                 code="DV360_OLV", bid="Target CPM", attr=4.0),
}
SHOPPING_KINDS = ("shopping", "pmax", "retail")

DEVICES = {
    "search": [("Mobile", 0.60, 1.00, 0.85), ("Desktop", 0.34, 0.95, 1.35), ("Tablet", 0.06, 1.0, 0.95)],
    "shopping": [("Mobile", 0.64, 1.00, 0.85), ("Desktop", 0.30, 0.95, 1.35), ("Tablet", 0.06, 1.0, 0.95)],
    "pmax": [("Mobile", 0.66, 1.00, 0.88), ("Desktop", 0.28, 0.95, 1.30), ("Tablet", 0.06, 1.0, 0.95)],
    "video": [("Mobile", 0.50, 1.00, 0.9), ("Desktop", 0.15, 1.10, 1.3), ("Connected TV", 0.35, 0.4, 0.6)],
    "retail": [("Mobile", 0.62, 1.00, 0.95), ("Desktop", 0.38, 1.00, 1.10)],
    "social": [("Mobile", 0.93, 1, 1), ("Desktop", 0.07, 1, 1)],
}

# ---------------------------------------------------------------------------
# Seasonality (French retail calendar)
# ---------------------------------------------------------------------------
EASTER = {2024: dt.date(2024, 3, 31), 2025: dt.date(2025, 4, 20), 2026: dt.date(2026, 4, 5)}
MOTHERS_DAY_FR = {2024: dt.date(2024, 5, 26), 2025: dt.date(2025, 5, 25), 2026: dt.date(2026, 5, 31)}
SOLDES_WINTER = {2024: dt.date(2024, 1, 10), 2025: dt.date(2025, 1, 8), 2026: dt.date(2026, 1, 7)}
SOLDES_SUMMER = {2024: dt.date(2024, 6, 26), 2025: dt.date(2025, 6, 25), 2026: dt.date(2026, 6, 24)}
PRIME_DAY = {2024: (dt.date(2024, 7, 16), 2), 2025: (dt.date(2025, 7, 8), 4), 2026: (dt.date(2026, 7, 7), 4)}
MONDIAL_AUTO = [(dt.date(2024, 10, 14), dt.date(2024, 10, 20)), (dt.date(2026, 10, 12), dt.date(2026, 10, 18))]


def black_friday(y):
    d = dt.date(y, 11, 1)
    while d.weekday() != 3:
        d += dt.timedelta(days=1)
    return d + dt.timedelta(days=22)


BF = {y: black_friday(y) for y in (2024, 2025, 2026)}

MONTHLY = {
    "electronics": [0.85, 0.85, 0.90, 0.92, 0.95, 0.92, 0.95, 1.00, 1.10, 1.00, 1.15, 1.20],
    "fashion": [1.00, 0.85, 0.95, 1.00, 1.00, 0.95, 1.00, 1.10, 1.20, 1.00, 1.05, 1.15],
    "cosmetics": [0.80, 0.95, 0.90, 0.95, 1.00, 0.90, 0.80, 0.80, 0.95, 1.00, 1.30, 1.50],
    "travel": [0.75, 0.85, 1.10, 1.20, 1.25, 1.25, 1.15, 0.95, 0.90, 0.85, 0.75, 0.80],
    "automotive": [1.10, 1.05, 1.10, 1.00, 1.00, 0.95, 0.85, 0.70, 1.10, 1.15, 1.00, 0.90],
    "furniture": [1.25, 0.95, 0.95, 1.00, 1.00, 0.95, 0.85, 0.85, 1.10, 1.15, 1.15, 0.90],
}
WEEKDAY = {
    "retail": [1.05, 1.00, 0.98, 0.97, 0.92, 0.93, 1.12],
    "automotive": [1.10, 1.05, 1.00, 1.00, 0.95, 1.00, 0.85],
    "travel": [1.05, 1.05, 1.00, 1.00, 0.95, 0.90, 1.05],
}


def season(v, d):
    y = d.year
    s = MONTHLY[v][d.month - 1]
    bf = BF[y]
    in_bf = bf - dt.timedelta(days=7) <= d <= bf + dt.timedelta(days=3)
    bf_peak = bf <= d <= bf + dt.timedelta(days=3)
    xmas = dt.date(y, 12, 1) <= d <= dt.date(y, 12, 21)
    xmas_dip = dt.date(y, 12, 24) <= d <= dt.date(y, 12, 31)
    sw = SOLDES_WINTER[y] <= d < SOLDES_WINTER[y] + dt.timedelta(days=28)
    ss = SOLDES_SUMMER[y] <= d < SOLDES_SUMMER[y] + dt.timedelta(days=28)
    rentree = dt.date(y, 8, 18) <= d <= dt.date(y, 9, 10)
    if v == "electronics":
        s *= (2.0 if bf_peak else 1.6) if in_bf else 1.0
        s *= 1.35 if xmas else 1.0
        s *= 1.25 if rentree else 1.0
    elif v == "fashion":
        s *= 1.5 if (sw or ss) else 1.0
        s *= 1.35 if rentree else 1.0
        s *= (1.9 if bf_peak else 1.5) if in_bf else 1.0
        s *= 1.2 if xmas else 1.0
    elif v == "cosmetics":
        md = MOTHERS_DAY_FR[y]
        s *= 1.6 if md - dt.timedelta(days=14) <= d <= md else 1.0
        s *= 1.25 if dt.date(y, 2, 1) <= d <= dt.date(y, 2, 14) else 1.0
        s *= (1.9 if bf_peak else 1.5) if in_bf else 1.0
        s *= 1.3 if xmas else 1.0
    elif v == "travel":
        e = EASTER[y]
        s *= 1.3 if e - dt.timedelta(days=21) <= d <= e else 1.0
        s *= 1.15 if bf_peak else 1.0
    elif v == "automotive":
        s *= 1.35 if any(a <= d <= b for a, b in MONDIAL_AUTO) else 1.0
        s *= 1.1 if bf_peak else 1.0
    elif v == "furniture":
        s *= 1.4 if (sw or ss) else 1.0
        s *= (1.7 if bf_peak else 1.4) if in_bf else 1.0
    if xmas_dip:
        s *= 0.7 if v != "automotive" else 0.5
    return s


# ---------------------------------------------------------------------------
# Tenants (fictional advertisers; sectors mirror Arcane's case studies)
# ---------------------------------------------------------------------------
CLIENTS = [
    dict(id="secondevie", name="Seconde Vie", code="SV", industry="Refurbished Electronics",
         model="E-commerce marketplace (multi-market)", vert="electronics", wk="retail", tier="Top Account",
         schema="Custom (top-account recipe)",
         ext="Product feed (SmartFeeds), Amazon retail media, B2B CRM (Seconde Vie Pro), incrementality tests",
         kpi="Commandes (GMV)", kpi_def="Backend orders net of cancellations & returns within 14 days; GMV incl. VAT",
         target=("ROAS", 6.0), hq="Paris", since="2021-09-01", media="Camille Marchand",
         data="Inès Garnier", budget=1_650_000, growth=0.16, aov=345.0, cvr=0.30, cpc=1.0, margin=0.22,
         organic=150_000, web_cvr=0.0056, products=100,
         markets=[("FR", .38), ("DE", .20), ("ES", .12), ("IT", .10), ("GB", .12), ("US", .08)],
         lines=[("Smartphones", .45), ("Laptops", .20), ("Tablets", .12), ("Gaming Consoles", .10),
                ("Smartwatches & Audio", .13)],
         types={"Search - Brand": .07, "Search - Generic": .20, "Shopping": .14, "Performance Max": .22,
                "Demand Gen": .04, "YouTube": (.04, ["FR", "DE"]), "Microsoft Search": (.03, ["FR", "DE", "GB", "US"]),
                "Microsoft Shopping": (.02, ["FR", "DE", "GB"]), "Meta - Prospecting": .07, "Meta - Retargeting": .03,
                "Meta - Advantage+ Shopping": .05, "TikTok - Spark Ads": (.04, ["FR", "DE", "GB", "US"], dt.date(2024, 9, 2)),
                "Amazon - Sponsored Products": (.05, ["FR", "DE", "IT", "ES"]),
                "Search - B2B Leads": (.015, ["FR", "DE", "ES", "IT", "GB"]),           # Seconde Vie Pro (B2B)
                "LinkedIn - Lead Gen Forms": (.008, ["FR", "DE", "GB"], dt.date(2024, 3, 4))}),
    dict(id="autonova", name="AutoNova Automobiles", code="AN", industry="Automotive Dealer Network",
         model="Lead generation + offline sales (12 dealerships)", vert="automotive", wk="automotive",
         tier="Top Account", schema="Custom (top-account recipe)",
         ext="CRM leads & offline sales (SmartConversion offline conversion import)",
         kpi="Lead qualifié / Véhicule vendu", kpi_def="Qualified lead = CRM status reached 'Qualified' by a "
         "dealership sales rep; Sale = signed order in DMS", target=("CPA", 45.0), hq="Lyon",
         since="2022-02-01", media="Julien Moreau", data="Thomas Girard", budget=175_000, growth=0.08,
         aov=150.0, cvr=0.52, cpc=1.3, margin=0.09, organic=9_000, web_cvr=0.004, products=0,
         markets=[("FR", 1.0)],
         lines=[("New Cars", .35), ("Used Cars", .30), ("Electric & Hybrid", .25), ("Utility Vans", .10)],
         types={"Search - Brand": .10, "Search - Generic": .35, "Microsoft Search": .04, "Performance Max": .10,
                "Meta - Lead Ads": .20, "Meta - Retargeting": .06, "YouTube": .05, "Demand Gen": .05,
                "DV360 - Online Video": .05}),
    dict(id="routeo", name="Routéo Location", code="RT", industry="Car & Van Rental",
         model="Online bookings (5 countries)", vert="travel", wk="travel", tier="Standard",
         schema="Standard (long-tail schema)", ext="None",
         kpi="Réservations", kpi_def="Confirmed bookings (paid or guaranteed), cancellations excluded",
         target=("CPA", 28.0), hq="Nanterre", since="2022-06-01", media="Hugo Bernard", data="Manon Leroy",
         budget=640_000, growth=0.10, aov=310.0, cvr=0.45, cpc=0.95, margin=0.35, organic=80_000,
         web_cvr=0.009, products=0,
         markets=[("FR", .40), ("ES", .20), ("IT", .15), ("DE", .10), ("GB", .15)],
         lines=[("Car Rental", .45), ("Van & Truck Rental", .20), ("Airport Rental", .25), ("One-way Rental", .10)],
         types={"Search - Brand": .14, "Search - Generic": .34, "Microsoft Search": .05, "Performance Max": .08,
                "Meta - Prospecting": .10, "Meta - Retargeting": .08, "Demand Gen": .06, "YouTube": (.05, ["FR", "ES"])}),
]
CL = {c["id"]: c for c in CLIENTS}
DATA_CONSULTANTS = ["Inès Garnier", "Thomas Girard", "Manon Leroy"]

# ---- built-in demo stories ----
SV_DE_CAP = dt.date(2026, 10, 20)            # Seconde Vie DE generic search budget cap (performance drop)
RT_META_OUTAGE = (dt.date(2026, 9, 15), dt.date(2026, 9, 19))   # Routéo Meta CAPI outage
SV_SMARTFEEDS = dt.date(2026, 3, 2)          # Seconde Vie SmartFeeds go-live
AN_SMARTCONV = dt.date(2025, 3, 10)          # AutoNova offline conversion import (SmartConversion)
AN_META_CAPI = dt.date(2025, 6, 2)           # AutoNova CRM -> Meta CAPI
SV_PRO_OCI = dt.date(2025, 9, 1)             # Seconde Vie Pro won deals -> Google offline conversions


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------
class Writer:
    def __init__(self):
        os.makedirs(OUT_CSV, exist_ok=True)
        self.files, self.writers, self.counts = {}, {}, defaultdict(int)
        for t, cols in SCHEMA.items():
            f = open(os.path.join(OUT_CSV, f"{t}.csv"), "w", newline="")
            w = csv.writer(f)
            w.writerow([c for c, _ in cols])
            self.files[t], self.writers[t] = f, w

    def row(self, table, values):
        if len(values) != len(SCHEMA[table]):
            raise ValueError(f"{table}: expected {len(SCHEMA[table])} cols, got {len(values)}: {values}")
        for v in values:
            if v is None or v == "":
                raise ValueError(f"NULL/empty value in {table}: {values}")
        self.writers[table].writerow(values)
        self.counts[table] += 1

    def close(self):
        for f in self.files.values():
            f.close()


W = Writer()

for p in PLATFORMS:
    W.row("platforms", list(p))
used_markets = sorted({m for c in CLIENTS for m, _ in c["markets"]}, key=list(MARKETS).index)
for m in used_markets:
    n, reg, cur, fx, lang, cap, lat, lon, _ = MARKETS[m]
    W.row("markets", [m, n, reg, cur, fx, lang, cap, lat, lon])

for c in CLIENTS:
    tt, tv = c["target"]
    W.row("clients", [c["id"], c["name"], c["industry"], c["model"], c["tier"], c["schema"], c["ext"], c["kpi"],
                      c["kpi_def"], f"Target {tt}", tv, c["hq"], c["since"], c["media"], c["data"],
                      r2(c["budget"] * (1 + c["growth"]) ** 2.8), c["id"]])

# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------
_ids = set()


def platform_id():
    while True:
        x = str(rng.randint(10 ** 9, 10 ** 10 - 1))
        if x not in _ids:
            _ids.add(x)
            return x


LINE_CODE = lambda s: "".join(w[:4] for w in s.replace("&", "").replace("-", " ").split())


class Camp:
    __slots__ = ("id", "client", "market", "type", "cfg", "line", "share", "start", "end", "q_ctr", "q_cvr",
                 "creatives", "next_launch", "products")


camps = []
for c in CLIENTS:
    since = max(START, dt.date.fromisoformat(c["since"]))
    for tname, spec in c["types"].items():
        share, mkts, tstart = (spec, None, None) if isinstance(spec, float) else (
            spec + (None,) * (3 - len(spec)))
        cfg = CT[tname]
        lines = c["lines"] if cfg.get("per_line") else [("All Products", 1.0)]
        for m, _ in c["markets"]:
            if mkts and m not in mkts:
                continue
            for line, lw in lines:
                k = Camp()
                k.id = platform_id()
                k.client, k.market, k.type, k.cfg, k.line = c, m, tname, cfg, line
                k.share = share * lw
                k.start = max(since, cfg.get("start", START), tstart or START)
                k.end = cfg.get("end", dt.date(2099, 12, 31))
                k.q_ctr, k.q_cvr = lognorm(0.15), lognorm(0.15)
                k.creatives, k.next_launch, k.products = [], k.start, None
                camps.append(k)

for k in camps:
    c, cfg = k.client, k.cfg
    name = f"{c['code']}_{k.market}_{cfg['code']}" + ("" if k.line == "All Products" else f"_{LINE_CODE(k.line)}")
    status = "Active" if k.end > END else "Removed (migrated to PMax)"
    obj = "Leads" if (c["id"] == "autonova" and cfg["funnel"] != "Awareness") else cfg["obj"]
    W.row("campaigns", [k.id, name, c["id"], cfg["p"], k.market, k.type, cfg["ch"], cfg["funnel"], obj,
                        yn(cfg["brand"]), k.line, cfg["bid"], k.start.isoformat(),
                        k.end.isoformat() if k.end <= END else NA_DATE, status, c["id"]])

# non-paid "campaigns" for organic / direct CRM leads
SV_PRO_MARKETS = ["FR", "DE", "ES", "IT", "GB"]
NONPAID = {("autonova", "FR"): "AN-FR-NONPAID"}
NONPAID.update({("secondevie", m): f"SV-{m}-NONPAID" for m in SV_PRO_MARKETS})
for (cid, m), npid in NONPAID.items():
    W.row("campaigns", [npid, f"{CL[cid]['code']}_{m}_NonPaid_OrganicDirect", cid, "non_paid", m,
                        "Non-paid (Organic / Direct)", "Organic & Direct", "N/A", "Leads", "No", "All Products", NA,
                        START.isoformat(), NA_DATE, "Always on", cid])

# ---------------------------------------------------------------------------
# Products (feed)
# ---------------------------------------------------------------------------
PRODUCT_CATALOG = {
    "secondevie": {
        "Smartphones": [("Apple", m, p) for m, p in [("iPhone 13", 389), ("iPhone 14", 459), ("iPhone 15", 579),
                        ("iPhone 15 Pro", 749), ("iPhone 16", 699), ("iPhone 12", 299)]] +
                       [("Samsung", m, p) for m, p in [("Galaxy S23", 419), ("Galaxy S24", 529), ("Galaxy A54", 219)]] +
                       [("Google", m, p) for m, p in [("Pixel 8", 359), ("Pixel 9", 489)]],
        "Laptops": [("Apple", "MacBook Air M1", 599), ("Apple", "MacBook Air M2", 799), ("Apple", "MacBook Pro 14 M3", 1349),
                    ("Dell", "XPS 13", 649), ("Lenovo", "ThinkPad T14", 459), ("HP", "EliteBook 840 G8", 429)],
        "Tablets": [("Apple", "iPad 9", 239), ("Apple", "iPad 10", 319), ("Apple", "iPad Air 5", 449),
                    ("Apple", "iPad Pro 11", 629), ("Samsung", "Galaxy Tab S9", 459)],
        "Gaming Consoles": [("Sony", "PlayStation 5", 399), ("Nintendo", "Switch OLED", 259), ("Microsoft", "Xbox Series X", 379),
                            ("Microsoft", "Xbox Series S", 219), ("Valve", "Steam Deck OLED", 459)],
        "Smartwatches & Audio": [("Apple", "Apple Watch Series 9", 289), ("Apple", "AirPods Pro 2", 169),
                                 ("Samsung", "Galaxy Watch 6", 159), ("Sony", "WH-1000XM5", 219)],
    },
}
VARIANTS = {
    "secondevie": ["128 Go - Très bon état", "256 Go - Parfait état", "64 Go - Bon état", "128 Go - Bon état",
                   "512 Go - Parfait état", "Standard - Très bon état"],
}
products_by_client = defaultdict(list)
for c in CLIENTS:
    if not c["products"]:
        continue
    cat = PRODUCT_CATALOG[c["id"]]
    pool = [(line, b, n, p) for line, items in cat.items() for b, n, p in items]
    seen = set()
    n = 0
    while n < c["products"]:
        line, b, base, price = rng.choice(pool)
        var = rng.choice(VARIANTS[c["id"]])
        if (base, var) in seen:
            continue
        seen.add((base, var))
        n += 1
        pid = f"{c['code']}-P{n:04d}"
        title = f"{base} - {var}" if c["id"] != "secondevie" else f"{b} {base} - {var}"
        if c["id"] == "secondevie":
            cond = "Refurbished - " + var.split(" - ")[1]
            pr = price * {"Parfait état": 1.12, "Très bon état": 1.0, "Bon état": 0.9}[var.split(" - ")[1]]
            pr *= {"64": 0.9, "128": 1.0, "256": 1.12, "512": 1.28}.get(var.split()[0], 1.0)
        else:
            cond, pr = "New", price * {"100 ml": 1.6, "200 ml": 1.9, "30 ml": 0.75, "Format voyage": 0.45}.get(var, 1.0)
        launch = START if rng.random() < 0.7 else START + dt.timedelta(days=rng.randint(30, SPAN - 60))
        launch = max(launch, dt.date.fromisoformat(c["since"]))
        opt_date = SV_SMARTFEEDS if c["id"] == "secondevie" else None
        optimized = opt_date is not None and rng.random() < 0.7
        sub = base.split(" ")[0] if c["id"] != "secondevie" else b
        prod = dict(id=pid, line=line, price=r2(pr), pop=0.0, cvr_q=lognorm(0.25), launch=launch,
                    opt=opt_date if optimized else None)
        products_by_client[c["id"]].append(prod)
        W.row("products", [pid, f"{c['code']}{rng.randint(100000, 999999)}", title, b, line, sub, cond, prod["price"],
                           round(min(0.85, max(0.05, c["margin"] * lognorm(0.15))), 4), launch.isoformat(),
                           yn(optimized), opt_date.isoformat() if optimized else NA_DATE, c["id"]])
    plist = products_by_client[c["id"]]
    ranks = list(range(1, len(plist) + 1))
    rng.shuffle(ranks)
    for prod, rk in zip(plist, ranks):
        prod["pop"] = 1.0 / rk ** 0.8

for k in camps:
    if k.cfg["kind"] in SHOPPING_KINDS and products_by_client.get(k.client["id"]):
        pl = products_by_client[k.client["id"]]
        k.products = [p for p in pl if k.line == "All Products" or p["line"] == k.line]

# ---------------------------------------------------------------------------
# CRM (shared "CRM & Offline Sales" data product): business locations + leads
#   AutoNova: B2C dealer leads (test drive -> sale)   Seconde Vie Pro: B2B device-fleet leads (quote -> won deal)
# ---------------------------------------------------------------------------
DEALERS = [
    ("Lyon Est", "Flagship", "Lyon", "Auvergne-Rhône-Alpes", "69003", 45.760300, 4.859700, 0.16),
    ("Lyon Nord - Villeurbanne", "Showroom", "Villeurbanne", "Auvergne-Rhône-Alpes", "69100", 45.771900, 4.890200, 0.11),
    ("Grenoble", "Showroom", "Grenoble", "Auvergne-Rhône-Alpes", "38000", 45.188500, 5.724500, 0.11),
    ("Saint-Étienne", "Showroom", "Saint-Étienne", "Auvergne-Rhône-Alpes", "42000", 45.439700, 4.387200, 0.09),
    ("Clermont-Ferrand", "Showroom", "Clermont-Ferrand", "Auvergne-Rhône-Alpes", "63000", 45.777200, 3.087000, 0.09),
    ("Annecy", "Showroom", "Annecy", "Auvergne-Rhône-Alpes", "74000", 45.899200, 6.129400, 0.08),
    ("Chambéry", "Showroom", "Chambéry", "Auvergne-Rhône-Alpes", "73000", 45.564600, 5.917800, 0.06),
    ("Valence", "Showroom", "Valence", "Auvergne-Rhône-Alpes", "26000", 44.933400, 4.892400, 0.07),
    ("Vienne", "Used Car Center", "Vienne", "Auvergne-Rhône-Alpes", "38200", 45.525300, 4.874300, 0.05),
    ("Bourg-en-Bresse", "Showroom", "Bourg-en-Bresse", "Auvergne-Rhône-Alpes", "01000", 46.205200, 5.225500, 0.05),
    ("Dijon", "Showroom", "Dijon", "Bourgogne-Franche-Comté", "21000", 47.322000, 5.041500, 0.09),
    ("Mâcon", "Used Car Center", "Mâcon", "Bourgogne-Franche-Comté", "71000", 46.306900, 4.828700, 0.04),
]
an_pick, sv_office = [], {}
for i, (nm, typ, city, reg, zp, lat, lon, w) in enumerate(DEALERS, 1):
    lid = f"AN-D{i:02d}"
    W.row("business_locations", [lid, f"AutoNova {nm}", f"Dealership - {typ}", city, reg, "France", zp, lat, lon,
                                 "autonova"])
    an_pick.append((lid, w))
for m in SV_PRO_MARKETS:
    city = {"FR": "Paris", "DE": "Berlin", "ES": "Madrid", "IT": "Milan", "GB": "London"}[m]
    lat, lon = {"IT": (45.464200, 9.190000)}.get(m, MARKETS[m][6:8])
    sv_office[m] = f"SV-PRO-{m}"
    W.row("business_locations", [sv_office[m], f"Seconde Vie Pro - {city}", "B2B Sales Office", city, MARKETS[m][1],
                                 MARKETS[m][0], NA, lat, lon, "secondevie"])

VEHICLES = {
    "New Cars": [("Peugeot", "208", "City Car", "Petrol", 21500), ("Peugeot", "3008", "SUV", "Hybrid", 36500),
                 ("Renault", "Clio", "City Car", "Petrol", 20500), ("Renault", "Austral", "SUV", "Hybrid", 35000),
                 ("Citroën", "C3 Aircross", "SUV", "Petrol", 24000), ("Dacia", "Duster", "SUV", "Petrol", 22000),
                 ("Toyota", "Yaris Cross", "SUV", "Hybrid", 28500)],
    "Used Cars": [("Peugeot", "308 (used)", "Compact", "Diesel", 16500), ("Renault", "Captur (used)", "SUV", "Petrol", 15500),
                  ("Volkswagen", "Golf (used)", "Compact", "Petrol", 17500), ("Dacia", "Sandero (used)", "City Car", "Petrol", 9900),
                  ("Toyota", "C-HR (used)", "SUV", "Hybrid", 21000)],
    "Electric & Hybrid": [("Renault", "5 E-Tech", "City Car", "Electric", 30000),
                          ("Peugeot", "e-2008", "SUV", "Electric", 36000), ("MG", "MG4", "Compact", "Electric", 32000),
                          ("Kia", "EV3", "SUV", "Electric", 36000), ("Renault", "Scenic E-Tech", "SUV", "Electric", 40000)],
    "Utility Vans": [("Renault", "Kangoo Van", "Van", "Diesel", 26000), ("Peugeot", "Expert", "Van", "Diesel", 34000),
                     ("Citroën", "Berlingo Van", "Van", "Diesel", 25000), ("Renault", "Master", "Van", "Diesel", 40000)],
}
AN_LEAD_TYPES = [("Test Drive Request", .34), ("Quote Request", .30), ("Trade-in Valuation", .14),
                 ("Callback Request", .14), ("Financing Simulation", .08)]
SV_LEAD_TYPES = [("Fleet Quote Request", .45), ("Contact Sales", .25), ("Device Buy-back (Trade-in)", .15),
                 ("Demo / Discovery Call", .15)]
SV_COMPANY = [("SMB (10-49 employees)", .6, 10, 49), ("Mid-market (50-249)", .3, 50, 249), ("Enterprise (250+)", .1, 250, 900)]
lead_seq = [0]


def emit_leads(cid, camp_id, plat, line, market, d, n):
    """CRM leads for client `cid` coming from campaign `camp_id` (platform `plat`) on day d."""
    for _ in range(n):
        lead_seq[0] += 1
        if cid == "autonova":
            lid = f"AN-L{lead_seq[0]:07d}"
            if line == "All Products":
                line = wchoice(CL["autonova"]["lines"])
            brand, model, seg, variant, price = rng.choice(VEHICLES[line])
            name = f"{brand} {model}"
            ltype = wchoice(AN_LEAD_TYPES)
            loc = wchoice(an_pick)
            if line == "Used Cars" and rng.random() < 0.5:
                loc = rng.choice(["AN-D09", "AN-D12"])
            if plat in ("google_ads", "microsoft_ads"):      # SmartConversion: value-based bidding on sold cars
                q = 0.36 + 0.14 * ramp(d, AN_SMARTCONV, 90)
            elif plat == "meta_ads":
                q = 0.22 + 0.08 * ramp(d, AN_META_CAPI, 90)
            else:
                q = 0.45 if plat == "non_paid" else 0.25
            p_opp, p_won, p_won_noopp = (0.30 if line == "Utility Vans" else 0.48), 0.27, 0.05
            opp_type, opp_days, close_days = "Test Drive", (2, 14), (3, 30)
            won_status, opp_open = "Sold", "Open - Test Drive Scheduled"
            lost = [("Lost - Bought Elsewhere", .55), ("Lost - Financing Refused", .15), ("Lost - No Answer", .30)]
            hours_med = 3.5 - 1.5 * ramp(d, AN_SMARTCONV, 120)
            oci_from, margin = AN_SMARTCONV, (0.06, 0.11)
            existing = rng.random() < 0.28
        else:   # secondevie - Seconde Vie Pro (B2B)
            lid = f"SV-L{lead_seq[0]:07d}"
            if line not in ("Laptops", "Smartphones", "Tablets"):
                line = wchoice([("Laptops", .65), ("Smartphones", .25), ("Tablets", .10)])
            brand, model, unit = rng.choice(PRODUCT_CATALOG["secondevie"][line])
            seg, _, lo, hi = SV_COMPANY[[x[0] for x in SV_COMPANY].index(wchoice([(x[0], x[1]) for x in SV_COMPANY]))]
            units = rng.randint(lo, hi)
            variant = f"{units} devices"
            price = units * unit * 0.9
            name = f"{brand} {model}"
            ltype = wchoice(SV_LEAD_TYPES)
            loc = sv_office[market]
            q = 0.42 if plat != "non_paid" else 0.50
            p_opp, p_won, p_won_noopp = 0.65, 0.32, 0.03
            opp_type, opp_days, close_days = "Quote Sent", (1, 7), (7, 45)
            won_status, opp_open = "Won", "Open - Quote Sent"
            lost = [("Lost - Price", .40), ("Lost - No Decision", .35), ("Lost - Competitor", .25)]
            hours_med = 6.0
            oci_from, margin = SV_PRO_OCI, (0.15, 0.22)
            existing = rng.random() < 0.18
        hours = r2(min(240.0, rng.lognormvariate(math.log(hours_med), 0.9)))
        contacted = d + dt.timedelta(days=int(hours // 24))
        is_q = rng.random() < q
        opp_date = won_date = None
        if not is_q:
            status = wchoice([("Disqualified - Duplicate", .35), ("Disqualified - Spam / Invalid", .25),
                              ("Lost - No Answer", .40)])
        else:
            if rng.random() < p_opp:
                opp_date = d + dt.timedelta(days=rng.randint(*opp_days))
            if rng.random() < (p_won if opp_date else p_won_noopp):
                won_date = (opp_date or d) + dt.timedelta(days=rng.randint(*close_days))
            if won_date and won_date <= END:
                status = won_status
            elif opp_date and opp_date > END:
                status, opp_date, won_date = opp_open, None, None
            elif won_date:
                status, won_date = "Open - Negotiation", None
            else:
                status = "Open - Negotiation" if (END - d).days < 30 else wchoice(lost)
        if contacted > END:
            status, is_q, opp_date, won_date = "New", False, None, None
        won = status == won_status
        val = r2(price * rng.uniform(0.92, 1.04)) if won else 0.0
        gp = r2(val * rng.uniform(*margin)) if won else 0.0
        uploaded = won and won_date >= oci_from and plat in ("google_ads", "microsoft_ads", "meta_ads")
        W.row("crm_leads", [lid, camp_id, loc, d.isoformat(), ltype, brand, name, line, seg, variant, yn(existing),
                            status, contacted.isoformat() if status != "New" else NA_DATE,
                            hours if status != "New" else 0.0, opp_type,
                            opp_date.isoformat() if opp_date else NA_DATE,
                            won_date.isoformat() if won else NA_DATE, (won_date - d).days if won else 0, val, gp,
                            yn(uploaded), int(is_q), int(opp_date is not None and opp_date <= END), int(won), cid])


# ---------------------------------------------------------------------------
# Creatives (social)
# ---------------------------------------------------------------------------
FORMATS = {
    "meta_ads": [("Static Image", .30, 0.90, False), ("Carousel", .20, 1.05, False), ("Reels Video", .30, 1.08, True),
                 ("UGC Video", .15, 1.25, True), ("Collection", .05, 1.00, False)],
    "meta_lead": [("Lead Form - Image", .5, 0.95, False), ("Lead Form - Video", .5, 1.10, True)],
    "tiktok_ads": [("UGC Video", .55, 1.25, True), ("Spark Ad (Creator)", .30, 1.20, True),
                   ("Short Video", .15, 1.05, True)],
    "linkedin_ads": [("Single Image Ad", .5, 1.0, False), ("Document Ad", .2, 1.1, False), ("Video Ad", .3, 1.05, True)],
    "pinterest_ads": [("Static Pin", .5, 0.95, False), ("Video Pin", .2, 1.10, True),
                      ("Carousel Pin", .15, 1.05, False), ("Collection", .15, 1.0, False)],
}
THEMES = [("Product Showcase", .30), ("Promo / Offer", .20), ("Brand Story", .12), ("Testimonial / Review", .18),
          ("Seasonal", .10), ("How-to / Tutorial", .10)]
creative_seq = [0]


def launch_creative(k, d):
    creative_seq[0] += 1
    fmts = FORMATS["meta_lead" if k.type == "Meta - Lead Ads" else k.cfg["p"]]
    fmt = wchoice([(f, w) for f, w, _, _ in fmts])
    _, _, fm, vid = next(x for x in fmts if x[0] == fmt)
    theme = wchoice(THEMES)
    prod = wchoice([("In-house Studio", .55), ("UGC Creator", .25), ("Agency Design", .20)] +
                   ([("AI-generated (Arcane AI Lab)", .35)] if d >= dt.date(2025, 6, 1) else []))
    q = lognorm(0.30) * fm * (1.06 if prod.startswith("AI") else 1.0) * (1.1 if prod == "UGC Creator" else 1.0)
    cr = dict(id=f"{k.client['code']}-CR{creative_seq[0]:06d}", fmt=fmt, theme=theme, prod=prod, vid=vid, q=q,
              launch=d, life=rng.randint(28, 100), last=None)
    cr["name"] = (f"{k.client['code']}_{k.market}_{fmt.split(' ')[0]}_{theme.split(' ')[0].replace('/', '')}_"
                  f"{d:%y%m%d}_v{rng.randint(1, 4)}")
    k.creatives.append(cr)
    k.next_launch = d + dt.timedelta(days=rng.randint(10, 24))
    return cr


# ---------------------------------------------------------------------------
# Daily simulation -> ad_performance_daily, creative_performance_daily (+ accumulators)
# ---------------------------------------------------------------------------
web_paid = defaultdict(lambda: [0, 0.0, 0.0])            # (client, market, date, channel) -> clicks, trans, revenue
spend_actual = defaultdict(float)                         # (client, platform, market, month)
spend_plan = defaultdict(float)                           # unconstrained (what the media plan wanted)
type_daily = defaultdict(lambda: [0.0, 0.0, 0.0])         # (client, market, type, date) -> spend, conv, value
prod_week = defaultdict(lambda: [0, 0, 0.0, 0.0, 0.0])    # (camp, week) -> impr, clicks, cost, conv, value

camps_by_cm = defaultdict(list)
for k in camps:
    camps_by_cm[(k.client["id"], k.market)].append(k)


def write_perf(k, d, dev, impr, clicks, cost, conv, val, vv, eng, search):
    fx = MARKETS[k.market][3]
    si, se, slb, slr = search
    W.row("ad_performance_daily", [f"{k.id}-{d:%Y%m%d}-{dev[:2].upper()}", k.id, d.isoformat(), dev, impr, clicks,
                                   r2(cost), r2(cost * fx), r2(conv), r2(val), vv, eng, si, se, slb, slr,
                                   k.client["id"]])


def creative_day(k, d, spend, cpc, ctr, cvr, aov, conv_factor):
    """Split a social campaign's day across its active creatives; returns campaign totals."""
    act = [cr for cr in k.creatives if cr["launch"] <= d and (d - cr["launch"]).days < cr["life"]]
    while len(act) < 2 or d >= k.next_launch:
        act.append(launch_creative(k, d))
        if len(act) >= 2 and d < k.next_launch:
            break
    fat = [max(0.45, 1 - (d - cr["launch"]).days / 120) for cr in act]
    ws = [(cr["q"] * f) ** 1.5 for cr, f in zip(act, fat)]
    sps = split_money(spend, ws)
    cpm = cpc * ctr * 1000
    tot = [0, 0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0]   # impr, clicks, cost, vv3, thru, eng, conv, value, conv_true
    for cr, f, sp in zip(act, fat, sps):
        impr = cnt(sp / (cpm * lognorm(0.08)) * 1000)
        clicks = min(impr, cnt(impr * ctr * cr["q"] ** 0.5 * f))
        conv_true = r2(cnt(clicks * cvr * cr["q"] ** 0.3) * rng.uniform(0.93, 1.0))
        conv = r2(conv_true * conv_factor)
        val = r2(conv * aov * lognorm(0.15))
        vv = cnt(impr * 0.26 * cr["q"] ** 0.5) if cr["vid"] else 0
        thru = cnt(vv * 0.24) if cr["vid"] else 0
        eng = cnt(impr * 0.009 * cr["q"])
        cr["last"] = d
        if impr == 0 and sp == 0:
            continue
        W.row("creative_performance_daily", [f"{cr['id']}-{d:%Y%m%d}", cr["id"], d.isoformat(), impr, clicks, r2(sp),
                                             vv, thru, eng, conv, val, k.client["id"]])
        for i, v in enumerate((impr, clicks, sp, vv, thru, eng, conv, val, conv_true)):
            tot[i] += v
    return tot


for c in CLIENTS:
    cid, vert = c["id"], c["vert"]
    for d in DAYS:
        s = season(vert, d)
        wk = WEEKDAY[c["wk"]][d.weekday()]
        years = (d - START).days / 365.25
        base = c["budget"] * (1 + c["growth"]) ** years / 30.4 * wk
        p = progress(d)
        for m, mw in c["markets"]:
            act = [k for k in camps_by_cm[(cid, m)] if k.start <= d <= k.end]
            if not act:
                continue
            tot_share = sum(k.share for k in act)
            mcpc = MARKETS[m][8]
            for k in act:
                cfg = k.cfg
                kind = cfg["kind"]
                s_k = 1 + (s - 1) * (0.5 if cfg["funnel"] == "Awareness" else 1.0)
                if kind == "retail" and d.year in PRIME_DAY:
                    pd0, pdn = PRIME_DAY[d.year]
                    if pd0 - dt.timedelta(days=3) <= d < pd0 + dt.timedelta(days=pdn):
                        s_k *= 2.4
                if cid == "autonova" and k.type == "DV360 - Online Video" and any(a <= d <= b for a, b in MONDIAL_AUTO):
                    s_k *= 2.5
                plan = base * mw * k.share / tot_share * s_k
                spend_factor, ctr_f, cvr_f, conv_factor, lb = 1.0, 1.0, 1.0, 1.0, cfg.get("lb", 0.0)
                if cid == "secondevie" and m == "DE" and k.type == "Search - Generic" and d >= SV_DE_CAP:
                    spend_factor, lb = 0.58, 0.42
                if cid == "routeo" and cfg["p"] == "meta_ads" and RT_META_OUTAGE[0] <= d <= RT_META_OUTAGE[1]:
                    conv_factor = 0.07
                if kind in ("shopping", "pmax") and cid == "secondevie" and d >= SV_SMARTFEEDS:
                    ctr_f, cvr_f = 1.12, 1.04
                spend = plan * spend_factor * lognorm(0.10)
                cpc = cfg["cpc"] * c["cpc"] * mcpc * (1 + 0.06 * years) * (1 + 0.15 * (s - 1)) * lognorm(0.06)
                ctr = cfg["ctr"] * k.q_ctr * ctr_f * lognorm(0.05)
                cvr = (cfg["cvr"] * c["cvr"] * k.q_cvr * cvr_f * (1 + 0.04 * years) *
                       max(0.7, 1 + 0.25 * (s - 1)) * lognorm(0.08))
                aov = c["aov"] * cfg["vm"]
                if cid == "autonova":
                    aov = 120.0 if d < AN_SMARTCONV else 185.0       # value-based bidding after offline import
                ym = month_start(d)
                spend_actual[(cid, cfg["p"], m, ym)] += spend
                spend_plan[(cid, cfg["p"], m, ym)] += plan
                if kind == "social":
                    impr, clicks, cost, vv3, thru, eng, conv, val, conv_true = creative_day(
                        k, d, spend, cpc, ctr, cvr, aov, conv_factor)
                    devs = DEVICES["social"]
                    wts = [w for _, w, _, _ in devs]
                    for (dev, _, _, _), i_, c_, co, cv, va, v_, e_ in zip(
                            devs, split_int(impr, wts), split_int(clicks, wts), split_money(cost, wts),
                            split_money(conv, wts), split_money(val, wts), split_int(vv3, wts), split_int(eng, wts)):
                        if i_ == 0 and co == 0:
                            continue
                        write_perf(k, d, dev, i_, c_, co, cv, va, v_, e_, (0, 0, 0, 0))
                    tot_clicks, tot_conv_true, tot_val_true = clicks, conv_true, conv_true * aov
                    tot_cost, tot_conv, tot_val = cost, conv, val
                    impr_tot = impr
                else:
                    tot_clicks = tot_cost = tot_conv = tot_val = impr_tot = tot_conv_true = 0
                    for dev, w, dctr, dcvr in DEVICES[kind]:
                        sp = spend * w
                        clicks = cnt(sp / (cpc * (0.85 if dev == "Mobile" else 1.0)))
                        impr = max(clicks, cnt(clicks / (ctr * dctr)))
                        conv_true = r2(cnt(clicks * cvr * dcvr) * rng.uniform(0.93, 1.0))
                        conv = r2(conv_true * conv_factor)
                        val = r2(conv * aov * lognorm(0.15))
                        vv = cnt(impr * (0.32 if cfg["p"] == "google_ads" else 0.62)) if kind == "video" else 0
                        eng = cnt(impr * 0.004) if kind == "video" else 0
                        if cfg.get("is_"):
                            lb_k = lb * lognorm(0.2)
                            is_ = min(cfg["is_"] * lognorm(0.05) * (1 - 0.08 * max(0, s - 1)) * spend_factor,
                                      0.97 - lb_k)
                            elig = cnt(impr / is_) if impr else 0
                            lost_b = int(elig * lb_k)
                            search = (impr, elig, lost_b, max(0, elig - impr - lost_b))
                        else:
                            search = (0, 0, 0, 0)
                        if impr == 0 and sp < 0.005:
                            continue
                        write_perf(k, d, dev, impr, clicks, sp, conv, val, vv, eng, search)
                        tot_clicks += clicks
                        tot_cost += sp
                        tot_conv += conv
                        tot_val += val
                        impr_tot += impr
                        tot_conv_true += conv_true
                    tot_val_true = tot_val / conv_factor if conv_factor else tot_val
                td_ = type_daily[(cid, m, k.type, d)]
                td_[0] += tot_cost
                td_[1] += tot_conv
                td_[2] += tot_val
                if k.products:
                    pw = prod_week[(k, week_start(d))]
                    pw[0] += impr_tot
                    pw[1] += tot_clicks
                    pw[2] += tot_cost
                    pw[3] += tot_conv
                    pw[4] += tot_val
                if kind != "retail":
                    wp = web_paid[(cid, m, d, cfg["ch"])]
                    wp[0] += tot_clicks
                    if cid == "autonova" or cfg["obj"] != "Leads":   # B2B lead forms are not web shop orders
                        wp[1] += tot_conv_true / cfg["attr"]
                        wp[2] += tot_val_true / cfg["attr"]
                if cid == "autonova":
                    emit_leads(cid, k.id, cfg["p"], k.line, m, d, cnt(tot_conv_true / 1.12))
                elif cfg["obj"] == "Leads":          # Seconde Vie Pro B2B lead-gen campaigns -> CRM
                    emit_leads(cid, k.id, cfg["p"], k.line, m, d, cnt(tot_conv_true / cfg["attr"]))
        if cid == "autonova":
            emit_leads(cid, NONPAID[(cid, "FR")], "non_paid", "All Products", "FR", d, cnt(26 * s * wk * (1 + c["growth"]) ** years))
        elif cid == "secondevie":
            for m in SV_PRO_MARKETS:
                emit_leads(cid, NONPAID[(cid, m)], "non_paid", "All Products", m, d,
                           cnt(1.6 * dict(c["markets"])[m] / 0.38 * wk * (0.4 + 0.6 * progress(d))))

# creatives dimension (after simulation so end dates are known)
for k in camps:
    for cr in k.creatives:
        end = cr["launch"] + dt.timedelta(days=cr["life"] - 1)
        active = end >= END and k.end > END
        W.row("creatives", [cr["id"], cr["name"], k.id, cr["fmt"], cr["theme"], cr["prod"], yn(cr["vid"]),
                            cr["launch"].isoformat(), NA_DATE if active else min(end, END).isoformat(),
                            "Active" if active else "Paused", k.client["id"]])

# ---------------------------------------------------------------------------
# Product performance (weekly split of shopping / PMax / Amazon campaigns)
# ---------------------------------------------------------------------------
for (k, wk), (im, cl, co, cv, va) in prod_week.items():
    prods = [p for p in k.products if p["launch"] <= wk + dt.timedelta(days=6)]
    if not prods or (im == 0 and co == 0):
        continue
    boost = [1.25 if (p["opt"] and wk >= p["opt"]) else 1.0 for p in prods]
    pw = [p["pop"] * lognorm(0.15) for p in prods]
    cw = [a * b for a, b in zip(pw, boost)]
    vw = [a * p["cvr_q"] for a, p in zip(cw, prods)]
    xw = [a * p["price"] for a, p in zip(vw, prods)]
    for p, i_, c_, co_, cv_, va_ in zip(prods, split_int(im, pw), split_int(cl, cw), split_money(co, cw),
                                        split_money(cv, vw), split_money(va, xw)):
        if i_ == 0 and c_ == 0 and co_ == 0:
            continue
        W.row("product_performance_weekly", [f"{p['id']}-{k.id}-{wk:%Y%m%d}", p["id"], k.id, wk.isoformat(),
                                             max(i_, c_), c_, co_, cv_, va_, k.client["id"]])

# ---------------------------------------------------------------------------
# Web analytics (GA4 + backend orders): paid channels de-duplicated, non-paid channels incl. AI assistants
# ---------------------------------------------------------------------------
NONPAID = [("Organic Search", .46, 1.0, .45), ("Direct", .28, 1.3, .20), ("Email & CRM", .09, 1.8, .05),
           ("Referral", .06, 0.9, .40), ("Affiliates", .06, 2.0, .35), ("Organic Social", .05, 0.5, .60)]
NEW_SHARE = {"Paid Search": .45, "Paid Shopping": .55, "Paid Social": .70, "Paid Video & Display": .75}
for c in CLIENTS:
    cid = c["id"]
    since = max(START, dt.date.fromisoformat(c["since"]))
    for d in DAYS:
        if d < since:
            continue
        s = 1 + (season(c["vert"], d) - 1) * 0.7
        years = (d - START).days / 365.25
        ai_share = 0.001 + 0.034 * progress(d) ** 1.8
        for m, mw in c["markets"]:
            rows = []
            for ch in ("Paid Search", "Paid Shopping", "Paid Social", "Paid Video & Display"):
                if (cid, m, d, ch) not in web_paid:
                    continue
                cl, tr, rev = web_paid[(cid, m, d, ch)]
                rows.append((ch, "Yes", cnt(cl * 0.87), tr, rev, NEW_SHARE[ch]))
            base = c["organic"] * mw * s * (1 + c["growth"] * 0.6) ** years * WEEKDAY[c["wk"]][d.weekday()]
            for ch, sh, cvm, new in NONPAID:
                if ch == "Organic Search":
                    sh -= ai_share
                ses = cnt(base * sh * lognorm(0.08))
                tr = ses * c["web_cvr"] * cvm * lognorm(0.1)
                rows.append((ch, "No", ses, tr, tr * c["aov"] * lognorm(0.1), new))
            ses = cnt(base * ai_share * lognorm(0.15))
            tr = ses * c["web_cvr"] * 1.7 * lognorm(0.15)
            rows.append(("AI Assistants (ChatGPT, Perplexity, Gemini)", "No", ses, tr, tr * c["aov"] * 1.1, .55))
            for ch, paid, ses, tr, rev, new in rows:
                n_tr = cnt(tr)
                rev = r2(rev * n_tr / tr) if tr > 0 else 0.0
                if cid == "autonova":
                    trans, revenue, leads, margin, newc = 0, 0.0, n_tr, 0.0, 0
                else:
                    trans, revenue, leads = n_tr, rev, 0
                    margin = r2(rev * c["margin"] * lognorm(0.05))
                    newc = cnt(n_tr * new)
                    newc = min(newc, n_tr)
                W.row("web_analytics_daily", [f"{cid}-{m}-{d:%Y%m%d}-{ch[:12].replace(' ', '')}", cid, m, d.isoformat(),
                                              ch, paid, ses, cnt(ses * 0.62), cnt(ses * 0.52), trans, revenue, margin,
                                              newc, leads, cid])

# ---------------------------------------------------------------------------
# Media budgets (monthly plan per client x platform x market), incl. Dec 2026
# ---------------------------------------------------------------------------
NOV26 = dt.date(2026, 11, 1)
DEC26 = dt.date(2026, 12, 1)
nov_days_done = (END - NOV26).days + 1
for (cid, plat, m, ym), planned in sorted(spend_plan.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3])):
    c = CL[cid]
    tt, tv = c["target"]
    roas, cpa = (tv, 0.0) if tt == "ROAS" else (0.0, tv)
    months = [ym]
    if ym == NOV26:
        planned = planned / nov_days_done * 30
        months.append(DEC26)
    for mo in months:
        amt = planned * (season(c["vert"], dt.date(2026, 12, 8)) / season(c["vert"], dt.date(2026, 11, 8))
                         if mo == DEC26 else 1.0)
        amt = round(amt * lognorm(0.04) / 500) * 500
        W.row("media_budgets", [f"{cid}-{plat}-{m}-{mo:%Y%m}", cid, plat, m, mo.isoformat(), r2(max(amt, 500)),
                                roas, cpa, c["media"], cid])

# ---------------------------------------------------------------------------
# Incrementality tests (Arcane Data & Measurement practice)
# ---------------------------------------------------------------------------
TESTS = [
    ("secondevie", "meta_ads", "FR", "Meta - Retargeting", "Conversion Lift (platform holdout)", "2024-05-06", 28, 0.7,
     "Cut retargeting budget by 40%, move to Advantage+ Shopping"),
    ("secondevie", "google_ads", "FR", "Search - Brand", "Geo Holdout (brand search paused)", "2024-09-09", 21, 1.4,
     "Keep brand search on competitor-conquested terms only"),
    ("secondevie", "google_ads", "DE", "Performance Max", "Geo-lift (synthetic control)", "2025-04-07", 35, 3.1,
     "Scale PMax DE +25% while iROAS > 2.5"),
    ("secondevie", "tiktok_ads", "FR", "TikTok - Spark Ads", "Geo-lift (synthetic control)", "2025-10-06", 28, 2.2,
     "Keep TikTok as always-on prospecting channel"),
    ("secondevie", "amazon_ads", "DE", "Amazon - Sponsored Products", "Geo-lift (synthetic control)", "2026-02-02", 28,
     1.6, "Maintain; focus on consoles & tablets ASINs"),
    ("secondevie", "google_ads", "GB", "Search - Generic", "Geo-lift (synthetic control)", "2026-11-02", 28, 2.6,
     "Results expected early December"),
    ("routeo", "google_ads", "ES", "Search - Brand", "Geo Holdout (brand search paused)", "2025-05-05", 21, 0.4,
     "Reduce brand bids in ES; keep defensive coverage on aggregator terms"),
    ("routeo", "google_ads", "FR", "YouTube", "Brand Lift + Geo-lift", "2026-03-02", 42, 1.1,
     "Keep YouTube for spring booking season only"),
    ("autonova", "meta_ads", "FR", "Meta - Lead Ads", "Geo-lift on sold cars (CRM)", "2025-06-02", 42, 1.8,
     "Optimise Meta on qualified leads via CAPI"),
    ("autonova", "dv360", "FR", "DV360 - Online Video", "Geo-lift on sold cars (CRM)", "2024-10-07", 28, 0.9,
     "Use DV360 only around Mondial de l'Auto"),
]
for i, (cid, plat, m, typ, meth, start, days, iroas, rec) in enumerate(TESTS, 1):
    c = CL[cid]
    s0 = dt.date.fromisoformat(start)
    e0 = s0 + dt.timedelta(days=days - 1)
    rng_days = [s0 + dt.timedelta(days=j) for j in range(days) if s0 + dt.timedelta(days=j) <= END]
    sp = sum(type_daily[(cid, m, typ, x)][0] for x in rng_days)
    pc = sum(type_daily[(cid, m, typ, x)][1] for x in rng_days)
    running = e0 > END
    pv = sum(type_daily[(cid, m, typ, x)][2] for x in rng_days)
    platform_roas = pv / sp if sp else 1.0
    if cid == "autonova":                 # iROAS on CRM gross profit, not on lead value
        platform_roas = 2400.0 * 0.12 * pc / sp if sp else 1.0
    factor = min(0.95, iroas / platform_roas) if platform_roas else 0.0   # share of platform conv. that is incremental
    inc_conv = pc * factor
    inc_rev = sp * iroas
    conf = 0.97 if iroas > 1.5 else (0.78 if 0.8 < iroas < 1.0 else 0.92)
    lift = 100 * factor * rng.uniform(0.15, 0.35)
    W.row("incrementality_tests", [f"IT-{i:03d}", cid, plat, m, f"{c['code']} {m} {typ} - {meth.split(' (')[0]}", typ,
                                   meth, s0.isoformat(), e0.isoformat(), "Running" if running else "Completed",
                                   r2(sp), r2(pc), 0.0 if running else r2(inc_conv), 0.0 if running else r2(inc_rev),
                                   0.0 if running else r2(lift), 0.0 if running else iroas,
                                   0.0 if running else conf, "No" if running or conf < 0.9 else "Yes",
                                   "Pending" if running else rec, cid])

# ---------------------------------------------------------------------------
# Data requests (the current "always-on data support loop": Google Form -> project tool -> consultant)
# ---------------------------------------------------------------------------
REQ_TYPES = [
    ("New KPI / metric", .20, 5, ["Add {kpi} to the main dashboard", "Show {kpi} split by {dim}",
                                  "Add {kpi} vs target to the overview page"]),
    ("New breakdown / filter", .18, 3, ["Add a {dim} filter on the performance page",
                                        "Break down {platform} results by {dim}"]),
    ("New data source", .07, 16, ["Connect {source} data to the dashboard", "Add {source} to the {market} report"]),
    ("Data discrepancy", .15, 6, ["{platform} conversions don't match {source} for {month}",
                                  "Cost in dashboard differs from {platform} UI for {market}"]),
    ("Ad-hoc deep dive", .20, 8, ["Why did {kpi} drop in {market} last week?",
                                  "Deep dive on {platform} performance in {market} for {month}",
                                  "Which products drive the {kpi} change in {market}?"]),
    ("Performance report (slides)", .14, 6, ["Monthly performance deck for {month}", "QBR slides for {month}",
                                             "Black Friday recap for {market}"]),
    ("Access request", .06, 1, ["Give dashboard access to a new team member on client side",
                                "Remove access for a former client employee"]),
]
KPIS = {"secondevie": ["ROAS", "GMV", "orders", "CPC", "impression share"], "autonova": ["CPL", "qualified leads",
        "cost per sold car", "test drives"], "routeo": ["CPA", "bookings", "booking value"]}
DIMS = ["market", "device", "campaign type", "product category", "funnel stage", "week"]
SOURCES = ["Shopify", "Salesforce CRM", "GA4", "Google Sheets (offline sales)", "Amazon Vendor Central", "Klaviyo"]
MONTHS_FR = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December"]
PLATFORM_NAME = {p[0]: p[1] for p in PLATFORMS}
req = 0
for c in CLIENTS:
    cid = c["id"]
    since = max(START, dt.date.fromisoformat(c["since"]))
    plats = sorted({CT[t]["p"] for t in c["types"]})
    mkts = [m for m, _ in c["markets"]]
    rate = 6.0 if c["tier"] == "Top Account" else 3.0
    mo = month_start(since)
    while mo <= END:
        for _ in range(poisson(rate * (1 + 0.25 * progress(mo)))):
            sub = mo + dt.timedelta(days=rng.randint(0, 27))
            if sub > END or sub < since:
                continue
            req += 1
            rt, _, effort, tmpls = REQ_TYPES[[x[0] for x in REQ_TYPES].index(wchoice([(x[0], x[1]) for x in REQ_TYPES]))]
            summ = rng.choice(tmpls).format(kpi=rng.choice(KPIS[cid]), dim=rng.choice(DIMS), platform=PLATFORM_NAME[rng.choice(plats)], source=rng.choice(SOURCES),
                market=rng.choice(mkts), month=f"{MONTHS_FR[(sub.month - 2) % 12]} {sub.year if sub.month > 1 else sub.year - 1}")
            prio = wchoice([("Low", .25), ("Medium", .5), ("High", .2), ("Urgent", .05)])
            q4 = 1.35 if sub.month in (10, 11, 12) else 1.0
            days = max(1, int(round(rng.lognormvariate(math.log((4.5 if c["tier"] == "Top Account" else 7.0) * q4 *
                                    {"Urgent": 0.35, "High": 0.7}.get(prio, 1.0)), 0.55))))
            if rt == "New data source":
                days += rng.randint(7, 20)
            deliv = sub + dt.timedelta(days=days)
            if rng.random() < 0.04:
                status, done = "Rejected", False
            elif deliv <= END:
                status, done = "Delivered", True
            else:
                status, done = ("In Progress" if rng.random() < 0.55 else "Backlog"), False
            W.row("data_requests", [f"DR-{req:05d}", cid, sub.isoformat(),
                                    wchoice([("Client", .45), ("Media Consultant", .55)]),
                                    wchoice([("Google Form", .7), ("Email", .2), ("Slack", .1)]), rt, summ, prio,
                                    c["data"] if rng.random() < 0.8 else rng.choice(DATA_CONSULTANTS), status,
                                    deliv.isoformat() if done else NA_DATE, days if done else 0,
                                    r2(effort * lognorm(0.4)), int(done), cid])
        mo = (mo + dt.timedelta(days=32)).replace(day=1)

# ---------------------------------------------------------------------------
# Data products (modules of the one shared model) + client entitlements -> object-level permissions
# ---------------------------------------------------------------------------
# LDM references (dataset -> referenced datasets). One shared model for every client.
REFS = {
    "platforms": [], "markets": [], "clients": [],
    "campaigns": ["clients", "platforms", "markets"],
    "ad_performance_daily": ["campaigns"],
    "creatives": ["campaigns"], "creative_performance_daily": ["creatives"],
    "products": [], "product_performance_weekly": ["products", "campaigns"],
    "web_analytics_daily": ["clients", "markets"],
    "business_locations": [], "crm_leads": ["campaigns", "business_locations"],
    "media_budgets": ["clients", "platforms", "markets"],
    "incrementality_tests": ["clients", "platforms", "markets"],
    "data_requests": ["clients"], "client_data_products": ["clients"],
}
SHARED_DIMS = ["clients", "platforms", "markets", "campaigns"]
CORE = "Paid Media Performance"
DATA_PRODUCTS = {  # name: (package, audience, datasets)
    CORE: ("Core", "Client + Arcane", ["ad_performance_daily"]),
    "Social Creatives": ("Standard", "Client + Arcane", ["creatives", "creative_performance_daily"]),
    "Web Analytics & GEO": ("Standard", "Client + Arcane", ["web_analytics_daily"]),
    "Budget & Pacing": ("Standard", "Client + Arcane", ["media_budgets"]),
    "Product Feed & Shopping": ("Premium add-on", "Client + Arcane", ["products", "product_performance_weekly"]),
    "CRM & Offline Sales": ("Premium add-on", "Client + Arcane", ["business_locations", "crm_leads"]),
    "Measurement & Incrementality": ("Premium add-on", "Client + Arcane", ["incrementality_tests"]),
    "Arcane Operations": ("Internal", "Arcane only", ["data_requests", "client_data_products"]),
}
ENTITLED = {   # client -> data products enabled (Core + Standard for everybody, add-ons per contract)
    "secondevie": ["Product Feed & Shopping", "CRM & Offline Sales", "Measurement & Incrementality"],
    "autonova": ["CRM & Offline Sales", "Measurement & Incrementality"],
    "routeo": [],
}


def dp_slug(name):
    return "dp_" + "".join(ch if ch.isalnum() else "_" for ch in name.lower().replace("&", "and")).strip("_").replace("__", "_").replace("__", "_")


# checks: every table is in exactly one place, one join path, modules only reach shared dims + core
owner = {t: "Shared Dimensions" for t in SHARED_DIMS}
for dpn, (_, _, tabs) in DATA_PRODUCTS.items():
    for t in tabs:
        assert t not in owner, t
        owner[t] = dpn
assert set(owner) == set(SCHEMA) == set(REFS), set(SCHEMA) ^ set(owner)


def paths(t, target):
    return (1 if t == target else 0) + sum(paths(r, target) for r in REFS[t])


for t in REFS:
    for target in REFS:
        assert paths(t, target) <= 1, f"ambiguous join path {t} -> {target}"
    for r in REFS[t]:
        assert owner[r] in ("Shared Dimensions", owner[t]), f"{t} ({owner[t]}) references {r} ({owner[r]})"

for c in CLIENTS:
    since = c["since"] if c["since"] > START.isoformat() else START.isoformat()
    for dpn, (pkg, aud, _) in DATA_PRODUCTS.items():
        on = pkg in ("Core", "Standard") or dpn in ENTITLED[c["id"]]
        if pkg == "Internal":
            on = False
        W.row("client_data_products", [f"{c['id']}-{dp_slug(dpn)}", c["id"], dpn, pkg, aud, yn(on),
                                       since if on else NA_DATE, dp_slug(dpn), c["id"]])

import json
with open(os.path.join(HERE, "data_products.json"), "w") as f:
    json.dump({
        "rule": "A data product's datasets may reference only Shared Dimensions or their own datasets; its metrics may "
                "also use the Core product (" + CORE + "), which every client and every Arcane user can see. "
                "Date datasets are shared.",
        "shared_dimensions": SHARED_DIMS,
        "references": REFS,
        "data_products": {n: {"user_group": dp_slug(n), "package": pk, "audience": au, "datasets": ds}
                          for n, (pk, au, ds) in DATA_PRODUCTS.items()},
        "entitlements": {c["id"]: [n for n, (pk, _, _) in DATA_PRODUCTS.items()
                                   if pk in ("Core", "Standard") or n in ENTITLED[c["id"]]] for c in CLIENTS},
    }, f, indent=2, ensure_ascii=False)

W.close()


# ---------------------------------------------------------------------------
# DDL (PostgreSQL / DuckDB / MotherDuck, BigQuery, Snowflake)
# ---------------------------------------------------------------------------
def bq_type(t):
    return {"DATE": "DATE", "INTEGER": "INT64", "BIGINT": "INT64"}.get(t, "NUMERIC" if t.startswith("NUMERIC")
                                                                         else "STRING")


def write_ddl():
    os.makedirs(OUT_DDL, exist_ok=True)
    with open(os.path.join(OUT_DDL, "postgresql.sql"), "w") as f:
        f.write("-- Arcane demo schema (GoodData Cloud). WDF column: wdf__client_id\n"
                "-- Works for PostgreSQL and DuckDB / MotherDuck.\n\n")
        for t, cols in SCHEMA.items():
            body = ",\n".join(f"  {c} {typ} NOT NULL" for c, typ in cols)
            body += f",\n  PRIMARY KEY ({', '.join(PRIMARY_KEYS[t])})"
            f.write(f"DROP TABLE IF EXISTS {t};\nCREATE TABLE {t} (\n{body}\n);\n\n")
        f.write("-- load (psql, run from demo_data/):\n")
        for t in SCHEMA:
            f.write(f"\\copy {t} FROM 'csv/{t}.csv' WITH (FORMAT csv, HEADER true)\n")
    with open(os.path.join(OUT_DDL, "bigquery.sql"), "w") as f:
        f.write("-- Arcane demo schema for BigQuery (Arcane's production warehouse). Dataset: arcane_demo\n"
                "-- Load: bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.<table> csv/<table>.csv\n\n")
        for t, cols in SCHEMA.items():
            body = ",\n".join(f"  {c} {bq_type(typ)} NOT NULL" for c, typ in cols)
            f.write(f"CREATE OR REPLACE TABLE arcane_demo.{t} (\n{body}\n);\n\n")
        for t in SCHEMA:
            f.write(f"-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.{t} csv/{t}.csv\n")
    with open(os.path.join(OUT_DDL, "snowflake.sql"), "w") as f:
        f.write("-- Arcane demo schema (GoodData Cloud). WDF column: WDF__CLIENT_ID\n")
        f.write("CREATE SCHEMA IF NOT EXISTS ARCANE;\nUSE SCHEMA ARCANE;\n"
                "CREATE OR REPLACE FILE FORMAT ARC_CSV TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '\"';\n"
                "CREATE OR REPLACE STAGE ARC_STAGE FILE_FORMAT = ARC_CSV;\n\n")
        for t, cols in SCHEMA.items():
            body = ",\n".join(f"  {c.upper()} {typ} NOT NULL" for c, typ in cols)
            f.write(f"CREATE OR REPLACE TABLE {t.upper()} (\n{body}\n);\n\n")
        f.write("-- PUT file://<path>/demo_data/csv/*.csv @ARC_STAGE;  then:\n")
        for t in SCHEMA:
            f.write(f"COPY INTO {t.upper()} FROM @ARC_STAGE/{t}.csv.gz;\n")


write_ddl()
print("Row counts:")
for t in SCHEMA:
    print(f"  {t:<28}{W.counts[t]:>10,}")
print(f"  {'TOTAL':<28}{sum(W.counts.values()):>10,}")
