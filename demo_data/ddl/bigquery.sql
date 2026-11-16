-- Arcane demo schema for BigQuery (Arcane's production warehouse). Dataset: arcane_demo
-- Load: bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.<table> csv/<table>.csv

CREATE OR REPLACE TABLE arcane_demo.platforms (
  platform_id STRING NOT NULL,
  platform_name STRING NOT NULL,
  platform_vendor STRING NOT NULL,
  platform_category STRING NOT NULL,
  arcane_practice STRING NOT NULL,
  adverity_connector STRING NOT NULL,
  is_paid STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.markets (
  market_id STRING NOT NULL,
  country_name STRING NOT NULL,
  market_region STRING NOT NULL,
  currency_code STRING NOT NULL,
  eur_fx_rate NUMERIC NOT NULL,
  language STRING NOT NULL,
  capital_city STRING NOT NULL,
  latitude NUMERIC NOT NULL,
  longitude NUMERIC NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.clients (
  client_id STRING NOT NULL,
  client_name STRING NOT NULL,
  industry STRING NOT NULL,
  business_model STRING NOT NULL,
  client_tier STRING NOT NULL,
  data_schema STRING NOT NULL,
  data_extensions STRING NOT NULL,
  primary_kpi STRING NOT NULL,
  primary_kpi_definition STRING NOT NULL,
  target_type STRING NOT NULL,
  target_value NUMERIC NOT NULL,
  headquarters_city STRING NOT NULL,
  arcane_client_since DATE NOT NULL,
  media_consultant STRING NOT NULL,
  data_consultant STRING NOT NULL,
  monthly_budget_eur NUMERIC NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.campaigns (
  campaign_id STRING NOT NULL,
  campaign_name STRING NOT NULL,
  client_id STRING NOT NULL,
  platform_id STRING NOT NULL,
  market_id STRING NOT NULL,
  campaign_type STRING NOT NULL,
  channel_group STRING NOT NULL,
  funnel_stage STRING NOT NULL,
  objective STRING NOT NULL,
  is_brand STRING NOT NULL,
  product_line STRING NOT NULL,
  bidding_strategy STRING NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  campaign_status STRING NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.creatives (
  creative_id STRING NOT NULL,
  creative_name STRING NOT NULL,
  campaign_id STRING NOT NULL,
  creative_format STRING NOT NULL,
  creative_theme STRING NOT NULL,
  production_source STRING NOT NULL,
  is_video STRING NOT NULL,
  launch_date DATE NOT NULL,
  end_date DATE NOT NULL,
  creative_status STRING NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.products (
  product_id STRING NOT NULL,
  sku STRING NOT NULL,
  product_title STRING NOT NULL,
  product_brand STRING NOT NULL,
  product_category STRING NOT NULL,
  product_subcategory STRING NOT NULL,
  product_condition STRING NOT NULL,
  price_eur NUMERIC NOT NULL,
  margin_pct NUMERIC NOT NULL,
  launch_date DATE NOT NULL,
  feed_optimized STRING NOT NULL,
  feed_optimized_date DATE NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.business_locations (
  location_id STRING NOT NULL,
  location_name STRING NOT NULL,
  location_type STRING NOT NULL,
  city STRING NOT NULL,
  region STRING NOT NULL,
  country STRING NOT NULL,
  postal_code STRING NOT NULL,
  latitude NUMERIC NOT NULL,
  longitude NUMERIC NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.ad_performance_daily (
  performance_id STRING NOT NULL,
  campaign_id STRING NOT NULL,
  date DATE NOT NULL,
  device STRING NOT NULL,
  impressions INT64 NOT NULL,
  clicks INT64 NOT NULL,
  cost_eur NUMERIC NOT NULL,
  cost_local_currency NUMERIC NOT NULL,
  conversions NUMERIC NOT NULL,
  conversion_value_eur NUMERIC NOT NULL,
  video_views INT64 NOT NULL,
  engagements INT64 NOT NULL,
  search_impressions INT64 NOT NULL,
  search_eligible_impressions INT64 NOT NULL,
  search_lost_is_budget INT64 NOT NULL,
  search_lost_is_rank INT64 NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.creative_performance_daily (
  creative_performance_id STRING NOT NULL,
  creative_id STRING NOT NULL,
  date DATE NOT NULL,
  impressions INT64 NOT NULL,
  clicks INT64 NOT NULL,
  cost_eur NUMERIC NOT NULL,
  video_3s_views INT64 NOT NULL,
  thruplays INT64 NOT NULL,
  engagements INT64 NOT NULL,
  conversions NUMERIC NOT NULL,
  conversion_value_eur NUMERIC NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.product_performance_weekly (
  product_performance_id STRING NOT NULL,
  product_id STRING NOT NULL,
  campaign_id STRING NOT NULL,
  week_start_date DATE NOT NULL,
  impressions INT64 NOT NULL,
  clicks INT64 NOT NULL,
  cost_eur NUMERIC NOT NULL,
  conversions NUMERIC NOT NULL,
  conversion_value_eur NUMERIC NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.web_analytics_daily (
  web_id STRING NOT NULL,
  client_id STRING NOT NULL,
  market_id STRING NOT NULL,
  date DATE NOT NULL,
  channel_group STRING NOT NULL,
  is_paid_channel STRING NOT NULL,
  sessions INT64 NOT NULL,
  engaged_sessions INT64 NOT NULL,
  new_users INT64 NOT NULL,
  transactions INT64 NOT NULL,
  revenue_eur NUMERIC NOT NULL,
  gross_margin_eur NUMERIC NOT NULL,
  new_customers INT64 NOT NULL,
  leads INT64 NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.crm_leads (
  lead_id STRING NOT NULL,
  campaign_id STRING NOT NULL,
  location_id STRING NOT NULL,
  lead_date DATE NOT NULL,
  lead_type STRING NOT NULL,
  product_brand STRING NOT NULL,
  product_name STRING NOT NULL,
  product_line STRING NOT NULL,
  product_segment STRING NOT NULL,
  product_variant STRING NOT NULL,
  is_existing_customer STRING NOT NULL,
  lead_status STRING NOT NULL,
  contacted_date DATE NOT NULL,
  hours_to_first_contact NUMERIC NOT NULL,
  opportunity_type STRING NOT NULL,
  opportunity_date DATE NOT NULL,
  won_date DATE NOT NULL,
  days_to_close INT64 NOT NULL,
  deal_value_eur NUMERIC NOT NULL,
  gross_profit_eur NUMERIC NOT NULL,
  offline_conversion_uploaded STRING NOT NULL,
  is_qualified INT64 NOT NULL,
  is_opportunity INT64 NOT NULL,
  is_won INT64 NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.media_budgets (
  budget_id STRING NOT NULL,
  client_id STRING NOT NULL,
  platform_id STRING NOT NULL,
  market_id STRING NOT NULL,
  budget_month DATE NOT NULL,
  planned_budget_eur NUMERIC NOT NULL,
  target_roas NUMERIC NOT NULL,
  target_cpa_eur NUMERIC NOT NULL,
  budget_owner STRING NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.incrementality_tests (
  test_id STRING NOT NULL,
  client_id STRING NOT NULL,
  platform_id STRING NOT NULL,
  market_id STRING NOT NULL,
  test_name STRING NOT NULL,
  campaign_scope STRING NOT NULL,
  methodology STRING NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  test_status STRING NOT NULL,
  test_spend_eur NUMERIC NOT NULL,
  platform_conversions NUMERIC NOT NULL,
  incremental_conversions NUMERIC NOT NULL,
  incremental_revenue_eur NUMERIC NOT NULL,
  lift_pct NUMERIC NOT NULL,
  iroas NUMERIC NOT NULL,
  confidence_level NUMERIC NOT NULL,
  is_significant STRING NOT NULL,
  recommendation STRING NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.data_requests (
  request_id STRING NOT NULL,
  client_id STRING NOT NULL,
  submitted_date DATE NOT NULL,
  requested_by_role STRING NOT NULL,
  request_channel STRING NOT NULL,
  request_type STRING NOT NULL,
  request_summary STRING NOT NULL,
  priority STRING NOT NULL,
  assigned_to STRING NOT NULL,
  request_status STRING NOT NULL,
  delivered_date DATE NOT NULL,
  days_to_deliver INT64 NOT NULL,
  effort_hours NUMERIC NOT NULL,
  is_delivered INT64 NOT NULL,
  wdf__client_id STRING NOT NULL
);

CREATE OR REPLACE TABLE arcane_demo.client_data_products (
  entitlement_id STRING NOT NULL,
  client_id STRING NOT NULL,
  data_product STRING NOT NULL,
  package STRING NOT NULL,
  audience STRING NOT NULL,
  is_enabled STRING NOT NULL,
  enabled_since DATE NOT NULL,
  user_group STRING NOT NULL,
  wdf__client_id STRING NOT NULL
);

-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.platforms csv/platforms.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.markets csv/markets.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.clients csv/clients.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.campaigns csv/campaigns.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.creatives csv/creatives.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.products csv/products.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.business_locations csv/business_locations.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.ad_performance_daily csv/ad_performance_daily.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.creative_performance_daily csv/creative_performance_daily.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.product_performance_weekly csv/product_performance_weekly.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.web_analytics_daily csv/web_analytics_daily.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.crm_leads csv/crm_leads.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.media_budgets csv/media_budgets.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.incrementality_tests csv/incrementality_tests.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.data_requests csv/data_requests.csv
-- bq load --source_format=CSV --skip_leading_rows=1 arcane_demo.client_data_products csv/client_data_products.csv
