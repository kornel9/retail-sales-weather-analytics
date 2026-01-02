WITH drinks AS (
  SELECT
    date, store, country,
    daily_revenue,
    precipitation_sum
  FROM curated_enriched_sales
  WHERE product IN ('Cold Drink')
),
bucketed AS (
  SELECT
    country,
    store,
    CASE
      WHEN precipitation_sum >= 5 THEN 'rainy_5mm_plus'
      WHEN precipitation_sum > 0 THEN 'light_rain_0_5'
      ELSE 'no_rain'
    END AS rain_bucket,
    SUM(daily_revenue) AS revenue
  FROM drinks
  GROUP BY 1,2,3
)
SELECT *
FROM bucketed
ORDER BY country, store, rain_bucket;
