#!/usr/bin/env python3
"""
Build one GoodData publisher report (document v2) per Arcane data product, and optionally deploy.

    python3 publisher/build_reports.py            # write publisher/<dp_id>_report.json
    python3 publisher/build_reports.py --deploy   # also create/update the documents in the parent workspace
    python3 publisher/build_reports.py dp_crm_and_offline_sales --deploy

Permissions: every report uses only visualizations of its own data product (same rule as the dashboards; the build
fails otherwise), so the object-level permissions of gooddata/apply_permissions.py apply to reports too - a user
outside the product's dp_* group can't render its visualizations. The reports live in the parent workspace and are
inherited by every client workspace; the data is filtered to the client there (workspace data filter).
Theming: colours and images come from the active workspace theme ({theme.colors.*}, {theme.assets.images.*},
theme/build_themes.py) - Arcane brand in the parent, each client's co-branded theme in the child workspaces. The
cover visual is the product image {theme.assets.images.<dp_id>}.
"""
import itertools
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "gooddata"))
import build_analytics as ba  # noqa: E402

HOST = os.environ.get("GD_HOST", "https://sandrasuszterova.demo.cloud.gooddata.com")
PARENT_WS = "4d4926ef508e4cba9085ca29fefcf4fd"

BG, CARD, PANEL = ("{theme.colors.backgrounds.page}", "{theme.colors.backgrounds.card}",
                   "{theme.colors.backgrounds.panel}")
ACCENT, TXT, TXT2, MUTED = ("{theme.colors.texts.accent}", "{theme.colors.texts.default}",
                            "{theme.colors.texts.muted}", "{theme.colors.texts.subtle}")
DEFAULT_DATE = ba.DATE
DATE_OF = {}
_spacer = itertools.count(1)
_page = "page"

ba.build_visuals()
VIS = ba.VIS
TITLES = {k: v["title"] for k, v in VIS.items()}
SLUG = {n: x["user_group"] for n, x in ba.DP["data_products"].items()}

