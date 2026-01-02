# Implementation

## 1) Synthetic Sales Dataset Generation

### Why synthetic data?
Real retail sales data is often proprietary. To demonstrate a realistic pipeline without exposing sensitive information, I generated a synthetic dataset that simulates daily retail transactions across multiple stores and products.

### Time range and granularity
- Date range: **2021-01-01 to 2025-12-31**
- Granularity: **daily sales per store per product**
- File: `data/sales_synthetic_2021_2025.csv` (~4.6 MB)

### Schema
Columns:
- `date` (YYYY-MM-DD)
- `store`, `country`
- `lat`, `lon` (store coordinates)
- `product`
- `quantity_sold`
- `price`

### Realism assumptions embedded in the generator
The generator encodes business-realistic behavior:
- **Seasonality:** summer boosts cold products (ice cream, cold drinks), winter boosts hot products (coffee, tea).
- **Store size effects:** larger cities have higher baseline demand.
- **Weekend uplift:** higher traffic on weekends.
- **Promotions:** random promo events with demand uplift (more likely in summer and Nov–Dec).
- **Price dynamics:** small inflation trend over time plus minor noise.

These assumptions make downstream KPIs and insights interpretable, rather than purely random.

### Synthetic Data Generator Code

The synthetic sales dataset was generated using a custom Python script that encodes business-relevant assumptions such as seasonality, store size effects, promotions, and price inflation.

The generator script is included in the repository for transparency and reproducibility:
- `data_generation/generate_sales.py`

The script was executed once to produce the input dataset used in the pipeline.


## 2) Weather Data Integration Strategy (Join Logic)

Sales data and weather data originate from independent systems and have different schemas. Integration is achieved by aligning records on shared temporal and spatial dimensions:

**Join keys**
- `date` (daily time dimension)
- `lat`, `lon` (store location)

Conceptually:
- `sales.date = weather.date`
- `sales.lat = weather.lat`
- `sales.lon = weather.lon`

This reflects common data warehousing practice where contextual data (weather) is joined to granular fact data (sales).

## 3) Raw Data Storage (Amazon S3)

The data lake is implemented using Amazon S3 with a clear separation between raw and curated data layers.

### Bucket structure
- `raw/sales/` – internal sales CSV data
- `raw/weather/` – external weather data ingested via API
- `curated/` – transformed, analytics-ready datasets

The synthetic sales dataset covering 2021–2025 was uploaded to the raw sales layer and serves as the internal data source for the pipeline.

## 4) Weather Ingestion (AWS Lambda + Open-Meteo)

Weather data is ingested from the Open-Meteo API using an AWS Lambda function (`weather_ingest_openmeteo`).  
The function retrieves daily weather metrics (mean temperature and precipitation sum) for each store location and writes the results into the S3 raw layer.

### Output format and storage
- Output: CSV
- S3 path pattern:
  - `raw/weather/year=YYYY/month=MM/weather_<start>_to_<end>.csv`

### Backfill strategy
To avoid large API requests and to keep the process reliable, historical ingestion is performed in monthly chunks. This mirrors real-world backfill practices and reduces the risk of timeouts.

### Historical backfill (2021–2025)
Historical weather data was ingested in monthly chunks (2021-01 to 2025-12) to avoid large API requests and reduce timeout/rate-limit risk. Each run writes a month-partitioned CSV file to:

`raw/weather/year=YYYY/month=MM/weather_<start>_to_<end>.csv`

This approach is consistent with real-world backfill patterns and supports efficient partition pruning in downstream analytics.

Note: The Open-Meteo Archive API endpoint is used because the project requires multi-year historical coverage.

## 5) Data Cataloging (AWS Glue Crawlers)

AWS Glue Crawlers were used to automatically infer schemas and register the raw datasets as tables in the Glue Data Catalog.

- `crawler_raw_sales` crawls `s3://<bucket>/raw/sales/`
- `crawler_raw_weather` crawls `s3://<bucket>/raw/weather/`

Both crawlers write tables into the Glue database `retail_weather_db`, enabling downstream querying and ETL development.

