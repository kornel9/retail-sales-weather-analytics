WITH totals AS (
  SELECT SUM(daily_revenue) AS total_revenue
  FROM curated_enriched_sales
),
sensitive AS (
  SELECT SUM(daily_revenue) AS sensitive_revenue
  FROM curated_enriched_sales
  WHERE product IN ('Ice Cream', 'Cold Drink')
)
SELECT
  t.total_revenue,
  s.sensitive_revenue,
  (s.sensitive_revenue / t.total_revenue) * 100 AS sensitive_revenue_pct
FROM totals t, sensitive s;
