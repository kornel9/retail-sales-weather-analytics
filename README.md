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
