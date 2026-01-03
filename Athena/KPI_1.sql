SELECT
  CASE
    WHEN temperature_mean >= 25 THEN 'hot_day_25plus'
    WHEN temperature_mean >= 15 THEN 'mild_15_24'
    ELSE 'cold_below_15'
  END AS temp_bucket,
  COUNT(*) AS days,
  SUM(daily_revenue) AS total_revenue,
  AVG(daily_revenue) AS avg_daily_revenue
FROM curated_enriched_sales
WHERE product = 'Ice Cream'
GROUP BY 1
ORDER BY avg_daily_revenue DESC;
