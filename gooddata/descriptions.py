"""
Hand-written descriptions of every attribute, label and fact of the Arcane model (key = "<dataset>.<column>").
The AI assistant reads them, so they say what the field means, its values / unit, and how to use it.
build_analytics.py fails if a field has no description here.
"""

DESC = {
    # ---- Platforms (global) ----
    "platforms.platform_id": "Technical ID of the advertising platform (e.g. google_ads, meta_ads). Use Platform Name for display.",
    "platforms.platform_id.platform_name": "Advertising platform: Google Ads, Microsoft Advertising, Meta Ads, TikTok Ads, LinkedIn Ads, "
                                           "Pinterest Ads, Amazon Ads, Display & Video 360, or Non-paid (Organic / Direct) for CRM leads "
                                           "that did not come from ads.",
    "platforms.platform_vendor": "Company that owns the platform (Google, Microsoft, Meta, TikTok, LinkedIn, Pinterest, Amazon).",
    "platforms.platform_category": "Type of media the platform sells: Search, Shopping & Video; Search & Shopping; Social; Retail "
                                   "Media; Programmatic; Non-paid.",
    "platforms.arcane_practice": "Arcane team that operates the platform: SEA (search), SMA (social), Retail Media, Programmatic & "
                                 "Video, SEO / CRM.",
    "platforms.adverity_connector": "Adverity connector that loads the platform's data into BigQuery.",
    "platforms.is_paid": "Yes for paid advertising platforms, No for the non-paid (organic / direct) source.",
    # ---- Markets (global) ----
    "markets.market_id": "ISO country code of the market the campaign targets (FR, DE, ES, IT, GB, US). Use Country for display.",
    "markets.market_id.country_name": "Country the campaign targets.",
    "markets.market_region": "Group of markets: France, DACH, Southern Europe, UK & Ireland, North America.",
    "markets.currency_code": "Local currency of the market (EUR, GBP, USD). Costs are reported in EUR and in local currency.",
    "markets.language": "Main language of the market, used for campaign and creative localisation.",
    "markets.capital_city": "Capital city of the market.",
    "markets.eur_fx_rate": "Exchange rate from EUR to the market's local currency (local = EUR x rate). 1.0 for euro markets.",
    # ---- Clients ----
    "clients.client_id": "ID of Arcane's client (advertiser) = the client workspace ID and the data filter value "
                         "(secondevie, autonova, routeo). Use Client Name for display.",
    "clients.client_id.client_name": "Arcane's client (advertiser): Seconde Vie, AutoNova Automobiles, Routéo Location.",
    "clients.industry": "Client's industry (Refurbished Electronics, Automotive Dealer Network, Car & Van Rental).",
    "clients.business_model": "How the client makes money online: e-commerce marketplace, lead generation with offline sales, "
                              "online bookings.",
    "clients.client_tier": "Arcane account tier: Top Account (custom data recipe, premium add-ons) or Standard (long-tail, "
                           "standard schema).",
    "clients.data_schema": "Whether the client runs on the standard long-tail schema or a custom top-account recipe.",
    "clients.data_extensions": "Data the client has on top of the standard media data, e.g. product feed, CRM, incrementality tests.",
    "clients.primary_kpi": "The client's own name for its main business KPI (e.g. Commandes (GMV), Lead qualifié / Véhicule vendu, "
                           "Réservations).",
    "clients.primary_kpi_definition": "The client's business definition of its main KPI - use it to interpret 'sales' or "
                                      "'conversions' for this client.",
    "clients.target_type": "Which efficiency target the client is managed on: Target ROAS or Target CPA.",
    "clients.headquarters_city": "City of the client's headquarters.",
    "clients.media_consultant": "Arcane media consultant responsible for the client's campaigns.",
    "clients.data_consultant": "Arcane data consultant responsible for the client's data and reporting.",
    "clients.target_value": "Value of the client's target: a ROAS multiple (e.g. 6.0) or a CPA in EUR (e.g. 45), see Target Type.",
    "clients.monthly_budget_eur": "Client's current average monthly media budget managed by Arcane, in EUR.",
    # ---- Campaigns ----
    "campaigns.campaign_id": "Platform campaign ID. Use Campaign Name for display.",
    "campaigns.campaign_id.campaign_name": "Campaign name in Arcane's naming convention CLIENT_MARKET_PLATFORM_TYPE_LINE, e.g. "
                                           "SV_DE_GADS_SEA_Generic_Smar = Seconde Vie, Germany, Google Ads, generic search, "
                                           "smartphones.",
    "campaigns.campaign_type": "Campaign type, e.g. Search - Brand, Search - Generic, Performance Max, Shopping, Meta - "
                               "Prospecting, Meta - Retargeting, TikTok - Spark Ads, LinkedIn - Lead Gen Forms, YouTube, "
                               "Amazon - Sponsored Products.",
    "campaigns.channel_group": "Marketing channel of the campaign: Paid Search, Paid Shopping, Paid Social, Paid Video & "
                               "Display, Retail Media, Organic & Direct.",
    "campaigns.funnel_stage": "Funnel stage the campaign serves: Awareness, Consideration or Conversion.",
    "campaigns.objective": "Optimisation goal: Sales, Leads, Conversions, Catalog Sales, Traffic or Reach. Lead-gen cost metrics use "
                           "campaigns with objective Leads.",
    "campaigns.is_brand": "Yes for brand search campaigns (bidding on the client's own brand name).",
    "campaigns.product_line": "Product line the campaign promotes (e.g. Smartphones, Used Cars, Airport Rental); All Products for "
                              "campaigns covering the whole catalogue.",
    "campaigns.bidding_strategy": "Bidding strategy of the campaign, e.g. Target ROAS, Maximize Conversions, Cost Cap, Target CPM.",
    "campaigns.campaign_status": "Active, Removed (migrated to PMax) for Standard Shopping stopped in March 2025, or Always on for "
                                 "non-paid sources.",
    # ---- Ad performance ----
    "ad_performance_daily.performance_id": "Technical ID of one row: campaign x day x device.",
    "ad_performance_daily.device": "Device the ad was shown on: Mobile, Desktop, Tablet or Connected TV.",
    "ad_performance_daily.impressions": "Number of times the ads were shown.",
    "ad_performance_daily.clicks": "Number of clicks on the ads.",
    "ad_performance_daily.cost_eur": "Media spend in EUR (converted from the local currency).",
    "ad_performance_daily.cost_local_currency": "Media spend in the market's local currency (see Currency).",
    "ad_performance_daily.conversions": "Conversions as reported by the ad platform (orders, bookings or leads depending on the "
                                        "client), with the platform's attribution - can be fractional (data-driven attribution) "
                                        "and over-counts versus the backend.",
    "ad_performance_daily.conversion_value_eur": "Conversion value reported by the ad platform in EUR (order value, booking value or "
                                                 "lead value).",
    "ad_performance_daily.video_views": "Video views of video campaigns (YouTube, Demand Gen, DV360).",
    "ad_performance_daily.engagements": "Engagements on video campaigns (likes, shares, clicks on overlays).",
    "ad_performance_daily.search_impressions": "Impressions of search and shopping campaigns (0 for other campaign types); numerator "
                                               "of Search Impression Share.",
    "ad_performance_daily.search_eligible_impressions": "Impressions the search campaign was eligible for in the auction; "
                                                        "denominator of Search Impression Share.",
    "ad_performance_daily.search_lost_is_budget": "Eligible search impressions lost because the campaign budget ran out.",
    "ad_performance_daily.search_lost_is_rank": "Eligible search impressions lost because of ad rank (bid too low or low quality).",
    # ---- Creatives ----
    "creatives.creative_id": "ID of the social ad creative. Use Creative Name for display.",
    "creatives.creative_id.creative_name": "Creative name in Arcane's convention CLIENT_MARKET_FORMAT_THEME_LAUNCHDATE_VERSION.",
    "creatives.creative_format": "Ad format, e.g. UGC Video, Reels Video, Static Image, Carousel, Collection, Spark Ad (Creator), "
                                 "Lead Form, Document Ad.",
    "creatives.creative_theme": "Message of the creative: Product Showcase, Promo / Offer, Brand Story, Testimonial / Review, "
                                "Seasonal, How-to / Tutorial.",
    "creatives.production_source": "Who made the creative: In-house Studio, UGC Creator, Agency Design or AI-generated (Arcane AI "
                                   "Lab, since June 2025).",
    "creatives.is_video": "Yes for video creatives (only videos have 3-second views and ThruPlays).",
    "creatives.creative_status": "Active if the creative is still running, otherwise Paused.",
    # ---- Creative performance ----
    "creative_performance_daily.creative_performance_id": "Technical ID of one row: creative x day.",
    "creative_performance_daily.impressions": "Impressions of the creative.",
    "creative_performance_daily.clicks": "Clicks on the creative.",
    "creative_performance_daily.cost_eur": "Spend on the creative in EUR. Sums to the cost of its social campaign.",
    "creative_performance_daily.video_3s_views": "Video views of at least 3 seconds (hook); numerator of Thumb-stop Rate.",
    "creative_performance_daily.thruplays": "Video views to 15 seconds or to completion; used for Hold Rate.",
    "creative_performance_daily.engagements": "Reactions, comments, shares and saves on the creative.",
    "creative_performance_daily.conversions": "Platform-reported conversions attributed to the creative.",
    "creative_performance_daily.conversion_value_eur": "Platform-reported conversion value attributed to the creative, in EUR.",
    # ---- Products ----
    "products.product_id": "ID of the product in the client's product feed. Use Product Title for display.",
    "products.product_id.product_title": "Product title as sent in the feed (e.g. 'Apple iPhone 14 - 128 Go - Très bon état').",
    "products.sku": "Client's SKU of the product.",
    "products.product_brand": "Manufacturer brand of the product (Apple, Samsung, Sony, ...).",
    "products.product_category": "Product category (Smartphones, Laptops, Tablets, Gaming Consoles, Smartwatches & Audio).",
    "products.product_subcategory": "Product subcategory (for refurbished electronics: the brand family).",
    "products.product_condition": "Product condition, e.g. Refurbished - Parfait état / Très bon état / Bon état.",
    "products.feed_optimized": "Yes if the product's feed entry was optimised with Arcane SmartFeeds (titles, attributes); "
                               "compare product CTR of Yes vs No.",
    "products.price_eur": "Current selling price of the product in EUR.",
    "products.margin_pct": "Gross margin of the product as a share of the price (0.22 = 22%).",
    # ---- Product performance ----
    "product_performance_weekly.product_performance_id": "Technical ID of one row: product x campaign x week.",
    "product_performance_weekly.impressions": "Product-ad impressions in the week.",
    "product_performance_weekly.clicks": "Product-ad clicks in the week.",
    "product_performance_weekly.cost_eur": "Product-ad spend in EUR in the week.",
    "product_performance_weekly.conversions": "Platform-reported conversions of the product in the week.",
    "product_performance_weekly.conversion_value_eur": "Platform-reported conversion value of the product in EUR in the week.",
    # ---- Web analytics ----
    "web_analytics_daily.web_id": "Technical ID of one row: client x market x day x channel group.",
    "web_analytics_daily.channel_group": "Website traffic channel (GA4): Paid Search, Paid Shopping, Paid Social, Paid Video & "
                                         "Display, Organic Search, Direct, Email & CRM, Referral, Affiliates, Organic Social, "
                                         "AI Assistants (ChatGPT, Perplexity, Gemini).",
    "web_analytics_daily.is_paid_channel": "Yes for paid media channels, No for organic, direct, email, referral, affiliates and "
                                           "AI assistants.",
    "web_analytics_daily.sessions": "Website sessions (GA4).",
    "web_analytics_daily.engaged_sessions": "Sessions longer than 10 seconds, with a conversion or with 2+ page views (GA4).",
    "web_analytics_daily.new_users": "First-time visitors (GA4).",
    "web_analytics_daily.transactions": "Orders or bookings recorded in the client's backend, de-duplicated across channels "
                                        "(0 for AutoNova, which sells offline).",
    "web_analytics_daily.revenue_eur": "Revenue of backend transactions in EUR - the client's source of truth.",
    "web_analytics_daily.gross_margin_eur": "Gross margin of backend revenue in EUR.",
    "web_analytics_daily.new_customers": "Backend transactions from first-time customers.",
    "web_analytics_daily.leads": "Lead form submissions on the website (AutoNova).",
    # ---- Business locations ----
    "business_locations.location_id": "ID of the business location that handles CRM leads. Use Location Name for display.",
    "business_locations.location_id.location_name": "Dealership (AutoNova) or B2B sales office (Seconde Vie Pro) handling the lead.",
    "business_locations.location_id.latitude": "Latitude of the location, for maps.",
    "business_locations.location_id.longitude": "Longitude of the location, for maps.",
    "business_locations.location_type": "Dealership - Flagship / Showroom / Used Car Center, or B2B Sales Office.",
    "business_locations.city": "City of the location.",
    "business_locations.region": "Region of the location (e.g. Auvergne-Rhône-Alpes, DACH).",
    "business_locations.country": "Country of the location.",
    # ---- CRM leads ----
    "crm_leads.lead_id": "ID of the lead in the client's CRM.",
    "crm_leads.lead_type": "What the prospect asked for, e.g. Test Drive Request, Quote Request, Trade-in Valuation (AutoNova); "
                           "Fleet Quote Request, Contact Sales (Seconde Vie Pro).",
    "crm_leads.product_brand": "Brand of the product the lead is interested in (vehicle make or device brand).",
    "crm_leads.product_name": "Product the lead is interested in (vehicle model, or device model for B2B fleets).",
    "crm_leads.product_line": "Product line of the lead (New Cars, Used Cars, Electric & Hybrid, Utility Vans; Laptops, "
                              "Smartphones, Tablets).",
    "crm_leads.product_segment": "Segment of the lead: vehicle body type (City Car, SUV, Compact, Van) or company size for B2B "
                                 "(SMB, Mid-market, Enterprise).",
    "crm_leads.product_variant": "Variant: fuel type for vehicles (Petrol, Diesel, Hybrid, Electric) or number of devices for B2B.",
    "crm_leads.is_existing_customer": "Yes if the lead is already a customer of the client.",
    "crm_leads.lead_status": "Current CRM status: New, Open - ..., Sold / Won, Lost - ... (reason) or Disqualified - Duplicate / "
                             "Spam.",
    "crm_leads.opportunity_type": "What counts as an opportunity for the client: Test Drive (AutoNova) or Quote Sent (Seconde Vie Pro).",
    "crm_leads.offline_conversion_uploaded": "Yes if the won deal was sent back to the ad platform as an offline conversion "
                                             "(Arcane SmartConversion).",
    "crm_leads.hours_to_first_contact": "Hours between lead creation and the first contact by sales.",
    "crm_leads.days_to_close": "Days from lead creation to the won deal (0 if not won).",
    "crm_leads.deal_value_eur": "Value of the won deal in EUR (vehicle price, or device fleet order value). 0 if not won.",
    "crm_leads.gross_profit_eur": "Gross profit of the won deal in EUR. 0 if not won.",
    "crm_leads.is_qualified": "1 if sales qualified the lead, else 0. Sum it to count qualified leads.",
    "crm_leads.is_opportunity": "1 if the lead reached an opportunity (test drive done / quote sent), else 0.",
    "crm_leads.is_won": "1 if the lead was won (car sold / B2B deal signed), else 0.",
    # ---- Media budgets ----
    "media_budgets.budget_id": "Technical ID of a media plan line: client x platform x market x month.",
    "media_budgets.budget_owner": "Arcane media consultant who owns the media plan line.",
    "media_budgets.planned_budget_eur": "Planned media budget for the month in EUR (media plan). Compare with Cost for pacing.",
    "media_budgets.target_roas": "ROAS target of the plan line (0 when the client is managed on CPA).",
    "media_budgets.target_cpa_eur": "CPA target of the plan line in EUR (0 when the client is managed on ROAS).",
    # ---- Incrementality tests ----
    "incrementality_tests.test_id": "ID of the incrementality test.",
    "incrementality_tests.test_id.test_name": "Name of the test: client, market, campaign scope and method.",
    "incrementality_tests.campaign_scope": "Campaign type that was tested (e.g. Meta - Retargeting, Search - Brand, Performance Max).",
    "incrementality_tests.methodology": "Test method: Geo-lift (synthetic control), Geo Holdout, Conversion Lift (platform "
                                        "holdout), Brand Lift, Geo-lift on CRM sales.",
    "incrementality_tests.test_status": "Completed or Running (results pending).",
    "incrementality_tests.is_significant": "Yes if the result is statistically significant (confidence >= 90%).",
    "incrementality_tests.recommendation": "Arcane's budget recommendation based on the result.",
    "incrementality_tests.test_spend_eur": "Media spend in the test cells during the test, in EUR.",
    "incrementality_tests.platform_conversions": "Conversions the platform reported for the tested campaigns during the test.",
    "incrementality_tests.incremental_conversions": "Conversions that would not have happened without the media (measured lift).",
    "incrementality_tests.incremental_revenue_eur": "Revenue (or gross profit for AutoNova) caused by the media, in EUR.",
    "incrementality_tests.lift_pct": "Measured lift of the test region versus control, in percent.",
    "incrementality_tests.iroas": "Incremental ROAS = incremental revenue / test spend. Below 1 the channel does not pay back.",
    "incrementality_tests.confidence_level": "Statistical confidence of the result (0.92 = 92%).",
    # ---- Data requests ----
    "data_requests.request_id": "ID of the data request.",
    "data_requests.request_id.request_summary": "What was asked, e.g. 'Why did ROAS drop in DE last week?'.",
    "data_requests.requested_by_role": "Who asked: the Client or an Arcane Media Consultant.",
    "data_requests.request_channel": "How the request arrived: Google Form, Email or Slack.",
    "data_requests.request_type": "Kind of request: New KPI / metric, New breakdown / filter, New data source, Data discrepancy, "
                                  "Ad-hoc deep dive, Performance report (slides), Access request.",
    "data_requests.priority": "Priority of the request: Low, Medium, High, Urgent.",
    "data_requests.assigned_to": "Arcane data consultant who handles the request.",
    "data_requests.request_status": "Delivered, In Progress, Backlog or Rejected.",
    "data_requests.days_to_deliver": "Days from submission to delivery (0 if not delivered yet).",
    "data_requests.effort_hours": "Consultant hours spent on the request.",
    "data_requests.is_delivered": "1 if the request was delivered, else 0.",
    # ---- Client data products ----
    "client_data_products.entitlement_id": "Technical ID: client x data product.",
    "client_data_products.data_product": "Data product (module of the shared model / dashboard), e.g. Paid Media Performance, "
                                         "CRM & Offline Sales.",
    "client_data_products.package": "Package of the data product: Core, Standard, Premium add-on or Internal.",
    "client_data_products.audience": "Who may see the data product: Client + Arcane, or Arcane only.",
    "client_data_products.is_enabled": "Yes if the client has the data product (its users are put in the product's user group).",
    "client_data_products.user_group": "GoodData user group that grants access to the data product (dp_...).",
}

