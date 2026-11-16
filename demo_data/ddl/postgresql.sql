-- Arcane demo schema (GoodData Cloud). WDF column: wdf__client_id
-- Works for PostgreSQL and DuckDB / MotherDuck.

DROP TABLE IF EXISTS platforms;
CREATE TABLE platforms (
  platform_id VARCHAR(64) NOT NULL,
  platform_name VARCHAR(160) NOT NULL,
  platform_vendor VARCHAR(160) NOT NULL,
  platform_category VARCHAR(160) NOT NULL,
  arcane_practice VARCHAR(160) NOT NULL,
  adverity_connector VARCHAR(160) NOT NULL,
  is_paid VARCHAR(3) NOT NULL,
  PRIMARY KEY (platform_id)
);

DROP TABLE IF EXISTS markets;
CREATE TABLE markets (
  market_id VARCHAR(2) NOT NULL,
  country_name VARCHAR(160) NOT NULL,
  market_region VARCHAR(160) NOT NULL,
  currency_code VARCHAR(3) NOT NULL,
  eur_fx_rate NUMERIC(6,4) NOT NULL,
  language VARCHAR(160) NOT NULL,
  capital_city VARCHAR(160) NOT NULL,
  latitude NUMERIC(9,6) NOT NULL,
  longitude NUMERIC(9,6) NOT NULL,
  PRIMARY KEY (market_id)
);

DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
  client_id VARCHAR(64) NOT NULL,
  client_name VARCHAR(160) NOT NULL,
  industry VARCHAR(160) NOT NULL,
  business_model VARCHAR(160) NOT NULL,
  client_tier VARCHAR(160) NOT NULL,
  data_schema VARCHAR(160) NOT NULL,
  data_extensions VARCHAR(160) NOT NULL,
  primary_kpi VARCHAR(160) NOT NULL,
  primary_kpi_definition VARCHAR(160) NOT NULL,
  target_type VARCHAR(160) NOT NULL,
  target_value NUMERIC(12,2) NOT NULL,
  headquarters_city VARCHAR(160) NOT NULL,
  arcane_client_since DATE NOT NULL,
  media_consultant VARCHAR(160) NOT NULL,
  data_consultant VARCHAR(160) NOT NULL,
  monthly_budget_eur NUMERIC(14,2) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (client_id)
);

DROP TABLE IF EXISTS campaigns;
CREATE TABLE campaigns (
  campaign_id VARCHAR(64) NOT NULL,
  campaign_name VARCHAR(160) NOT NULL,
  client_id VARCHAR(64) NOT NULL,
  platform_id VARCHAR(64) NOT NULL,
  market_id VARCHAR(2) NOT NULL,
  campaign_type VARCHAR(160) NOT NULL,
  channel_group VARCHAR(160) NOT NULL,
  funnel_stage VARCHAR(160) NOT NULL,
  objective VARCHAR(160) NOT NULL,
  is_brand VARCHAR(3) NOT NULL,
  product_line VARCHAR(160) NOT NULL,
  bidding_strategy VARCHAR(160) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  campaign_status VARCHAR(160) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (campaign_id)
);

DROP TABLE IF EXISTS creatives;
CREATE TABLE creatives (
  creative_id VARCHAR(64) NOT NULL,
  creative_name VARCHAR(160) NOT NULL,
  campaign_id VARCHAR(64) NOT NULL,
  creative_format VARCHAR(160) NOT NULL,
  creative_theme VARCHAR(160) NOT NULL,
  production_source VARCHAR(160) NOT NULL,
  is_video VARCHAR(3) NOT NULL,
  launch_date DATE NOT NULL,
  end_date DATE NOT NULL,
  creative_status VARCHAR(160) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (creative_id)
);

DROP TABLE IF EXISTS products;
CREATE TABLE products (
  product_id VARCHAR(64) NOT NULL,
  sku VARCHAR(64) NOT NULL,
  product_title VARCHAR(160) NOT NULL,
  product_brand VARCHAR(160) NOT NULL,
  product_category VARCHAR(160) NOT NULL,
  product_subcategory VARCHAR(160) NOT NULL,
  product_condition VARCHAR(160) NOT NULL,
  price_eur NUMERIC(14,2) NOT NULL,
  margin_pct NUMERIC(6,4) NOT NULL,
  launch_date DATE NOT NULL,
  feed_optimized VARCHAR(3) NOT NULL,
  feed_optimized_date DATE NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (product_id)
);

DROP TABLE IF EXISTS business_locations;
CREATE TABLE business_locations (
  location_id VARCHAR(64) NOT NULL,
  location_name VARCHAR(160) NOT NULL,
  location_type VARCHAR(160) NOT NULL,
  city VARCHAR(160) NOT NULL,
  region VARCHAR(160) NOT NULL,
  country VARCHAR(160) NOT NULL,
  postal_code VARCHAR(10) NOT NULL,
  latitude NUMERIC(9,6) NOT NULL,
  longitude NUMERIC(9,6) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (location_id)
);

