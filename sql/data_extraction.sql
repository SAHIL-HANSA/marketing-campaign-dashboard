-- SQL Data Extraction Queries for Marketing Campaign Dashboard
-- Author: Sahil Hansa
-- Email: sahilhansa007@gmail.com  
-- Description: SQL queries for extracting marketing campaign data for Power BI dashboard
-- Location: Jammu, J&K, India

-- =============================================
-- Campaign Performance Data Extraction
-- =============================================

-- Main campaign performance query
SELECT 
    c.campaign_id,
    c.campaign_name,
    c.campaign_type,
    c.channel,
    c.start_date,
    c.end_date,
    c.budget_allocated,
    c.total_spend,
    c.impressions,
    c.clicks,
    c.leads_generated,
    c.conversions,
    c.revenue_generated,
    c.status,
    
    -- Calculated KPIs
    ROUND(
        CASE 
            WHEN c.total_spend > 0 
            THEN ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 
            ELSE 0 
        END, 2
    ) as roi_percentage,
    
    ROUND(
        CASE 
            WHEN c.leads_generated > 0 
            THEN c.total_spend / c.leads_generated 
            ELSE 0 
        END, 2
    ) as cost_per_lead,
    
    ROUND(
        CASE 
            WHEN c.conversions > 0 
            THEN c.total_spend / c.conversions 
            ELSE 0 
        END, 2
    ) as cost_per_acquisition,
    
    ROUND(
        CASE 
            WHEN c.leads_generated > 0 
            THEN (c.conversions / c.leads_generated) * 100 
            ELSE 0 
        END, 2
    ) as conversion_rate,
    
    ROUND(
        CASE 
            WHEN c.impressions > 0 
            THEN (c.clicks / c.impressions) * 100 
            ELSE 0 
        END, 4
    ) as click_through_rate,
    
    -- Budget metrics
    c.budget_allocated - c.total_spend as remaining_budget,
    ROUND((c.total_spend / c.budget_allocated) * 100, 2) as budget_utilization,
    
    -- Time calculations
    DATEDIFF(c.end_date, c.start_date) + 1 as campaign_duration_days,
    DATEDIFF(CURDATE(), c.start_date) as days_since_start,
    
    -- Performance indicators
    CASE 
        WHEN ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 >= 300 THEN 'Excellent'
        WHEN ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 >= 200 THEN 'Good'
        WHEN ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 >= 100 THEN 'Average'
        ELSE 'Poor'
    END as performance_tier

FROM marketing_campaigns c
WHERE c.start_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
ORDER BY c.start_date DESC;

-- =============================================
-- Budget Allocation and Spending Analysis
-- =============================================

-- Budget breakdown by channel and category
SELECT 
    b.campaign_id,
    c.campaign_name,
    b.channel,
    b.budget_category,
    b.allocated_amount,
    b.spent_amount,
    b.remaining_amount,
    b.quarter,
    b.month,
    b.year,
    b.cost_center,
    
    -- Budget utilization metrics
    ROUND((b.spent_amount / b.allocated_amount) * 100, 2) as utilization_rate,
    
    -- Budget variance
    b.allocated_amount - b.spent_amount as budget_variance,
    ROUND(((b.allocated_amount - b.spent_amount) / b.allocated_amount) * 100, 2) as variance_percentage,
    
    -- Budget status
    CASE 
        WHEN b.spent_amount > b.allocated_amount THEN 'Over Budget'
        WHEN (b.spent_amount / b.allocated_amount) > 0.95 THEN 'Near Limit'
        WHEN (b.spent_amount / b.allocated_amount) > 0.80 THEN 'On Track'
        ELSE 'Under Utilized'
    END as budget_status

FROM budget_allocation b
LEFT JOIN marketing_campaigns c ON b.campaign_id = c.campaign_id
WHERE b.year >= YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
ORDER BY b.year DESC, b.quarter DESC, b.month DESC;

-- =============================================
-- Channel Performance Comparison
-- =============================================

