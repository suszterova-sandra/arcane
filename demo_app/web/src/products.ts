/**
 * Exzeo's standard content as the app uses it: the dashboards every carrier inherits from the Exzeo template,
 * their headline KPIs and the visualizations a number opens (analytics/dashboards, analytics/visualisations).
 * One AI Publisher report (business_performance_report) covers all of them.
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
  /** headline KPIs, most important first */
  kpis: ProductKpi[];
  /** secondary numbers for the watch list */
  watch: ProductKpi[];
  /** visualizations a key driver (product category / customer country) opens */
  byCategory: { viz: string; title: string };
  byCountry: { viz: string; title: string };
}

export const REPORT_ID = "business_performance_report";

const k = (metric: string, label: string, format: Format, goodWhenUp: boolean, viz: string): ProductKpi => ({ metric, label, format, goodWhenUp, viz });

const P = (name: string, dashboard: string, dashTitle: string, kpis: ProductKpi[], watch: ProductKpi[], byCategory: [string, string], byCountry: [string, string]): Product => ({
  name,
  dashboard,
  dashTitle,
  report: REPORT_ID,
  kpis,
  watch,
  byCategory: { viz: byCategory[0], title: byCategory[1] },
  byCountry: { viz: byCountry[0], title: byCountry[1] },
});

export const PRODUCTS: Record<string, Product> = Object.fromEntries(
  [
    P(
      "Business Overview",
      "overview",
      "Overview",
      [k("net_sales", "Net sales", "money", true, "net_sales_headline"), k("active_customers", "Active customers", "count", true, "active_customers_headline")],
      [k("gross_profit_margin", "Gross margin", "pct", true, "gross_profit_by_product_category"), k("order_cancellation_rate", "Cancellation rate", "pct", false, "completed_vs_canceled_orders_trend")],
      ["net_sales_by_product_category", "Net Sales by Product Category"],
      ["active_customers_by_country", "Active Customers by Country"],
    ),
    P(
      "Sales",
      "sales",
      "Sales",
      [k("net_orders", "Orders", "count", true, "orders_processed_headline"), k("gross_profit", "Gross profit", "money", true, "gross_profit_headline")],
      [k("average_order_volume", "Avg. order value", "money", true, "average_orders_breakdown")],
      ["sales_performance_by_product_category_over_time", "Sales by Product Category over Time"],
      ["top_10_customers_by_revenue", "Top 10 Customers by Revenue"],
    ),
    P(
      "Products",
      "products",
      "Products",
      [],
      [k("return_rate", "Return rate", "pct", false, "product_performance_by_orders_and_returns")],
      ["gross_profit_by_product_category", "Gross Profit by Product Category"],
      ["product_performance_by_orders_and_returns", "Product Performance by Orders & Returns"],
    ),
    P(
      "Customers",
      "customers",
      "Customers",
      [],
      [],
      ["product_preferences_by_customers", "Product Preferences by Customers"],
      ["customers_by_country_and_state", "Customers by Country and State"],
    ),
  ].map((p) => [p.name, p]),
);

/** The persona's products that the app knows, in the persona's order. */
export const productsOf = (names: string[] | undefined) => (names || []).map((n) => PRODUCTS[n]).filter(Boolean) as Product[];

/** The AI Publisher report (one for all standard dashboards). */
export const reportOf = (names: string[] | undefined, fallback = REPORT_ID) => productsOf(names)[0]?.report || fallback;