DROP TABLE IF EXISTS ad_performance_daily;
CREATE TABLE ad_performance_daily (
  performance_id VARCHAR(64) NOT NULL,
  campaign_id VARCHAR(64) NOT NULL,
  date DATE NOT NULL,
  device VARCHAR(160) NOT NULL,
  impressions BIGINT NOT NULL,
  clicks BIGINT NOT NULL,
  cost_eur NUMERIC(14,2) NOT NULL,
  cost_local_currency NUMERIC(14,2) NOT NULL,
  conversions NUMERIC(12,2) NOT NULL,
  conversion_value_eur NUMERIC(14,2) NOT NULL,
  video_views BIGINT NOT NULL,
  engagements BIGINT NOT NULL,
  search_impressions BIGINT NOT NULL,
  search_eligible_impressions BIGINT NOT NULL,
  search_lost_is_budget BIGINT NOT NULL,
  search_lost_is_rank BIGINT NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (performance_id)
);

DROP TABLE IF EXISTS creative_performance_daily;
CREATE TABLE creative_performance_daily (
  creative_performance_id VARCHAR(64) NOT NULL,
  creative_id VARCHAR(64) NOT NULL,
  date DATE NOT NULL,
  impressions BIGINT NOT NULL,
  clicks BIGINT NOT NULL,
  cost_eur NUMERIC(14,2) NOT NULL,
  video_3s_views BIGINT NOT NULL,
  thruplays BIGINT NOT NULL,
  engagements BIGINT NOT NULL,
  conversions NUMERIC(12,2) NOT NULL,
  conversion_value_eur NUMERIC(14,2) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (creative_performance_id)
);

DROP TABLE IF EXISTS product_performance_weekly;
CREATE TABLE product_performance_weekly (
  product_performance_id VARCHAR(64) NOT NULL,
  product_id VARCHAR(64) NOT NULL,
  campaign_id VARCHAR(64) NOT NULL,
  week_start_date DATE NOT NULL,
  impressions BIGINT NOT NULL,
  clicks BIGINT NOT NULL,
  cost_eur NUMERIC(14,2) NOT NULL,
  conversions NUMERIC(12,2) NOT NULL,
  conversion_value_eur NUMERIC(14,2) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (product_performance_id)
);

DROP TABLE IF EXISTS web_analytics_daily;
CREATE TABLE web_analytics_daily (
  web_id VARCHAR(64) NOT NULL,
  client_id VARCHAR(64) NOT NULL,
  market_id VARCHAR(2) NOT NULL,
  date DATE NOT NULL,
  channel_group VARCHAR(160) NOT NULL,
  is_paid_channel VARCHAR(3) NOT NULL,
  sessions BIGINT NOT NULL,
  engaged_sessions BIGINT NOT NULL,
  new_users BIGINT NOT NULL,
  transactions INTEGER NOT NULL,
  revenue_eur NUMERIC(14,2) NOT NULL,
  gross_margin_eur NUMERIC(14,2) NOT NULL,
  new_customers INTEGER NOT NULL,
  leads INTEGER NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (web_id)
);

DROP TABLE IF EXISTS crm_leads;
CREATE TABLE crm_leads (
  lead_id VARCHAR(64) NOT NULL,
  campaign_id VARCHAR(64) NOT NULL,
  location_id VARCHAR(64) NOT NULL,
  lead_date DATE NOT NULL,
  lead_type VARCHAR(160) NOT NULL,
  product_brand VARCHAR(160) NOT NULL,
  product_name VARCHAR(160) NOT NULL,
  product_line VARCHAR(160) NOT NULL,
  product_segment VARCHAR(160) NOT NULL,
  product_variant VARCHAR(160) NOT NULL,
  is_existing_customer VARCHAR(3) NOT NULL,
  lead_status VARCHAR(160) NOT NULL,
  contacted_date DATE NOT NULL,
  hours_to_first_contact NUMERIC(12,2) NOT NULL,
  opportunity_type VARCHAR(160) NOT NULL,
  opportunity_date DATE NOT NULL,
  won_date DATE NOT NULL,
  days_to_close INTEGER NOT NULL,
  deal_value_eur NUMERIC(14,2) NOT NULL,
  gross_profit_eur NUMERIC(14,2) NOT NULL,
  offline_conversion_uploaded VARCHAR(3) NOT NULL,
  is_qualified INTEGER NOT NULL,
  is_opportunity INTEGER NOT NULL,
  is_won INTEGER NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (lead_id)
);

