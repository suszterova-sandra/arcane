import type { IconName } from "./icons";

export const AGENT_STYLE: Record<string, { ico: IconName; bg: string; fg: string; short: string }> = {
  "arcane-briefing-agent": { ico: "summary", bg: "#E0F2F1", fg: "#004C52", short: "Briefing" },
  "arcane-performance-agent": { ico: "compass", bg: "#FFE4E0", fg: "#C2412F", short: "Performance doctor" },
  "arcane-budget-agent": { ico: "shield", bg: "#E6F4EC", fg: "#2F7A55", short: "Budget" },
};

export const agentStyle = (id: string) => AGENT_STYLE[id] || { ico: "bot" as IconName, bg: "#F1F5F9", fg: "#334155", short: "Assistant" };

/** Arcane's own agents (AI Hub) carry this id prefix. */
export const isArcaneAgent = (id: string) => id.startsWith("arcane-");

export const PLAYBOOK = [
  {
    agent: "arcane-briefing-agent",
    title: "Weekly briefing",
    sub: "What happened and why",
    prompt: "Brief me on the last 4 weeks: spend, conversions, ROAS / CPA versus target. Which market, platform or campaign type stands out?",
  },
  {
    agent: "arcane-performance-agent",
    title: "Diagnose a drop",
    sub: "Root cause in minutes",
    prompt: "Conversions dropped recently. Find the market, platform and campaign type behind it and check impression share lost to budget vs rank, CPC, conversion rate and tracking.",
  },
  {
    agent: "arcane-budget-agent",
    title: "Budget & pacing",
    sub: "Where to move the money",
    prompt: "How are we pacing against the media plan this month? Which markets or platforms are under- or over-spending, and where should unspent budget go?",
  },
];

export const SKILL_LABEL: Record<string, string> = {
  visualization: "Visualization",
  key_driver_analysis: "Key drivers",
  alert: "Alerts",
  knowledge: "Knowledge",
  schedule_export: "Scheduled exports",
  anomaly_detection: "Anomalies",
  what_if_analysis: "What-if",
  forecasting: "Forecasting",
  metric: "Metrics",
  clustering: "Clustering",
  dashboard_builder: "Dashboard builder",
  dashboard_editor: "Dashboard editor",
  visualization_summary: "Viz summary",
  dashboard_summary: "Dashboard summary",
  report_builder: "Report builder",
  document_builder: "Document builder",
};

export const KEY_PERMS = ["MANAGE", "ANALYZE", "VIEW"];