-- Channel performance aggregation
SELECT 
    c.channel,
    COUNT(c.campaign_id) as total_campaigns,
    SUM(c.budget_allocated) as total_budget,
    SUM(c.total_spend) as total_spent,
    SUM(c.impressions) as total_impressions,
    SUM(c.clicks) as total_clicks,
    SUM(c.leads_generated) as total_leads,
    SUM(c.conversions) as total_conversions,
    SUM(c.revenue_generated) as total_revenue,
    
    -- Average performance metrics
    ROUND(AVG(
        CASE 
            WHEN c.total_spend > 0 
            THEN ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 
            ELSE 0 
        END), 2
    ) as avg_roi_percentage,
    
    ROUND(AVG(
        CASE 
            WHEN c.leads_generated > 0 
            THEN c.total_spend / c.leads_generated 
            ELSE 0 
        END), 2
    ) as avg_cost_per_lead,
    
    ROUND(AVG(
        CASE 
            WHEN c.conversions > 0 
            THEN c.total_spend / c.conversions 
            ELSE 0 
        END), 2
    ) as avg_cost_per_acquisition,
    
    ROUND(AVG(
        CASE 
            WHEN c.leads_generated > 0 
            THEN (c.conversions / c.leads_generated) * 100 
            ELSE 0 
        END), 2
    ) as avg_conversion_rate,
    
    ROUND(AVG(
        CASE 
            WHEN c.impressions > 0 
            THEN (c.clicks / c.impressions) * 100 
            ELSE 0 
        END), 4
    ) as avg_ctr,
    
    -- Overall channel ROI
    ROUND(
        CASE 
            WHEN SUM(c.total_spend) > 0 
            THEN ((SUM(c.revenue_generated) - SUM(c.total_spend)) / SUM(c.total_spend)) * 100 
            ELSE 0 
        END, 2
    ) as channel_total_roi,
    
    -- Market share by revenue
    ROUND(
        (SUM(c.revenue_generated) / 
         (SELECT SUM(revenue_generated) FROM marketing_campaigns WHERE start_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
        ) * 100, 2
    ) as revenue_market_share

FROM marketing_campaigns c
WHERE c.start_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY c.channel
ORDER BY channel_total_roi DESC;

-- =============================================
-- Time-based Performance Analysis
-- =============================================

-- Monthly performance trends
SELECT 
    DATE_FORMAT(c.start_date, '%Y-%m') as month_year,
    YEAR(c.start_date) as year,
    MONTH(c.start_date) as month,
    MONTHNAME(c.start_date) as month_name,
    QUARTER(c.start_date) as quarter,
    
    COUNT(c.campaign_id) as campaigns_launched,
    SUM(c.budget_allocated) as total_budget,
    SUM(c.total_spend) as total_spent,
    SUM(c.revenue_generated) as total_revenue,
    SUM(c.leads_generated) as total_leads,
    SUM(c.conversions) as total_conversions,
    
    -- Monthly ROI
    ROUND(
        CASE 
            WHEN SUM(c.total_spend) > 0 
            THEN ((SUM(c.revenue_generated) - SUM(c.total_spend)) / SUM(c.total_spend)) * 100 
            ELSE 0 
        END, 2
    ) as monthly_roi,
    
    -- Monthly averages
    ROUND(AVG(c.total_spend), 2) as avg_campaign_spend,
    ROUND(AVG(c.revenue_generated), 2) as avg_campaign_revenue,
    
    -- Growth calculations (compared to previous month)
    LAG(SUM(c.revenue_generated)) OVER (ORDER BY DATE_FORMAT(c.start_date, '%Y-%m')) as prev_month_revenue,
    
    ROUND(
        ((SUM(c.revenue_generated) - LAG(SUM(c.revenue_generated)) OVER (ORDER BY DATE_FORMAT(c.start_date, '%Y-%m'))) / 
         LAG(SUM(c.revenue_generated)) OVER (ORDER BY DATE_FORMAT(c.start_date, '%Y-%m'))) * 100, 2
    ) as revenue_growth_mom

FROM marketing_campaigns c
WHERE c.start_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
GROUP BY 
    DATE_FORMAT(c.start_date, '%Y-%m'),
    YEAR(c.start_date),
    MONTH(c.start_date),
    MONTHNAME(c.start_date),
    QUARTER(c.start_date)
ORDER BY month_year DESC;

-- =============================================
-- Campaign Type Performance Analysis
-- =============================================

-- Performance by campaign type
SELECT 
    c.campaign_type,
    COUNT(c.campaign_id) as total_campaigns,
    COUNT(CASE WHEN c.status = 'Active' THEN 1 END) as active_campaigns,
    COUNT(CASE WHEN c.status = 'Completed' THEN 1 END) as completed_campaigns,
    
    SUM(c.total_spend) as total_investment,
    SUM(c.revenue_generated) as total_revenue,
    SUM(c.leads_generated) as total_leads,
    SUM(c.conversions) as total_conversions,
    
    -- Type-level metrics
    ROUND(AVG(
        CASE 
            WHEN c.total_spend > 0 
            THEN ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 
            ELSE 0 
        END), 2
    ) as avg_roi,
    
    ROUND(
        CASE 
            WHEN SUM(c.total_spend) > 0 
            THEN ((SUM(c.revenue_generated) - SUM(c.total_spend)) / SUM(c.total_spend)) * 100 
            ELSE 0 
        END, 2
    ) as total_roi,
    
    ROUND(AVG(
        CASE 
            WHEN c.leads_generated > 0 
            THEN (c.conversions / c.leads_generated) * 100 
            ELSE 0 
        END), 2
    ) as avg_conversion_rate,
    
    -- Success rate (campaigns with ROI > 200%)
    ROUND(
        (COUNT(CASE 
            WHEN ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 > 200 
            THEN 1 
        END) / COUNT(c.campaign_id)) * 100, 2
    ) as success_rate_percentage

FROM marketing_campaigns c
WHERE c.start_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY c.campaign_type
ORDER BY total_roi DESC;

-- =============================================
-- Top Performing Campaigns
-- =============================================

-- Best performing campaigns by ROI
SELECT 
    c.campaign_id,
    c.campaign_name,
    c.campaign_type,
    c.channel,
    c.start_date,
    c.end_date,
    c.total_spend,
    c.revenue_generated,
    c.leads_generated,
    c.conversions,
    
    ROUND(((c.revenue_generated - c.total_spend) / c.total_spend) * 100, 2) as roi_percentage,
    ROUND(c.total_spend / c.leads_generated, 2) as cost_per_lead,
    ROUND((c.conversions / c.leads_generated) * 100, 2) as conversion_rate,
    
    -- Ranking
    ROW_NUMBER() OVER (ORDER BY ((c.revenue_generated - c.total_spend) / c.total_spend) DESC) as roi_rank,
    ROW_NUMBER() OVER (ORDER BY c.revenue_generated DESC) as revenue_rank,
    ROW_NUMBER() OVER (ORDER BY (c.conversions / c.leads_generated) DESC) as conversion_rank

FROM marketing_campaigns c
WHERE c.status = 'Completed'
  AND c.total_spend > 0
  AND c.leads_generated > 0
ORDER BY roi_percentage DESC
LIMIT 20;

-- =============================================
-- Underperforming Campaigns Analysis
-- =============================================

-- Campaigns needing attention (low ROI or high spend with low returns)
SELECT 
    c.campaign_id,
    c.campaign_name,
    c.campaign_type,
    c.channel,
    c.status,
    c.total_spend,
    c.revenue_generated,
    c.leads_generated,
    c.conversions,
    
    ROUND(((c.revenue_generated - c.total_spend) / c.total_spend) * 100, 2) as roi_percentage,
    ROUND(c.total_spend / NULLIF(c.leads_generated, 0), 2) as cost_per_lead,
    ROUND((c.conversions / NULLIF(c.leads_generated, 0)) * 100, 2) as conversion_rate,
    
    -- Problem identification
    CASE 
        WHEN c.revenue_generated < c.total_spend THEN 'Negative ROI'
        WHEN c.leads_generated = 0 THEN 'No Leads Generated'
        WHEN c.conversions = 0 THEN 'No Conversions'
        WHEN (c.total_spend / c.leads_generated) > 100 THEN 'High Cost Per Lead'
        WHEN ((c.conversions / c.leads_generated) * 100) < 5 THEN 'Low Conversion Rate'
        ELSE 'Review Required'
    END as issue_category,
    
    -- Recommendations
    CASE 
        WHEN c.revenue_generated < c.total_spend THEN 'Pause and analyze targeting'
        WHEN c.leads_generated = 0 THEN 'Review ad creative and audience'
        WHEN c.conversions = 0 THEN 'Optimize landing page and offer'
        WHEN (c.total_spend / c.leads_generated) > 100 THEN 'Reduce bid or improve targeting'
        WHEN ((c.conversions / c.leads_generated) * 100) < 5 THEN 'Improve lead quality or nurturing'
        ELSE 'Monitor closely'
    END as recommended_action

FROM marketing_campaigns c
WHERE (
    ((c.revenue_generated - c.total_spend) / c.total_spend) * 100 < 100  -- ROI less than 100%
    OR c.leads_generated = 0
    OR c.conversions = 0
    OR (c.total_spend / NULLIF(c.leads_generated, 0)) > 100  -- Cost per lead > $100
    OR ((c.conversions / NULLIF(c.leads_generated, 0)) * 100) < 5  -- Conversion rate < 5%
)
AND c.start_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
ORDER BY roi_percentage ASC;