DATE_DESC = {
    "activity_date": "Main date of every dataset, so one date filter works across dashboards: the performance day "
                     "(ads, creatives, web analytics), the week start (product performance), the lead creation date (CRM), "
                     "the plan month (media budgets), the test start date (incrementality) and the submission date "
                     "(data requests). Data ends yesterday; the current week and month are partial.",
    "won_date": "Date a CRM lead was won: car sold (AutoNova) or B2B deal signed (Seconde Vie Pro). Use it to report won "
                "deals and deal value by the month they closed; 1900-01-01 means not won.",
}

# ---------------------------------------------------------------------------
# Metrics: definition, formula, unit / direction, caveats
# ---------------------------------------------------------------------------
METRIC_DESC = {
    # Paid Media Performance (Core)
    "pm_cost": "Media spend in EUR across all ad platforms (converted from local currency). Sum of Cost (EUR). "
               "Use it as the denominator of ROAS, CPA, MER and pacing.",
    "pm_impressions": "Number of times the ads were shown, across all platforms and campaign types.",
    "pm_clicks": "Number of clicks on the ads, across all platforms and campaign types.",
    "pm_conversions": "Conversions reported by the ad platforms with their own attribution: orders (Seconde Vie), bookings "
                      "(Routéo) or leads (AutoNova, Seconde Vie Pro). Over-counts versus the backend; do not add across "
                      "clients with different KPIs.",
    "pm_conv_value": "Conversion value reported by the ad platforms in EUR (order value, booking value or lead value). "
                     "Higher than backend revenue because of platform over-attribution.",
    "pm_video_views": "Video views of YouTube, Demand Gen and DV360 campaigns.",
    "pm_search_impr": "Impressions of search and shopping campaigns only - numerator of Search Impression Share.",
    "pm_search_eligible": "Impressions the search and shopping campaigns were eligible for in the auction - denominator of "
                          "Search Impression Share.",
    "pm_search_lost_budget": "Eligible search impressions lost because the campaign budget ran out.",
    "pm_search_lost_rank": "Eligible search impressions lost because of ad rank (bid too low or low ad quality).",
    "pm_ctr": "Click-through rate = Clicks / Impressions. Higher is better; compare within the same campaign type "
              "(search CTRs are much higher than display or video).",
    "pm_cpc": "Cost per click = Cost / Clicks, in EUR. Lower is better; rising CPC usually means more competition.",
    "pm_cpm": "Cost per 1,000 impressions = Cost / Impressions x 1000, in EUR. The price of reach; key for video and social.",
    "pm_cvr": "Conversion rate = Platform Conversions / Clicks. Higher is better; a drop with stable traffic points to the "
              "site, the offer or tracking.",
    "pm_cpa": "Cost per acquisition = Cost / Platform Conversions, in EUR - cost per order, booking or lead depending on the "
              "client. Lower is better; compare with the client's Target CPA.",
    "pm_roas": "Return on ad spend = Platform Conversion Value / Cost (e.g. 6.0x = EUR 6 of value per EUR 1 spent). Higher is "
               "better; compare with the client's Target ROAS. Platform-reported, so higher than Backend ROAS.",
    "pm_search_is": "Search Impression Share = Search Impressions / Search Eligible Impressions. Higher is better; brand search "
                    "should be above 90%.",
    "pm_lost_is_budget": "Share of eligible search impressions lost because of budget caps = Lost to Budget / Eligible. A jump "
                         "means the campaigns are budget-limited - check pacing.",
    "pm_lost_is_rank": "Share of eligible search impressions lost because of ad rank = Lost to Rank / Eligible. A jump means "
                       "bids or ad quality are too low versus competitors.",
    "pm_active_campaigns": "Number of campaigns with impressions or spend in the period.",
    # Social Creatives
    "sc_spend": "Spend on social creatives (Meta, TikTok, LinkedIn) in EUR. Equals the cost of the social campaigns.",
    "sc_impressions": "Impressions of social creatives.",
    "sc_clicks": "Clicks on social creatives.",
    "sc_conversions": "Platform-reported conversions attributed to social creatives.",
    "sc_conv_value": "Platform-reported conversion value attributed to social creatives, in EUR.",
    "sc_vv3": "Video views of at least 3 seconds - how many people the video's first seconds (hook) stopped.",
    "sc_thruplays": "Video views to 15 seconds or to completion.",
    "sc_ctr": "Social click-through rate = Social Clicks / Social Impressions. Falling CTR on an old creative signals "
              "creative fatigue.",
    "sc_cpa": "Social cost per conversion = Social Spend / Social Conversions, in EUR. Lower is better.",
    "sc_roas": "Social ROAS = Social Conversion Value / Social Spend. Platform-reported; social over-attributes the most.",
    "sc_thumbstop": "Thumb-stop rate = 3-second Video Views / Social Impressions - strength of the video hook. Higher is better; "
                    "only meaningful for video creatives.",
    "sc_hold": "Hold rate = ThruPlays / 3-second Video Views - how well the video keeps attention after the hook. Higher is "
               "better.",
    "sc_creatives": "Number of creatives that delivered impressions in the period.",
    # Web Analytics & GEO
    "wa_sessions": "Website sessions from GA4, all channels.",
    "wa_transactions": "Orders or bookings recorded in the client's backend, de-duplicated across channels - the client's "
                       "source of truth (0 for AutoNova, which sells offline).",
    "wa_revenue": "Revenue of backend transactions in EUR, all channels - the client's source of truth for sales.",
    "wa_margin": "Gross margin of backend revenue in EUR.",
    "wa_new_customers": "Backend transactions from first-time customers.",
    "wa_leads": "Lead form submissions on the website (AutoNova). Qualified leads and sales are in CRM & Offline Sales.",
    "wa_cvr": "Site conversion rate = Backend Transactions / Sessions. Higher is better.",
    "wa_aov": "Average order value = Backend Revenue / Backend Transactions, in EUR.",
    "wa_paid_revenue": "Backend revenue from paid media channels (Paid Search, Shopping, Social, Video & Display), "
                       "de-duplicated - what paid media really sold.",
    "wa_paid_transactions": "Backend transactions from paid media channels, de-duplicated.",
    "wa_paid_share": "Share of backend revenue coming from paid media = Paid Media Revenue / Backend Revenue.",
    "wa_mer": "Marketing efficiency ratio (blended ROAS) = total Backend Revenue / total media Cost. The board-level "
              "efficiency KPI; higher is better.",
    "wa_paid_roas": "Backend ROAS = Paid Media Revenue (backend) / Cost. The de-duplicated alternative to platform ROAS; use it "
                    "for budget decisions.",
    "wa_overattribution": "Platform over-attribution = Platform Conversion Value / Paid Media Revenue (backend). 1.0x means the "
                          "platforms agree with the backend; 1.5x means they claim 50% more than really happened.",
    "wa_ai_sessions": "Sessions referred by AI assistants (ChatGPT, Perplexity, Gemini) - the GEO channel Arcane optimises.",
    "wa_ai_share": "AI assistant share of sessions = AI Assistant Sessions / Sessions. Shows how fast AI search is growing as a "
                   "traffic source.",
    # Budget & Pacing
    "bp_planned": "Planned media budget in EUR from the media plan (client x platform x market x month).",
    "bp_pacing": "Budget pacing = Cost / Planned Budget. 100% = on plan. For the current month compare with the share of the "
                 "month elapsed: below it is under-spending, above it over-spending.",
    "bp_variance": "Budget variance = Cost - Planned Budget, in EUR. Negative = under-spending versus plan.",
    "bp_remaining": "Remaining budget = Planned Budget - Cost, in EUR - what is left to spend in the period.",
    "bp_target_roas": "ROAS target from the media plan (average of the plan lines; 0 when the client is managed on CPA).",
    "bp_target_cpa": "CPA target in EUR from the media plan (average of the plan lines; 0 when the client is managed on ROAS).",
    # Product Feed & Shopping
    "pf_impressions": "Product-ad impressions (Shopping, Performance Max, Microsoft Shopping, Amazon) at product level.",
    "pf_clicks": "Product-ad clicks at product level.",
    "pf_cost": "Product-ad spend in EUR at product level. Sums to the cost of the shopping campaigns.",
    "pf_conversions": "Platform-reported conversions of product ads at product level.",
    "pf_value": "Platform-reported conversion value of product ads at product level, in EUR.",
    "pf_ctr": "Product CTR = Product Clicks / Product Impressions. Compare SmartFeeds-optimised vs non-optimised products.",
    "pf_roas": "Product ROAS = Product Conversion Value / Product Cost. Higher is better.",
    "pf_products": "Number of products that had product-ad impressions in the period.",
    # CRM & Offline Sales
    "crm_leads": "Number of CRM leads created (paid and non-paid), by lead creation date.",
    "crm_qualified": "Leads qualified by the client's sales team (AutoNova: 'lead qualifié').",
    "crm_opportunities": "Leads that reached an opportunity: test drive done (AutoNova) or quote sent (Seconde Vie Pro).",
    "crm_won": "Leads won: car sold (AutoNova) or B2B device-fleet deal signed (Seconde Vie Pro).",
    "crm_deal_value": "Value of won deals in EUR (vehicle price or fleet order value).",
    "crm_gross_profit": "Gross profit of won deals in EUR.",
    "crm_qual_rate": "Qualification rate = Qualified Leads / Leads - lead quality. Higher is better; compare by platform.",
    "crm_win_rate": "Win rate = Won Deals / Qualified Leads. Higher is better.",
    "crm_contact_hours": "Average hours from lead creation to first contact by sales (new, uncontacted leads excluded). "
                         "Lower is better.",
    "crm_days_to_close": "Average days from lead creation to the won deal (won leads only).",
    "crm_lead_cost": "Media cost of lead-generation campaigns (campaign objective = Leads), in EUR - the cost base of the CRM "
                     "efficiency metrics.",
    "crm_cpl": "Cost per lead = Lead-gen Media Cost / paid leads (leads from campaigns with objective Leads), in EUR. Lower is "
               "better; AutoNova's target is EUR 45.",
    "crm_cpql": "Cost per qualified lead = Lead-gen Media Cost / qualified paid leads, in EUR. Better than CPL for judging "
                "platforms, because lead quality differs a lot.",
    "crm_cost_per_won": "Cost per won deal = Lead-gen Media Cost / won paid leads, in EUR - cost per car sold (AutoNova) or per "
                        "B2B deal (Seconde Vie Pro). The true acquisition cost.",
    "crm_oci_share": "Won deals sent back to the ad platforms as offline conversions (Arcane SmartConversion), so bidding "
                     "optimises for real sales.",
    # Measurement & Incrementality
    "mi_tests": "Number of incrementality tests (geo-lift, conversion-lift, holdouts) started in the period.",
    "mi_spend": "Media spend in the test cells during the tests, in EUR.",
    "mi_inc_revenue": "Incremental revenue in EUR: revenue (gross profit for AutoNova) that would not have happened without "
                      "the media.",
    "mi_iroas": "Incremental ROAS = Incremental Revenue / Test Spend. Below 1.0 the channel does not pay back. Prefer it over "
                "platform ROAS for budget decisions.",
    "mi_inc_share": "Share of platform-reported conversions that were truly incremental = Incremental Conversions / Platform "
                    "Conversions of the tests.",
    # Arcane Operations
    "op_requests": "Number of data requests submitted to Arcane's data team (Google Form, email, Slack).",
    "op_delivered": "Number of data requests delivered.",
    "op_days": "Average days from request to delivery (delivered requests only) - the lead time of today's manual process.",
    "op_effort": "Consultant hours spent on data requests.",
    "op_open": "Data requests in progress or in the backlog.",
    "op_entitled": "Number of data products enabled for the client (from the client's entitlements).",
}

