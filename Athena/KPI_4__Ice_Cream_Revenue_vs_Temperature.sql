SELECT
  CASE
    WHEN temperature_mean < 10 THEN 'Cold'
    WHEN temperature_mean BETWEEN 10 AND 20 THEN 'Mild'
    ELSE 'Hot'
  END AS temperature_bucket,
  ROUND(SUM(daily_revenue), 2) AS ice_cream_revenue
FROM curated_enriched_sales
WHERE product = 'Ice Cream'
GROUP BY 1
ORDER BY 1;
