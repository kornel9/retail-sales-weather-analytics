/*
  File: Create_db_in_Athena.sql
  Description: 
      DDL (Data Definition Language) script to initialize the Data Lake schema.
      
  Actions:
      1. Creates the database 'athena_db' if it doesn't exist.
      2. Creates external table 'sales_raw' pointing to S3 raw/sales/.
      3. Creates external table 'weather_raw' pointing to S3 raw/weather/.
      
  Notes:
      - Ensure the S3 paths match the bucket structure defined in the infrastructure.
      - Uses Hive partitioning (if applicable) for performance optimization.
*/

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
