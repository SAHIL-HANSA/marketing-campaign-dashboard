-- KPI Calculations for Marketing Campaign Dashboard
-- Author: Sahil Hansa
-- Email: sahilhansa007@gmail.com
-- Description: SQL queries for calculating critical KPIs
-- Location: Jammu, J&K, India

-- Calculate ROI, Cost Per Lead, CPA, Conversion Rate, CTR per campaign

SELECT
    campaign_id,
    campaign_name,
    channel,
    start_date,
    end_date,
    total_spend,
    revenue_generated,
    leads_generated,
    conversions,
    impressions,
    clicks,

    ROUND(
        CASE 
            WHEN total_spend > 0 THEN ((revenue_generated - total_spend) / total_spend) * 100
            ELSE 0
        END, 2
    ) AS roi_percentage,

    ROUND(
        CASE 
            WHEN leads_generated > 0 THEN (total_spend / leads_generated)
            ELSE NULL
        END, 2
    ) AS cost_per_lead,

    ROUND(
        CASE
            WHEN conversions > 0 THEN (total_spend / conversions)
            ELSE NULL
        END, 2
    ) AS cost_per_acquisition,

    ROUND(
        CASE 
            WHEN leads_generated > 0 THEN (conversions / leads_generated) * 100
            ELSE NULL
        END, 2
    ) AS conversion_rate,

    ROUND(
        CASE
            WHEN impressions > 0 THEN (clicks / impressions) * 100
            ELSE NULL
        END, 2
    ) AS click_through_rate

FROM marketing_campaigns
WHERE start_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
ORDER BY start_date DESC;