# ---------------------------------------------------------------- report content per data product
# kpis: 4 headline visualizations; main: chart next to the KPIs; period: report months (relative, -1 = last full month)
# pages: (title, lead, left vis, right vis, reading guide). Guides are reading guides; AI takeaways give the numbers.
PRODUCTS = {
    "Paid Media Performance": dict(
        kicker="PAID MEDIA", summary="Cross-platform media results: spend, conversions, ROAS / CPA, markets and search health.",
        kpis=["pm_k_cost", "pm_k_conv", "pm_k_roas", "pm_k_cpa"], main="pm_trend",
        main_guide="ROAS holding while spend grows means the budget scales efficiently.\n\n"
                   "Peaks follow the retail calendar (soldes, Black Friday, Christmas).\n\n"
                   "**Ask:** which campaign types should get the next euro?",
        pages=[("Platforms & Campaign Types", "Where the budget goes and which campaign types pay back.",
                "pm_by_platform", "pm_by_type",
                "Brand search has the best ROAS but little incremental value.\n\n"
                "PMax replaced Standard Shopping in March 2025.\n\n**Ask:** where is CPA above target?"),
               ("Markets & Search Health", "Results per market and the search impression share trend.",
                "pm_by_market", "pm_is_trend",
                "A jump in Lost IS (Budget) means campaigns are capped and miss demand.\n\n"
                "Lost IS (Rank) means competitors outbid us.\n\n**Ask:** which market is budget-limited?")]),
    "Social Creatives": dict(
        kicker="SOCIAL & CREATIVES", summary="Meta, TikTok and LinkedIn creative performance: formats, themes, production.",
        kpis=["sc_k_spend", "sc_k_ctr", "sc_k_cpa", "sc_k_thumb"], main="sc_trend",
        main_guide="TikTok and LinkedIn grow next to Meta - each needs its own creative style.\n\n"
                   "**Ask:** is the creative pipeline fast enough for the spend?",
        pages=[("Formats & Production", "Which formats and production sources win.", "sc_by_format", "sc_by_source",
                "UGC and creator-style videos usually beat polished studio ads on CTR.\n\n"
                "AI-generated creatives (Arcane AI Lab) cut production time.\n\n**Ask:** what should the next brief be?"),
               ("Themes & Top Creatives", "Messages that convert and the creatives to keep or refresh.",
                "sc_by_theme", "sc_top",
                "Creatives fatigue after 4-6 weeks: CTR falls on old creatives.\n\n"
                "**Ask:** which top spenders need a refresh?")]),
    "Web Analytics & GEO": dict(
        kicker="WEB, SALES & GEO", summary="Backend truth: revenue by channel, blended ROAS, over-attribution and AI search.",
        kpis=["wa_k_rev", "wa_k_mer", "wa_k_paidshare", "wa_k_ai"], main="wa_rev_channel",
        main_guide="Backend revenue is the client's source of truth - platforms each claim the same sale.\n\n"
                   "**Ask:** is paid media growing revenue or just taking credit?",
        pages=[("Platform vs Backend", "How much the platforms over-attribute, by market.", "wa_attrib", "wa_market",
                "Platform ROAS above backend ROAS is normal; a widening gap is not.\n\n"
                "Social and video over-attribute the most.\n\n**Ask:** which budget decisions should use MER?"),
               ("Channels & AI Search", "Channel efficiency and the rise of AI assistants as a traffic source.",
                "wa_channels", "wa_ai_trend",
                "AI assistants (ChatGPT, Perplexity, Gemini) send small but fast-growing, high-converting traffic.\n\n"
                "**Ask:** is the brand visible in AI answers (GEO)?")]),
    "Budget & Pacing": dict(
        kicker="BUDGET & PACING", summary="Media plan versus actual spend by month, market and platform.",
        kpis=["bp_p_planned", "bp_p_actual", "bp_p_pacing", "bp_p_variance"], main="bp_trend",
        main_guide="Pacing far below 100% means the plan is not delivered - often a budget cap or low demand.\n\n"
                   "**Ask:** should unspent budget move to another market or platform?",
        pages=[("Plan vs Actual", "Which plan lines under- or over-delivered.", "bp_p_table", "bp_trend",
                "Under-spending right before peak season (Black Friday) is lost revenue.\n\n"
                "**Ask:** which market's plan needs to be re-forecast?")]),
    "Product Feed & Shopping": dict(
        kicker="PRODUCT FEED & SHOPPING", summary="Shopping, Performance Max and Amazon at product level; SmartFeeds impact.",
        kpis=["pf_k_cost", "pf_k_value", "pf_k_roas", "pf_k_ctr"], main="pf_feed",
        main_guide="Optimised feed titles and attributes lift product CTR in the same auctions.\n\n"
                   "**Ask:** which categories should be optimised next?",
        pages=[("Categories & Top Products", "Where shopping budget pays back.", "pf_category", "pf_top",
                "A few products drive most of the value - protect their budget.\n\n"
                "**Ask:** which products spend without converting?"),
               ("Platforms", "Google vs Microsoft vs Amazon.", "pf_platform", "pf_category",
                "Amazon converts high-intent shoppers; Google drives volume.\n\n**Ask:** is the platform mix right?")]),
    "CRM & Offline Sales": dict(
        kicker="CRM & OFFLINE SALES", summary="Lead quality and real sales: funnel, cost per qualified lead and per won deal.",
        kpis=["crm_k_leads", "crm_k_qual", "crm_k_won", "crm_k_cpw"], main="crm_trend",
        main_guide="More leads at lower quality is not progress - judge platforms on qualified leads and won deals.\n\n"
                   "**Ask:** which platforms bring leads that actually buy?",
        pages=[("Funnel & Lead Quality", "Where leads drop out and which platforms bring buyers.",
                "crm_funnel", "crm_platform",
                "Meta lead forms bring volume but lower qualification than search.\n\n"
                "**Ask:** should bidding optimise on qualified leads?"),
               ("Cost Efficiency & Locations", "Cost per qualified lead / won deal and performance per location.",
                "crm_cost_trend", "crm_location",
                "Offline conversion import (SmartConversion) teaches bidding which leads buy.\n\n"
                "Speed to first contact drives qualification.\n\n**Ask:** which locations follow up too slowly?")]),
    "Measurement & Incrementality": dict(
        kicker="MEASUREMENT", summary="Incrementality tests: what the media really caused, channel by channel.",
        kpis=["mi_k_tests", "mi_k_iroas", "mi_k_rev", "mi_k_share"], main="mi_scope", period=(-23, -1),
        main_guide="iROAS below 1.0 means the channel does not pay back, whatever the platform reports.\n\n"
                   "**Ask:** which channel should be tested next?",
        pages=[("Test Results", "All tests with result and recommendation.", "mi_table", "mi_scope",
                "Retargeting and brand search are usually the least incremental.\n\n"
                "Prospecting and PMax in new markets are usually the most.\n\n**Ask:** what budget shift follows?")]),
    "Arcane Operations": dict(
        kicker="ARCANE OPERATIONS (INTERNAL)", summary="The data-support loop today: request volume, lead time and effort.",
        kpis=["op_k_req", "op_k_days", "op_k_open", "op_k_effort"], main="op_trend",
        main_guide="Every request is a consultant writing SQL and rebuilding a report - days of waiting.\n\n"
                   "**Ask:** how many of these could clients answer themselves with AI?",
        pages=[("Lead Time & Request Log", "Which requests take longest and what is in the queue.",
                "op_days_type", "op_list",
                "New data sources take weeks; new KPIs and breakdowns are self-service in GoodData.\n\n"
                "**Ask:** which request types disappear with self-service and AI?")]),
}


