# Retail Sales & Weather Analytics for Demand Optimization

## Project Overview
This project implements a cloud-based data engineering pipeline to analyze the relationship between retail sales and weather conditions. The solution integrates internal sales data with external weather data to support demand optimization and business decision-making.

## Business Problem
Retail demand is strongly influenced by weather conditions such as temperature and precipitation. Without integrating weather data into sales analytics, businesses risk overstocking, understocking, and inefficient pricing decisions.

## Solution
I design and implement an AWS-based data pipeline that:
- Ingests internal sales data and external weather data
- Transforms and enriches the data
- Stores curated analytics-ready datasets
- Enables KPI-driven analysis using SQL

## Technologies Used
- Amazon S3
- AWS Lambda
- AWS Glue
- Amazon Athena

## Repository Structure
- `docs/` – Project documentation (business context, architecture, KPIs, implementation)
- `data/` – Synthetic input datasets
- `architecture/` – Architecture diagrams
- `backfill/` – Python code for the backfilling
- `Athena/` – Sql queries for the creation of the Athena db and for the KPIs
- `data_generation/` – Python code for the synthetic data generation
- `lambda/` – Python code for the openmeteo API call

## Key implementation files
- Synthetic sales generator: [`data_generation/generate_sales.py`](../data_generation/generate_sales.py)
- Weather backfill runner (monthly chunking): [`backfill/backfill.py`](../backfill/backfill.py)
- Athena DB + external table creation: [`Athena/Create_db_in_Athena.sql`](../Athena/Create_db_in_Athena.sql)
- Lambda function code: [`lambda/`](../lambda/)

## Reproducibility (high level)
1. Generate synthetic sales CSV: run `data_generation/generate_sales.py` (or use provided `data/sales_synthetic_2021_2025.csv`)
2. Upload sales CSV to S3 `raw/sales/`
3. Run Lambda ingestion for weather (manual test or backfill via `backfill/backfill.py`)
4. Run Glue Crawlers to create `sales_raw` and `weather_raw` tables
5. Run Glue ETL job to create curated Parquet in `curated/enriched_sales/`
6. Create Athena external table (`Athena/Create_db_in_Athena.sql`) and run KPI queries
