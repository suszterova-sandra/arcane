#!/usr/bin/env python3
"""
AI context for the Arcane workspaces.

* Parent workspace (inherited by every client workspace): Arcane-wide rules for the AI assistant + the analytics
  guide (knowledge/arcane_analytics_guide.md).
* Each client workspace: the client's OWN business definitions ("what does sales mean for us", target, seasonality)
  = the per-client semantic layer on top of the shared model.

    set -a; . ../.env; set +a
    python3 gooddata/deploy_ai_context.py
Re-running updates everything in place.
"""
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

HOST = os.environ.get("GD_HOST", "https://sandrasuszterova.demo.cloud.gooddata.com")
PARENT = "4d4926ef508e4cba9085ca29fefcf4fd"
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
TOKEN = os.environ["GOODDATA_API_TOKEN"]

# (id, title, strategy, instruction <= 255 chars, keywords for AUTO)
PARENT_MEMORIES = [
    ("arc_roas", "ROAS: platform vs backend", "ALWAYS",
     "ROAS = platform conversion value / cost (what ad platforms report). Backend ROAS uses de-duplicated backend "
     "revenue and is the truth for the client. When they differ, say platforms over-attribute.", []),
    ("arc_conversions", "Conversions mean different things", "ALWAYS",
     "Platform Conversions are orders, bookings or leads depending on the client (see the client's Primary KPI). "
     "Never add conversions across clients with different KPIs.", []),
    ("arc_partial", "Partial periods", "ALWAYS",
     "Data ends yesterday; the current week and month are partial. Compare to-date periods with the same days of the "
     "previous period, never a partial month with a full month.", []),
    ("arc_direction", "Good and bad direction", "ALWAYS",
     "Lower is better: CPC, CPM, CPA, Cost per Lead, Cost per Won Deal, Lost IS. Higher is better: ROAS, MER, CTR, "
     "conversion rate, impression share, qualification and win rate, iROAS.", []),
    ("arc_drop", "Diagnosing a performance drop", "AUTO",
     "For a drop: compare by market, platform and campaign type, then check Search Impression Share, Lost IS (Budget) "
     "vs Lost IS (Rank), CPC and conversion rate, and budget pacing vs plan.",
     ["drop", "decline", "down", "fell", "decrease", "why", "worse", "performance", "problem", "issue"]),
    ("arc_tracking", "Tracking issues", "AUTO",
     "If platform conversions collapse while clicks and backend transactions stay stable, it is a tracking issue "
     "(pixel / CAPI / tag), not a demand drop.",
     ["tracking", "pixel", "capi", "tag", "conversions", "zero", "missing", "outage", "meta", "facebook"]),
    ("arc_budget", "Budget pacing", "AUTO",
     "Budget Pacing = cost / planned budget. For the current month compare with the share of the month elapsed: "
     "below it is under-pacing, above it is over-pacing.",
     ["budget", "pacing", "plan", "planned", "spend", "underspend", "overspend", "media plan"]),
    ("arc_social", "Social creative metrics", "AUTO",
     "Thumb-stop rate = 3-second views / impressions (hook). Hold rate = ThruPlays / 3-second views. Creatives fatigue "
     "after 4-6 weeks: falling CTR on an old creative means refresh it.",
     ["creative", "creatives", "ugc", "video", "hook", "thumb", "fatigue", "tiktok", "meta", "social"]),
    ("arc_incrementality", "Incrementality", "AUTO",
     "iROAS = incremental revenue / test spend from geo-lift or conversion-lift tests. It beats platform ROAS for "
     "budget decisions; iROAS < 1 means the channel does not pay back.",
     ["incrementality", "incremental", "iroas", "lift", "geo", "test", "holdout", "mmm"]),
    ("arc_geo", "AI assistants (GEO)", "AUTO",
     "The web channel 'AI Assistants (ChatGPT, Perplexity, Gemini)' tracks visits referred by AI answers - Arcane's "
     "GEO offer. Report its sessions and share of sessions.",
     ["ai", "chatgpt", "perplexity", "gemini", "geo", "llm", "assistant", "organic"]),
    ("arc_feed", "Product feed", "AUTO",
     "Feed Optimized = the product feed was optimised with Arcane SmartFeeds (titles, attributes). Compare product CTR "
     "of optimised vs non-optimised products in the same weeks.",
     ["feed", "smartfeeds", "product", "products", "shopping", "pmax", "sku", "catalog"]),
]