# ---------------------------------------------------------------- primitives

def text(tid, markdown, text_style="normalText", proportion=None, **style):
    node = {"type": "text", "id": tid, "markdown": markdown, "style": {"text_style": text_style, **style}}
    if proportion is not None:
        node["proportion"] = proportion
    return node


def heading(tid, label, text_style="largeText", proportion=None, as_title=False, **style):
    node = text(tid, f"**{label}**", text_style, proportion, **style)
    if as_title:
        node["type"] = "title"
    return node


def image(iid, source, proportion=None, fit="contain", h="left", v="center"):
    node = {"type": "image", "id": iid, "decorative": True, "source": source,
            "style": {"fit": fit, "horizontal_align": h, "vertical_align": v}}
    if proportion is not None:
        node["proportion"] = proportion
    return node


def rule(proportion):
    return image(f"{_page}_rule{next(_spacer)}", "{theme.assets.images.accent_bar}", proportion)


def spacer(proportion):
    return image(f"{_page}_gap{next(_spacer)}", "{theme.assets.images.spacer}", proportion, h="center")


def card(children, background=CARD, proportion=None, pad=None):
    if pad:
        side, top, bottom = pad
        body = {"type": "column", "proportion": 1, "children": children}
        inner = {"type": "row", "proportion": 10, "children": [spacer(side), body, spacer(side)]} if side else \
            {"type": "column", "proportion": 10, "children": children}
        children = ([spacer(top)] if top else []) + [inner] + ([spacer(bottom)] if bottom else [])
    node = {"type": "column", "style": {"background_color": background}, "children": children}
    if proportion is not None:
        node["proportion"] = proportion
    return node


def plain_row(children, proportion):
    return {"type": "row", "proportion": proportion, "children": children}


def viz(vid, visualization):
    return {"type": "visualization", "id": vid, "visualization": visualization,
            "date": DATE_OF.get(visualization, DEFAULT_DATE)}


def kpi_tile(visualization):
    return card([
        heading(f"{_page}_{visualization}_lbl", TITLES[visualization].upper(), "smallText", 0.55,
                text_color=TXT2, horizontal_align="center", vertical_align="bottom"),
        {"type": "column", "proportion": 3.6, "children": [viz(f"{_page}_{visualization}", visualization)]},
    ], pad=(0, 0.35, 0.35))


def chart_card(vid, visualization, proportion=None):
    return card([
        heading(f"{vid}_lbl", TITLES[visualization], "normalText", 1, text_color=TXT,
                horizontal_align="center", vertical_align="center"),
        {"type": "column", "proportion": 8, "children": [viz(vid, visualization)]},
    ], proportion=proportion)


def insight(body, proportion=1.3, label="What to look for"):
    return card([
        heading(f"{_page}_ih", label, "normalText", 1, text_color=ACCENT, vertical_align="center"),
        text(f"{_page}_ib", body, "smallText", 5.5, text_color=TXT2),
    ], background=PANEL, proportion=proportion, pad=(0.07, 0.3, 0.3))


def footer(label):
    return {"type": "row", "proportion": 0.6, "children": [
        image(f"{_page}_logo", "{theme.assets.images.logo}", 2, v="bottom"),
        {"type": "text", "id": f"{_page}_section", "proportion": 5, "decorative": True, "markdown": label,
         "style": {"text_style": "smallText", "horizontal_align": "center", "vertical_align": "bottom"}},
        {"type": "text", "id": f"{_page}_pageno", "proportion": 2, "decorative": True,
         "markdown": "{currentPageNumber} / {totalPages}",
         "style": {"text_style": "smallText", "horizontal_align": "right", "vertical_align": "bottom"}}]}


def content_page(page_id, label, kicker, title, lead, body_rows):
    global _page
    _page = page_id
    children = [
        {"type": "column", "proportion": 2.0, "children": [
            text(f"{page_id}_kicker", kicker, "smallText", 0.8, text_color=ACCENT, vertical_align="bottom"),
            heading(f"{page_id}_title", title, "largeText", 1.3, as_title=True, text_color=TXT,
                    vertical_align="center"),
            text(f"{page_id}_lead", lead, "normalText", 1, vertical_align="top")]},
        rule(0.05),
        *body_rows(),
        footer(label),
    ]
    return {"id": page_id, "kind": "content", "style": {"background_color": BG},
            "layout": {"type": "column", "children": children}}


