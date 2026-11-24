"""
Section descriptions of the Arcane dashboards (shown under each section title). Client-neutral, because the
client workspaces inherit the dashboards from the parent.
"""

CONTENT = {
    "d1_paid_media": {
        "sections": {
            "Trend & Mix": "Monthly spend and return, where the budget goes (platform, market / funnel stage) and CPA by device.",
            "Campaigns": "Performance by campaign type, or switch to the top campaigns ranked by cost.",
            "Search Health": "Impression share on search and shopping. A rising Lost IS (Budget) means caps are "
                             "limiting volume.",
        },
    },
    "d2_social_creatives": {
        "sections": {
            "Formats & Production": "Format and production source - click a format to see its creatives.",
            "Trend": "Social spend by platform over time and conversions by creative theme.",
            "Creatives": "Individual creatives ranked by spend, with hook (thumb-stop) and hold rates.",
        },
    },
    "d3_web_geo": {
        "sections": {
            "Channels": "Backend revenue and conversion rate per marketing channel.",
            "Attribution & GEO": "Platform-reported vs backend ROAS or AI-assistant traffic (switch), and efficiency by market.",
        },
    },
    "d4_budget_pacing": {
        "sections": {
            "This Month": "Current-month pacing by market and platform - not affected by the date filter.",
            "Selected Period": "Planned vs actual for the period in the date filter, by month, market and platform.",
        },
    },
    "d5_product_feed": {
        "sections": {
            "Feed Optimization": "CTR of optimised vs non-optimised products, and product spend by platform.",
            "Products": "Category ROAS and the top products by cost.",
        },
    },
    "d6_crm_offline": {
        "sections": {
            "Funnel": "Lead volume and quality by month, and the funnel / lead status (switch).",
            "Efficiency": "Cost per lead and per won deal over time, and lead quality by platform.",
            "Locations": "Dealers / sales locations: leads, qualification, won deals, value and speed of contact.",
        },
    },
    "d7_measurement": {
        "sections": {
            "Results": "iROAS by campaign scope and the full test log.",
        },
    },
    "d8_arcane_ops": {
        "sections": {
            "Requests": "Request volume by type, delivery time and the full request log.",
            "Entitlements": "Data products enabled per client - this table drives dashboard and data permissions.",
        },
    },
}