CLIENT_MEMORIES = {
    "secondevie": [
        ("sv_sales", "Seconde Vie: what sales means", "ALWAYS",
         "For Seconde Vie, sales / commandes / GMV = Backend Transactions and Backend Revenue (orders net of "
         "cancellations and 14-day returns, VAT incl.). Target ROAS 6.0. Markets FR DE ES IT GB US.", []),
        ("sv_b2b", "Seconde Vie Pro (B2B)", "AUTO",
         "Seconde Vie Pro is the B2B device-fleet business: its leads and won deals are in the CRM (quote sent -> deal "
         "won), fed by Search - B2B Leads and LinkedIn Lead Gen campaigns.",
         ["b2b", "pro", "lead", "leads", "deal", "deals", "quote", "linkedin", "fleet", "crm"]),
    ],
    "autonova": [
        ("an_sales", "AutoNova: what sales means", "ALWAYS",
         "For AutoNova, conversions are leads; a sale = a Won Deal (car sold in the DMS). Lead qualifie = Qualified "
         "Leads. Judge media on Cost per Qualified Lead and Cost per Won Deal; target CPL 45 EUR.", []),
        ("an_smartconversion", "AutoNova offline conversions", "AUTO",
         "Since 10 March 2025 sold cars are uploaded to Google Ads as offline conversions (SmartConversion); Google "
         "lead quality and cost per car sold improved after that date.",
         ["offline", "smartconversion", "sold", "sale", "quality", "qualified", "google", "import"]),
    ],
    "routeo": [
        ("rt_sales", "Routeo: what sales means", "ALWAYS",
         "For Routeo, sales / reservations = Backend Transactions = confirmed bookings (paid or guaranteed, "
         "cancellations excluded). Target CPA 28 EUR. Bookings peak March-July and before Easter.", []),
    ],
}


def api(method, path, body=None, content_type="application/vnd.gooddata.api+json"):
    req = urllib.request.Request(HOST + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": content_type})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b"{}")


def deploy_memories(ws, items, tag):
    path = f"/api/v1/entities/workspaces/{ws}/memoryItems"
    for mid, title, strategy, instruction, keywords in items:
        assert len(instruction) <= 255, (mid, len(instruction))
        body = {"data": {"id": mid, "type": "memoryItem", "attributes": {
            "title": title, "strategy": strategy, "instruction": instruction, "keywords": keywords,
            "tags": [tag], "isDisabled": False}}}
        try:
            api("POST", path, body)
        except urllib.error.HTTPError as e:
            if e.code != 409:
                raise RuntimeError(f"{ws}/{mid}: {e.code} {e.read().decode()[:300]}")
            api("PUT", f"{path}/{mid}", body)
    print(f"✓ {ws}: {len(items)} AI memory items")


def deploy_knowledge(ws):
    for doc in sorted(KNOWLEDGE_DIR.glob("*.md")):
        title = doc.read_text().splitlines()[0].lstrip("# ").strip()
        out = subprocess.run(
            ["curl", "-s", "-X", "PUT", f"{HOST}/api/v1/ai/workspaces/{ws}/knowledge/documents",
             "-H", f"Authorization: Bearer {TOKEN}",
             "-F", f"file=@{doc};type=text/markdown", "-F", f"title={title}"],
            capture_output=True, text=True, check=True).stdout
        res = json.loads(out)
        if not res.get("success"):
            raise RuntimeError(out)
        print(f"✓ knowledge document {doc.name} ({res['numChunks']} chunks)")


if __name__ == "__main__":
    deploy_memories(PARENT, PARENT_MEMORIES, "Arcane")
    for cid, items in CLIENT_MEMORIES.items():
        deploy_memories(cid, items, f"Client: {cid}")
    deploy_knowledge(PARENT)
