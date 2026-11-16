/**
 * Arcane data products as the app uses them: one dashboard, one Publisher report, the headline KPIs and
 * the visualizations a number opens. Mirrors gooddata/data_products.json and analytics/visualisations.
 * Users only see the products they are entitled to (object-level permissions per dp_* user group).
 */
export type Format = "money" | "count" | "pct" | "num";

export interface ProductKpi {
  metric: string;
  label: string;
  format: Format;
  goodWhenUp: boolean;
  viz: string;
}

export interface Product {
  name: string;
  dashboard: string;
  dashTitle: string;
  report: string;
  /** headline KPIs (the dashboard's <prefix>_k_* headlines), most important first */
  kpis: ProductKpi[];
  /** secondary numbers for the watch list */
  watch: ProductKpi[];
  /** visualizations a key driver (market / platform) opens */
  byMarket: { viz: string; title: string };
  byPlatform: { viz: string; title: string };
}

const k = (metric: string, label: string, format: Format, goodWhenUp: boolean, viz: string): ProductKpi => ({ metric, label, format, goodWhenUp, viz });

const slug = (name: string) => name.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
const P = (name: string, dashboard: string, dashTitle: string, kpis: ProductKpi[], watch: ProductKpi[], byMarket: [string, string], byPlatform: [string, string]): Product => ({
  name,
  dashboard,
  dashTitle,
  report: `dp_${slug(name)}_report`,
  kpis,
  watch,
  byMarket: { viz: byMarket[0], title: byMarket[1] },
  byPlatform: { viz: byPlatform[0], title: byPlatform[1] },
});

export const PRODUCTS: Record<string, Product> = Object.fromEntries(
  [
    P(
      "Paid Media Performance",
      "d1_paid_media",
      "Paid Media Performance",
      [k("pm_cost", "Media spend", "money", true, "pm_k_cost"), k("pm_roas", "ROAS", "num", true, "pm_k_roas")],
      [k("pm_cpa", "CPA", "money", false, "pm_k_cpa"), k("pm_ctr", "CTR", "pct", true, "pm_k_ctr")],
      ["pm_by_market", "Cost & Conversions by Market"],
      ["pm_by_platform", "Cost by Platform"],
    ),
    P(
      "CRM & Offline Sales",
      "d6_crm_offline",
      "CRM & Offline Sales",
      [k("crm_leads", "Leads", "count", true, "crm_k_leads"), k("crm_won", "Won deals", "count", true, "crm_k_won")],
      [k("crm_qual_rate", "Qualification rate", "pct", true, "crm_k_qual"), k("crm_cost_per_won", "Cost per won deal", "money", false, "crm_k_cpw")],
      ["crm_location", "Performance by Location"],
      ["crm_platform", "Lead Quality by Platform"],
    ),
    P(
      "Web Analytics & GEO",
      "d3_web_geo",
      "Web, Sales & GEO",
      [k("wa_revenue", "Backend revenue", "money", true, "wa_k_rev"), k("wa_mer", "Blended ROAS (MER)", "num", true, "wa_k_mer")],
      [k("wa_ai_sessions", "AI assistant sessions", "count", true, "wa_k_ai"), k("wa_cvr", "Site conversion rate", "pct", true, "wa_k_cvr")],
      ["wa_market", "Revenue & Efficiency by Market"],
      ["wa_channels", "Channel Performance"],
    ),
    P(
      "Product Feed & Shopping",
      "d5_product_feed",
      "Product Feed & Shopping",
      [k("pf_value", "Product conversion value", "money", true, "pf_k_value"), k("pf_roas", "Product ROAS", "num", true, "pf_k_roas")],
      [k("pf_ctr", "Product CTR", "pct", true, "pf_k_ctr"), k("pf_cost", "Product cost", "money", true, "pf_k_cost")],
      ["pf_top", "Top Products"],
      ["pf_platform", "Product Cost by Platform"],
    ),
    P(
      "Social Creatives",
      "d2_social_creatives",
      "Social & Creatives",
      [k("sc_spend", "Social spend", "money", true, "sc_k_spend"), k("sc_cpa", "Social CPA", "money", false, "sc_k_cpa")],
      [k("sc_ctr", "Social CTR", "pct", true, "sc_k_ctr"), k("sc_thumbstop", "Thumb-stop rate", "pct", true, "sc_k_thumb")],
      ["sc_top", "Top Creatives"],
      ["sc_trend", "Social Spend by Platform by Month"],
    ),
    P(
      "Budget & Pacing",
      "d4_budget_pacing",
      "Budget & Pacing",
      [k("bp_planned", "Planned budget", "money", true, "bp_p_planned"), k("bp_pacing", "Budget pacing", "pct", true, "bp_p_pacing")],
      [k("bp_variance", "Budget variance", "money", true, "bp_p_variance")],
      ["bp_p_table", "Plan vs Actual by Market & Platform"],
      ["bp_platform", "Pacing by Platform (This Month)"],
    ),
    P(
      "Measurement & Incrementality",
      "d7_measurement",
      "Measurement & Incrementality",
      [k("mi_iroas", "iROAS", "num", true, "mi_k_iroas"), k("mi_inc_revenue", "Incremental revenue", "money", true, "mi_k_rev")],
      [k("mi_tests", "Incrementality tests", "count", true, "mi_k_tests")],
      ["mi_table", "Test Results"],
      ["mi_scope", "iROAS by Campaign Scope"],
    ),
    P(
      "Arcane Operations",
      "d8_arcane_ops",
      "Arcane Operations",
      [k("op_requests", "Data requests", "count", false, "op_k_req"), k("op_days", "Avg days to deliver", "num", false, "op_k_days")],
      [k("op_open", "Open requests", "count", false, "op_k_open"), k("op_effort", "Effort hours", "num", false, "op_k_effort")],
      ["op_list", "Request Log"],
      ["op_days_type", "Days to Deliver by Request Type"],
    ),
  ].map((p) => [p.name, p]),
);

/** The persona's products that the app knows, in the persona's order. */
export const productsOf = (names: string[] | undefined) => (names || []).map((n) => PRODUCTS[n]).filter(Boolean) as Product[];

/** The Publisher report of the persona's first data product. */
export const reportOf = (names: string[] | undefined, fallback = "dp_paid_media_performance_report") => productsOf(names)[0]?.report || fallback;