DROP TABLE IF EXISTS media_budgets;
CREATE TABLE media_budgets (
  budget_id VARCHAR(64) NOT NULL,
  client_id VARCHAR(64) NOT NULL,
  platform_id VARCHAR(64) NOT NULL,
  market_id VARCHAR(2) NOT NULL,
  budget_month DATE NOT NULL,
  planned_budget_eur NUMERIC(14,2) NOT NULL,
  target_roas NUMERIC(12,2) NOT NULL,
  target_cpa_eur NUMERIC(12,2) NOT NULL,
  budget_owner VARCHAR(160) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (budget_id)
);

DROP TABLE IF EXISTS incrementality_tests;
CREATE TABLE incrementality_tests (
  test_id VARCHAR(64) NOT NULL,
  client_id VARCHAR(64) NOT NULL,
  platform_id VARCHAR(64) NOT NULL,
  market_id VARCHAR(2) NOT NULL,
  test_name VARCHAR(160) NOT NULL,
  campaign_scope VARCHAR(160) NOT NULL,
  methodology VARCHAR(160) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  test_status VARCHAR(160) NOT NULL,
  test_spend_eur NUMERIC(14,2) NOT NULL,
  platform_conversions NUMERIC(12,2) NOT NULL,
  incremental_conversions NUMERIC(12,2) NOT NULL,
  incremental_revenue_eur NUMERIC(14,2) NOT NULL,
  lift_pct NUMERIC(12,2) NOT NULL,
  iroas NUMERIC(12,2) NOT NULL,
  confidence_level NUMERIC(12,2) NOT NULL,
  is_significant VARCHAR(3) NOT NULL,
  recommendation VARCHAR(160) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (test_id)
);

DROP TABLE IF EXISTS data_requests;
CREATE TABLE data_requests (
  request_id VARCHAR(64) NOT NULL,
  client_id VARCHAR(64) NOT NULL,
  submitted_date DATE NOT NULL,
  requested_by_role VARCHAR(160) NOT NULL,
  request_channel VARCHAR(160) NOT NULL,
  request_type VARCHAR(160) NOT NULL,
  request_summary VARCHAR(160) NOT NULL,
  priority VARCHAR(160) NOT NULL,
  assigned_to VARCHAR(160) NOT NULL,
  request_status VARCHAR(160) NOT NULL,
  delivered_date DATE NOT NULL,
  days_to_deliver INTEGER NOT NULL,
  effort_hours NUMERIC(12,2) NOT NULL,
  is_delivered INTEGER NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (request_id)
);

DROP TABLE IF EXISTS client_data_products;
CREATE TABLE client_data_products (
  entitlement_id VARCHAR(64) NOT NULL,
  client_id VARCHAR(64) NOT NULL,
  data_product VARCHAR(160) NOT NULL,
  package VARCHAR(160) NOT NULL,
  audience VARCHAR(160) NOT NULL,
  is_enabled VARCHAR(3) NOT NULL,
  enabled_since DATE NOT NULL,
  user_group VARCHAR(64) NOT NULL,
  wdf__client_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (entitlement_id)
);

-- load (psql, run from demo_data/):
\copy platforms FROM 'csv/platforms.csv' WITH (FORMAT csv, HEADER true)
\copy markets FROM 'csv/markets.csv' WITH (FORMAT csv, HEADER true)
\copy clients FROM 'csv/clients.csv' WITH (FORMAT csv, HEADER true)
\copy campaigns FROM 'csv/campaigns.csv' WITH (FORMAT csv, HEADER true)
\copy creatives FROM 'csv/creatives.csv' WITH (FORMAT csv, HEADER true)
\copy products FROM 'csv/products.csv' WITH (FORMAT csv, HEADER true)
\copy business_locations FROM 'csv/business_locations.csv' WITH (FORMAT csv, HEADER true)
\copy ad_performance_daily FROM 'csv/ad_performance_daily.csv' WITH (FORMAT csv, HEADER true)
\copy creative_performance_daily FROM 'csv/creative_performance_daily.csv' WITH (FORMAT csv, HEADER true)
\copy product_performance_weekly FROM 'csv/product_performance_weekly.csv' WITH (FORMAT csv, HEADER true)
\copy web_analytics_daily FROM 'csv/web_analytics_daily.csv' WITH (FORMAT csv, HEADER true)
\copy crm_leads FROM 'csv/crm_leads.csv' WITH (FORMAT csv, HEADER true)
\copy media_budgets FROM 'csv/media_budgets.csv' WITH (FORMAT csv, HEADER true)
\copy incrementality_tests FROM 'csv/incrementality_tests.csv' WITH (FORMAT csv, HEADER true)
\copy data_requests FROM 'csv/data_requests.csv' WITH (FORMAT csv, HEADER true)
\copy client_data_products FROM 'csv/client_data_products.csv' WITH (FORMAT csv, HEADER true)