# ---------------------------------------------------------------------------
# Visualizations: what it shows and how to read it
# ---------------------------------------------------------------------------
VIS_DESC = {
    # 1. Paid Media Performance
    "pm_k_cost": "Total media spend in EUR across all platforms, with the change versus the previous period.",
    "pm_k_conv": "Platform-reported conversions (orders, bookings or leads depending on the client), versus the previous period.",
    "pm_k_value": "Platform-reported conversion value in EUR, versus the previous period.",
    "pm_k_roas": "Platform ROAS (conversion value / cost) versus the previous period; compare with the client's Target ROAS.",
    "pm_k_cpa": "Cost per conversion in EUR versus the previous period; a rise is bad. Compare with the client's Target CPA.",
    "pm_k_ctr": "Click-through rate across all campaigns, versus the previous period.",
    "pm_trend": "Monthly media spend (columns) and ROAS (line). Shows seasonality (Black Friday, soldes, Easter) and whether "
                "efficiency holds when spend scales.",
    "pm_by_platform": "Share of media spend per platform (Google, Meta, Microsoft, TikTok, LinkedIn, Amazon, DV360).",
    "pm_by_type": "Cost, clicks, conversions, CPA and ROAS per campaign type, with totals - which campaign types drive results "
                  "and which are expensive.",
    "pm_by_market": "Media cost and conversions per market (country) - where the budget goes and what it returns.",
    "pm_by_funnel": "Monthly spend split by funnel stage (awareness, consideration, conversion) - the media-mix strategy over time.",
    "pm_device": "CPA and conversion rate per device (mobile, desktop, tablet, connected TV). Desktop usually converts better.",
    "pm_is_trend": "Weekly search impression share and the share lost to budget and to rank. A rise in Lost IS (Budget) means "
                   "campaigns are capped by budget; a rise in Lost IS (Rank) means competitors outbid you.",
    "pm_is_market": "Search impression share, lost share and conversions per market - spot the market where budget caps limit "
                    "delivery (e.g. Germany).",
    "pm_top_campaigns": "Campaigns ranked by cost with conversions, CPA, ROAS and CTR - the campaigns that matter most.",
    # 2. Social & Creatives
    "sc_k_spend": "Spend on social creatives in EUR versus the previous period.",
    "sc_k_ctr": "Click-through rate of social creatives versus the previous period; falling CTR hints at creative fatigue.",
    "sc_k_cpa": "Social cost per conversion in EUR versus the previous period.",
    "sc_k_thumb": "Thumb-stop rate (3-second views / impressions) - hook strength of video creatives - versus the previous period.",
    "sc_k_hold": "Hold rate (ThruPlays / 3-second views) - how well videos keep attention - versus the previous period.",
    "sc_k_live": "Number of creatives that delivered in the period, versus the previous period.",
    "sc_by_format": "CTR and CPA per creative format (UGC video, Reels, static image, carousel, Spark Ads ...) - which formats "
                    "to brief more of.",
    "sc_by_source": "CPA (columns) and CTR (line) per production source: in-house studio, UGC creators, agency design and "
                    "AI-generated creatives from Arcane AI Lab.",
    "sc_trend": "Monthly social spend per platform (Meta, TikTok, LinkedIn) - shows TikTok and LinkedIn ramping up.",
    "sc_by_theme": "Conversions per creative theme (product showcase, promo, testimonial, seasonal ...) - which messages convert.",
    "sc_top": "Creatives ranked by spend with impressions, CTR, thumb-stop rate, conversions and CPA - spot winners and fatigued "
              "creatives to refresh.",
    # 3. Web, Sales & GEO
    "wa_k_rev": "Backend revenue in EUR (the client's source of truth, all channels) versus the previous period.",
    "wa_k_mer": "Blended ROAS / MER (total backend revenue / total media cost) versus the previous period.",
    "wa_k_paidshare": "Share of backend revenue coming from paid media, versus the previous period.",
    "wa_k_cvr": "Site conversion rate (backend transactions / sessions) versus the previous period.",
    "wa_k_newc": "First-time customers versus the previous period.",
    "wa_k_ai": "Sessions referred by AI assistants (ChatGPT, Perplexity, Gemini) versus the previous period - the GEO KPI.",
    "wa_rev_channel": "Monthly backend revenue stacked by channel group (paid, organic, direct, email, affiliates, AI assistants).",
    "wa_channels": "Sessions, transactions, conversion rate, revenue, AOV and new customers per web channel, with totals.",
    "wa_ai_trend": "Monthly sessions from AI assistants (columns) and their share of all sessions (line) - growth of AI search "
                   "as a traffic source.",
    "wa_attrib": "Monthly platform ROAS vs backend ROAS vs blended ROAS (MER). The gap between the platform line and the "
                 "backend line is platform over-attribution.",
    "wa_market": "Backend revenue, media cost, MER, backend ROAS and platform over-attribution per market.",
    # 4. Budget & Pacing
    "bp_k_planned": "Planned media budget for the current calendar month (media plan).",
    "bp_k_actual": "Media spend so far in the current month.",
    "bp_k_pacing": "Spend / plan for the current month. Compare with the share of the month elapsed (e.g. 50% at mid-month).",
    "bp_k_remaining": "Budget left to spend in the current month.",
    "bp_trend": "Monthly planned budget vs actual cost (columns) and pacing % (line), including next month's plan.",
    "bp_table": "Current-month plan, spend, pacing and variance per market and platform, with totals - where spend is ahead of "
                "or behind plan.",
    "bp_p_planned": "Planned media budget for the selected period (dashboard or report date filter).",
    "bp_p_actual": "Media spend for the selected period, to compare with the planned budget.",
    "bp_p_pacing": "Spend / planned budget for the selected period; 100% = delivered exactly to plan.",
    "bp_p_variance": "Spend minus planned budget for the selected period, in EUR; negative = under-spent versus plan.",
    "bp_p_table": "Planned budget, spend, pacing and variance per market and platform for the selected period, with totals - "
                  "which plan lines under- or over-delivered.",
    "bp_platform": "Current-month pacing per platform - which platforms under- or over-deliver versus the plan.",
    # 5. Product Feed & Shopping
    "pf_k_cost": "Product-ad spend (Shopping, PMax, Microsoft Shopping, Amazon) versus the previous period.",
    "pf_k_value": "Conversion value of product ads versus the previous period.",
    "pf_k_roas": "Product ROAS (product conversion value / cost) versus the previous period.",
    "pf_k_ctr": "Product-ad CTR versus the previous period.",
    "pf_k_products": "Number of products with product-ad impressions, versus the previous period.",
    "pf_feed": "Weekly product CTR of SmartFeeds-optimised vs non-optimised products - the uplift of feed optimisation after "
               "go-live.",
    "pf_category": "Product ROAS and cost per product category - where shopping budget pays back.",
    "pf_platform": "Product-ad spend split by platform: Google (Shopping / PMax), Microsoft Shopping and Amazon.",
    "pf_top": "Products ranked by conversion value with cost, ROAS, CTR, conversions and feed optimisation flag.",
    # 6. CRM & Offline Sales
    "crm_k_leads": "CRM leads created versus the previous period.",
    "crm_k_qual": "Qualification rate (qualified leads / leads) versus the previous period - lead quality.",
    "crm_k_won": "Won deals (cars sold / B2B deals signed) versus the previous period.",
    "crm_k_value": "Value of won deals in EUR versus the previous period.",
    "crm_k_cpl": "Cost per paid lead (lead-gen media cost / paid leads) versus the previous period.",
    "crm_k_cpw": "Cost per won deal (lead-gen media cost / won paid leads) - cost per car sold or per B2B deal - versus the "
                 "previous period.",
    "crm_funnel": "Lead funnel: leads -> qualified -> opportunity (test drive / quote) -> won. Shows where leads drop out.",
    "crm_trend": "Monthly lead volume (columns) and qualification rate (line) - did more leads come at the cost of quality?",
    "crm_cost_trend": "Monthly cost per qualified lead and cost per won deal. For AutoNova both fall after the offline "
                      "conversion import (SmartConversion) went live in March 2025.",
    "crm_platform": "Leads, qualification rate, win rate, won deals and deal value per platform - which platforms bring leads "
                    "that actually buy.",
    "crm_location": "Leads, qualification rate, won deals, deal value and speed to first contact per dealership / sales office.",
    "crm_status": "Leads by current CRM status: open, won, lost (with reason) and disqualified.",
    # 7. Measurement & Incrementality
    "mi_k_tests": "Number of incrementality tests started in the period.",
    "mi_k_iroas": "Incremental ROAS across the tests (incremental revenue / test spend). Below 1.0 the media does not pay back.",
    "mi_k_rev": "Incremental revenue measured by the tests - revenue caused by the media.",
    "mi_k_share": "Share of platform-reported conversions that were truly incremental in the tests.",
    "mi_scope": "Incremental ROAS per tested campaign type - e.g. retargeting and brand search are far less incremental than "
                "prospecting or PMax.",
    "mi_table": "All incrementality tests with status, significance, spend, iROAS, incremental revenue and Arcane's "
                "recommendation.",
    # 8. Arcane Operations
    "op_k_req": "Data requests submitted to Arcane's data team versus the previous period.",
    "op_k_days": "Average days to deliver a data request versus the previous period - the lead time of today's manual loop.",
    "op_k_open": "Data requests currently in progress or in the backlog.",
    "op_k_effort": "Consultant hours spent on data requests versus the previous period.",
    "op_trend": "Monthly data requests by type (new KPI, new filter, deep dive, slides, discrepancy ...) - what clients and media "
                "consultants ask for.",
    "op_days_type": "Average days to deliver per request type - new data sources take the longest.",
    "op_list": "Log of data requests with client, status, days to deliver and effort.",
    "op_entitlements": "Data products enabled per client and their package (Core, Standard, Premium add-on) - drives which "
                       "dashboards each client's users can see.",
}
