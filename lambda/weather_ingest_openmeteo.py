import os
import json
import urllib.request
from datetime import datetime, date
import csv
import io
import boto3

s3 = boto3.client("s3")

BUCKET_NAME = os.environ.get("BUCKET_NAME", "")

# Store coordinates MUST match the sales dataset values (lat/lon).
# These are the same cities used in the generator script.
STORES = [
    {"store": "Budapest", "country": "HU", "lat": 47.4979, "lon": 19.0402},
    {"store": "Vienna",   "country": "AT", "lat": 48.2082, "lon": 16.3738},
    {"store": "Prague",   "country": "CZ", "lat": 50.0755, "lon": 14.4378},
    {"store": "Berlin",   "country": "DE", "lat": 52.5200, "lon": 13.4050},
    {"store": "Warsaw",   "country": "PL", "lat": 52.2297, "lon": 21.0122},
    {"store": "Munich",   "country": "DE", "lat": 48.1351, "lon": 11.5820},
]

def _iso(d: date) -> str:
    return d.strftime("%Y-%m-%d")

def fetch_open_meteo_daily(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    """
    Fetch daily weather from Open-Meteo for the given lat/lon and date range (inclusive).
    We request daily mean temperature + precipitation sum (simple and useful for retail demand).
    """
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        "&daily=temperature_2m_mean,precipitation_sum"
        "&timezone=UTC"
    )

    with urllib.request.urlopen(url, timeout=20) as resp:
        data = resp.read().decode("utf-8")
        return json.loads(data)

def lambda_handler(event, context):
    """
    Supports two modes:
    1) Backfill mode: event contains start_date and end_date (YYYY-MM-DD).
       Example: {"start_date":"2021-01-01","end_date":"2021-01-31"}
    2) Default daily mode: if no dates provided, fetch yesterday only.
    """
    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME environment variable is missing.")

    # Parse date range
    start = event.get("start_date")
    end = event.get("end_date")

    if not start or not end:
        # Default: yesterday in UTC
        today_utc = datetime.utcnow().date()
        yday = today_utc.fromordinal(today_utc.toordinal() - 1)
        start = _iso(yday)
        end = _iso(yday)

    # Validate formatting quickly
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("start_date and end_date must be in YYYY-MM-DD format.")

    if end_dt < start_dt:
        raise ValueError("end_date must be >= start_date.")

    year = start_dt.strftime("%Y")
    month = start_dt.strftime("%m")

    # We'll write a single CSV per backfill chunk (month) containing all stores.
    # Raw weather path:
    # raw/weather/year=YYYY/month=MM/weather_YYYY-MM-DD_to_YYYY-MM-DD.csv
    key = f"raw/weather/year={year}/month={month}/weather_{start}_to_{end}.csv"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "date", "store", "country", "lat", "lon", "temperature_2m_mean", "precipitation_sum"
    ])

    total_rows = 0

    for st in STORES:
        data = fetch_open_meteo_daily(st["lat"], st["lon"], start, end)

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temps = daily.get("temperature_2m_mean", [])
        precs = daily.get("precipitation_sum", [])

        # Defensive: ensure same length
        n = min(len(dates), len(temps), len(precs))

        for i in range(n):
            writer.writerow([
                dates[i],
                st["store"],
                st["country"],
                st["lat"],
                st["lon"],
                temps[i],
                precs[i],
            ])
            total_rows += 1

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=output.getvalue().encode("utf-8"),
        ContentType="text/csv"
    )

    return {
        "status": "ok",
        "s3_bucket": BUCKET_NAME,
        "s3_key": key,
        "rows_written": total_rows,
        "start_date": start,
        "end_date": end
    }
