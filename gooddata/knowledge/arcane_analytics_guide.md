# Arcane Analytics Guide

How to read the Arcane client analytics: paid media across platforms, social creatives, web and backend sales,
budget pacing, product feeds, CRM / offline sales and incrementality.

## Business context

- Arcane is a Paris media and data agency. It buys search, shopping, social, video and retail media for its
  clients (advertisers) and runs feed engineering (SmartFeeds), offline conversion import (SmartConversion),
  incrementality testing and GEO (visibility in AI assistants).
- Data comes from the ad platforms through Adverity into BigQuery, plus the clients' backend, GA4 and CRM data.
- Each client has its own workspace and sees only its own data. Arcane consultants work in the parent workspace,
  which shows all clients.
- Clients: **Seconde Vie** (refurbished electronics marketplace, 6 markets, plus the B2B line Seconde Vie Pro),
  **AutoNova Automobiles** (car dealer network with 12 dealerships, lead generation and cars sold offline) and
  **Routéo Location** (car and van rental, online bookings in 5 countries).
- Every client defines its main KPI differently (see Client > Primary KPI Definition): orders / GMV, qualified
  leads and cars sold, or confirmed bookings.

## Data products (dashboards)

| Dashboard | What it answers |
|---|---|
| 1. Paid Media Performance | Spend, conversions, ROAS / CPA by platform, market, campaign type and device; search impression share |
| 2. Social & Creatives | Which creatives, formats, themes and production sources (UGC, AI-generated) work; fatigue |
| 3. Web, Sales & GEO | Backend revenue by channel, blended ROAS (MER), platform over-attribution, AI-assistant traffic |
| 4. Budget & Pacing | Media plan vs actual spend by month, market and platform |
| 5. Product Feed & Shopping | Product-level Shopping / PMax / Amazon results, impact of SmartFeeds |
| 6. CRM & Offline Sales | Lead funnel, lead quality by platform, cost per qualified lead and per won deal |
| 7. Measurement & Incrementality | Geo-lift and conversion-lift tests, iROAS per channel |
| 8. Arcane Operations | Internal: data request volume and delivery time, client data-product entitlements |

## Key metrics

| Metric | Definition | Good direction |
|---|---|---|
| Cost | Media spend in EUR (local currency also available) | – |
| ROAS | Platform conversion value / cost | Higher |
| CPA | Cost / platform conversions | Lower |
| Backend ROAS | De-duplicated backend paid revenue / cost | Higher |
| Blended ROAS (MER) | Total backend revenue / total media cost | Higher |
| Platform Over-attribution | Platform conversion value / backend paid revenue (1.0x = agree) | Closer to 1 |
| Search Impression Share | Search impressions / eligible impressions | Higher |
| Lost IS (Budget) / (Rank) | Eligible impressions lost to budget caps / to ad rank | Lower |
| Budget Pacing | Cost / planned budget | ~100% |
| Thumb-stop Rate / Hold Rate | 3-s views / impressions; ThruPlays / 3-s views | Higher |
| Qualification Rate / Win Rate | Qualified / leads; won / qualified | Higher |
| Cost per Lead / per Won Deal | Cost of lead-gen campaigns (objective = Leads) / leads or won deals | Lower |
| iROAS | Incremental revenue / test spend | Higher (> 1 pays back) |

## How to analyse

- **Performance drop**: break down by market, then platform and campaign type. Check impression share. If Lost IS
  (Budget) jumped, a budget cap is limiting delivery; check pacing vs the media plan. If CPC jumped, competition
  increased. If conversion rate fell with stable traffic, look at the site / offer.
- **Tracking issue vs real drop**: platform conversions collapsing while clicks and backend transactions stay flat
  is a tracking problem (pixel, Conversions API, tag), not lower demand.
- **Platform vs backend**: platforms over-attribute, especially social and video. Use backend ROAS / MER for
  business decisions and platform ROAS for in-platform optimisation.
- **Budget decisions**: prefer iROAS from incrementality tests over platform ROAS.
- **Seasonality**: French retail calendar - soldes (January, late June), Mother's Day, back to school (late
  August), Black Friday / Cyber Monday, Christmas. Rentals book in spring for summer and before Easter. Car sales
  dip in August and peak around the Paris Motor Show (Mondial de l'Auto, October in even years).
- Data ends yesterday; the current month is partial.
