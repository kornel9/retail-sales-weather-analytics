CREATE DATABASE IF NOT EXISTS retail_weather_athena;

CREATE EXTERNAL TABLE IF NOT EXISTS curated_enriched_sales (
  date date,
  store string,
  country string,
  product string,
  quantity_sold int,
  price double,
  daily_revenue double,
  temperature_mean double,
  precipitation_sum double
)
STORED AS PARQUET
LOCATION 's3://retail-sales-weather-w12k77/curated/enriched_sales/';
