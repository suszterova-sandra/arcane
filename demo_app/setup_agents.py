"""Create or update the three Arcane agents in AI Hub (idempotent).

    python3 demo_app/setup_agents.py

All Arcane clients have the AI Assistant, so the agents follow the data products: the Briefing and Performance
Doctor agents go to everyone with Paid Media Performance (Core = every client), the Budget agent to the Budget &
Pacing group; Arcane admins get all three.
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = dict(l.split("=", 1) for l in (ROOT / ".env").read_text().splitlines() if "=" in l)
TOKEN = ENV["GOODDATA_API_TOKEN"].strip().strip('"')  # org admin, local only
HOST = "https://sandrasuszterova.demo.cloud.gooddata.com"


def req(method, path, body=None):
    r = urllib.request.Request(HOST + path, method=method, data=json.dumps(body).encode() if body else None,
                               headers={"Authorization": "Bearer " + TOKEN,
                                        "Content-Type": "application/vnd.gooddata.api+json"})
    try:
        with urllib.request.urlopen(r) as x:
            return x.status, x.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def ins(title, content):
    assert len(content) <= 255, (title, len(content))
    return {"title": title, "strategy": "ALWAYS", "content": content}


AGENTS = [
    dict(id="arcane-briefing-agent", name="Client Briefing Agent",
         description="Weekly briefing for an advertiser: spend, conversions and ROAS / CPA versus target, what moved, in which market, platform and campaign type.",
         personality="You are a senior performance-marketing consultant at a Paris media agency briefing an advertiser. Lead with the headline number, then context. Plain language, no filler.",
         skills=["dashboard_summary", "visualization_summary", "visualization", "key_driver_analysis", "anomaly_detection"],
         instructions=[ins("Format", "Start with a one-line headline with the key number versus target. Then at most 5 bullets: metric, change vs previous period, and the driver (market, platform, campaign type)."),
                       ins("Truth", "Use the client's own KPI definition. Say when platform conversions differ from backend sales. Always state the period. Mark anything unusual with 'Anomaly'.")],
         groups=["dp_paid_media_performance", "adminGroup"]),
    dict(id="arcane-performance-agent", name="Performance Doctor",
         description="Diagnoses a performance drop: finds the market, platform and campaign type behind it and separates budget caps, auction pressure, conversion rate and tracking issues.",
         personality="You are Arcane's paid-search and paid-social troubleshooter. Be precise, show the evidence for each cause and end with the fix.",
         skills=["key_driver_analysis", "anomaly_detection", "visualization", "forecasting", "metric", "alert"],
         instructions=[ins("Method", "Break the drop down by market, platform and campaign type. Check Lost IS (Budget) vs Lost IS (Rank), CPC, conversion rate and pacing. Clicks stable but conversions gone = tracking."),
                       ins("Format", "Return: 1) root cause with numbers, 2) what it cost (conversions / revenue lost), 3) the fix with an owner, 4) an alert to set so it is caught next time. Ask before creating anything.")],
         groups=["dp_paid_media_performance", "adminGroup"]),
    dict(id="arcane-budget-agent", name="Budget & Pacing Agent",
         description="Checks pacing against the media plan, forecasts month-end spend and proposes where to move unspent budget.",
         personality="You are a media planner. You think in budgets, targets and trade-offs and speak in concrete reallocations.",
         skills=["forecasting", "what_if_analysis", "visualization", "alert", "schedule_export", "metric"],
         instructions=[ins("Format", "List under- and over-pacing plan lines (market x platform) with planned vs actual. Forecast month-end. Propose at most 3 budget moves with expected impact on ROAS or CPA."),
                       ins("Rules", "Respect the client's target ROAS / CPA. Never propose moving budget into a channel with iROAS below 1 when a test exists. Offer a pacing alert or weekly export; ask first.")],
         groups=["dp_budget_and_pacing", "adminGroup"]),
]

if __name__ == "__main__":
    for a in AGENTS:
        body = {"data": {"id": a["id"], "type": "agent",
                         "attributes": {"enabled": True, "name": a["name"], "description": a["description"],
                                        "personality": a["personality"], "skillsMode": "custom",
                                        "customSkills": a["skills"], "aiKnowledge": True, "availableToAll": False,
                                        "instructions": a["instructions"]},
                         "relationships": {"userGroups": {"data": [{"id": g, "type": "userGroup"} for g in a["groups"]]}}}}
        s, t = req("POST", "/api/v1/entities/agents", body)
        if s == 409:
            s, t = req("PUT", "/api/v1/entities/agents/" + a["id"], body)
        print(a["id"], s, t[:300] if s >= 300 else "ok")