def cover(dp_id, title, summary, kicker):
    global _page
    _page = pid = "page_cover"
    return {"id": pid, "kind": "cover", "style": {"background_color": BG},
            "layout": {"type": "row", "children": [
                card([
                    spacer(1.6),
                    text("cover_kicker", f"{kicker}  ·  {{documentDateRange}}", "smallText", 0.6,
                         text_color=ACCENT, vertical_align="bottom"),
                    heading("cover_title", title, "largeText", 1.4, as_title=True, text_color=TXT,
                            vertical_align="center"),
                    rule(0.08),
                    text("cover_meta", summary, "normalText", 1.3, text_color=TXT2, vertical_align="top"),
                    image("cover_logo", "{theme.assets.images.logo}", 0.6, v="bottom")],
                    background=BG, proportion=1, pad=(0.08, 0.3, 0.3)),
                {"type": "column", "proportion": 1.25, "style": {"background_color": BG}, "children": [
                    image("cover_hero", f"{{theme.assets.images.{dp_id}}}", fit="cover", h="center")]}]}}


def build(product, cfg, dp_id):
    title = f"{product} Report"
    label = f"Arcane  ·  {product}"
    k = cfg["kicker"]
    pages = [cover(dp_id, title, cfg["summary"], k),
             content_page("page_glance", label, k, "At a Glance", "Headline results for the period.", lambda: [
                 plain_row([kpi_tile(v) for v in cfg["kpis"]], 4.0),
                 plain_row([chart_card("v_main", cfg["main"], proportion=2.7), insight(cfg["main_guide"])], 5.0)])]
    for i, (ptitle, lead, left, right, guide) in enumerate(cfg["pages"], 1):
        pages.append(content_page(f"page_{i}", label, k, ptitle, lead, lambda l=left, r=right, g=guide: [
            plain_row([chart_card(f"v_{i}_l", l), chart_card(f"v_{i}_r", r), insight(g, proportion=0.75)], 8)]))
    # data product isolation: every visualization must belong to this product
    used = set(re.findall(r'"visualization": "([a-z0-9_]+)"', json.dumps(pages)))
    foreign = [v for v in used if VIS[v]["tags"] != [product]]
    if foreign:
        raise SystemExit(f"{product} report uses visualizations of other products: {foreign}")
    p_from, p_to = cfg.get("period", (-5, -1))
    return {
        "type": "document", "id": f"{dp_id}_report", "version": "2", "title": title, "description": cfg["summary"],
        "tags": [product],
        "period": {"granularity": "MONTH", "from": p_from, "to": p_to},
        "content": {
            "defaults": {"page_size": "widescreen", "takeaway": {"generation": {"instructions": (
                f"Act as a senior performance-marketing analyst at a media agency reporting to an advertiser. This "
                f"report covers {product}. Write short messages, max 255 characters. Explain what stands behind the "
                f"numbers (markets, platforms, campaign types, seasonality, budget, tracking) more than restating them, "
                f"and end with a concrete recommendation where possible.")}}},
            "sections": [{"id": "section_main", "pages": pages}],
        },
    }


# ---------------------------------------------------------------- deploy (authoring format -> API format)

def camel(k):
    parts = k.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def to_api(node):
    if isinstance(node, list):
        return [to_api(x) for x in node]
    if not isinstance(node, dict):
        return node
    if node.get("type") == "visualization":
        return {"type": "visualization", "id": node["id"],
                "visualization": {"identifier": node["visualization"], "type": "insight"},
                "dateDataSet": {"identifier": node["date"], "type": "dataSet"}}
    return {camel(k): to_api(v) for k, v in node.items()}


def api(method, path, body=None):
    req = urllib.request.Request(HOST + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {os.environ['GOODDATA_API_TOKEN']}",
                                          "Content-Type": "application/vnd.gooddata.api+json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]


def deploy(doc):
    p = doc["period"]
    attrs = {"title": doc["title"], "description": doc["description"], "tags": doc["tags"], "version": "2",
             "period": {"granularity": f"GDC.time.{p['granularity'].lower()}", "from": p["from"], "to": p["to"],
                        "type": "relative"},
             "content": to_api(doc["content"])}
    body = {"data": {"id": doc["id"], "type": "document", "attributes": attrs}}
    code, resp = api("PUT", f"/api/v1/entities/workspaces/{PARENT_WS}/documents/{doc['id']}", body)
    if code == 404:
        code, resp = api("POST", f"/api/v1/entities/workspaces/{PARENT_WS}/documents", body)
    return code, resp


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    assert set(PRODUCTS) == set(SLUG), set(PRODUCTS) ^ set(SLUG)
    for product, cfg in PRODUCTS.items():
        dp_id = SLUG[product]
        if only and dp_id not in only:
            continue
        doc = build(product, cfg, dp_id)
        (HERE / f"{dp_id}_report.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        msg = f"{dp_id}_report.json"
        if "--deploy" in sys.argv:
            code, resp = deploy(doc)
            msg += f"  -> {code}" + ("" if code in (200, 201) else f" {resp}")
        print(msg)


if __name__ == "__main__":
    main()
