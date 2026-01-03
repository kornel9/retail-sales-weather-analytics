"""
Script Name: Synthetic Sales Generator
Description: 
    Generates a synthetic dataset representing daily sales transactions.
    Used to populate the 'raw/sales' S3 bucket for testing the ETL pipeline 
    without requiring sensitive production data.

Output:
    - Format: CSV
    - Columns: [e.g., date, store_id, product_id, units_sold, revenue]
    - Location: Saves locally to ./data/ or uploads directly to S3 (depending on config).

Usage:
    Run manually: `python generate_sales.py`

Configuration:
    - DATE_RANGE: [e.g., 2021-01-01 to Present]
    - RANDOM_SEED: Fixed for reproducibility.
"""

import csv
import random
from datetime import date, timedelta
import math

# -----------------------------
# CONFIG (business realism)
# -----------------------------
START_DATE = date(2021, 1, 1)
END_DATE   = date(2025, 12, 31)

# Stores (city-level so weather can be pulled by coordinates later)
STORES = [
    {"store": "Budapest", "country": "HU", "lat": 47.4979, "lon": 19.0402},
    {"store": "Vienna",   "country": "AT", "lat": 48.2082, "lon": 16.3738},
    {"store": "Prague",   "country": "CZ", "lat": 50.0755, "lon": 14.4378},
    {"store": "Berlin",   "country": "DE", "lat": 52.5200, "lon": 13.4050},
    {"store": "Warsaw",   "country": "PL", "lat": 52.2297, "lon": 21.0122},
    {"store": "Munich",   "country": "DE", "lat": 48.1351, "lon": 11.5820},
]

# Products: mix of weather-sensitive and stable items
PRODUCTS = [
    {"product": "Ice Cream",     "base_price": 2.7,  "base_demand": 55, "season": "summer"},
    {"product": "Cold Drink",    "base_price": 1.9,  "base_demand": 75, "season": "summer"},
    {"product": "Bottled Water", "base_price": 1.2,  "base_demand": 90, "season": "summer"},
    {"product": "Hot Coffee",    "base_price": 2.2,  "base_demand": 65, "season": "winter"},
    {"product": "Tea",           "base_price": 1.8,  "base_demand": 45, "season": "winter"},
    {"product": "Umbrella",      "base_price": 9.5,  "base_demand": 8,  "season": "rain"},
    {"product": "Snack",         "base_price": 1.5,  "base_demand": 80, "season": "stable"},
    {"product": "Bread",         "base_price": 1.3,  "base_demand": 110,"season": "stable"},
]

random.seed(42)

def daterange(d1, d2):
    d = d1
    while d <= d2:
        yield d
        d += timedelta(days=1)

def month_seasonality_factor(d: date) -> float:
    """
    Smooth yearly seasonality factor using a sine wave.
    Peaks in July (summer demand), low in January (winter).
    """
    day_of_year = d.timetuple().tm_yday
    # Shift so peak ~ mid-year (around day 200)
    return 1.0 + 0.25 * math.sin(2 * math.pi * (day_of_year - 200) / 365.25)

def weekday_factor(d: date) -> float:
    """
    Weekends slightly higher traffic.
    """
    if d.weekday() >= 5:  # 5=Sat, 6=Sun
        return 1.08
    return 1.0

def store_size_multiplier(store_name: str) -> float:
    """
    Pretend some stores are larger.
    """
    size_map = {
        "Budapest": 1.15,
        "Berlin":   1.12,
        "Vienna":   1.05,
        "Munich":   1.00,
        "Warsaw":   0.98,
        "Prague":   0.95,
    }
    return size_map.get(store_name, 1.0)

def promo_probability(d: date) -> float:
    """
    Random promos: more around holidays (Nov-Dec) and summer.
    """
    if d.month in (11, 12):
        return 0.12
    if d.month in (6, 7, 8):
        return 0.08
    return 0.05

def simulate_quantity(product, d: date, store: str) -> int:
    base = product["base_demand"]
    s_mult = store_size_multiplier(store)
    w_mult = weekday_factor(d)
    season = month_seasonality_factor(d)

    # Product-specific season influence
    if product["season"] == "summer":
        # boost in warm months
        season_boost = 1.0 + (0.35 if d.month in (6,7,8) else 0.0) + (0.15 if d.month in (5,9) else 0.0)
    elif product["season"] == "winter":
        season_boost = 1.0 + (0.30 if d.month in (12,1,2) else 0.0) + (0.10 if d.month in (11,3) else 0.0)
    elif product["season"] == "rain":
        # "umbrella" demand higher in spring/autumn (proxy for rain season)
        season_boost = 1.0 + (0.35 if d.month in (3,4,10,11) else 0.0)
    else:
        season_boost = 1.0

    # Random promo event
    promo = 1.0
    if random.random() < promo_probability(d):
        promo = 1.18  # uplift

    # Random noise (normal-ish)
    noise = random.gauss(1.0, 0.12)

    qty = base * s_mult * w_mult * season * season_boost * promo * noise

    # Keep umbrellas low-ish and integer
    qty = max(0, int(round(qty)))

    # Caps for sanity
    if product["product"] == "Umbrella":
        qty = min(qty, 80)
    return qty

def simulate_price(base_price: float, d: date) -> float:
    """
    Small inflation trend + random price jitter.
    """
    years_from_start = (d - START_DATE).days / 365.25
    inflation = 1.0 + 0.03 * years_from_start  # ~3% per year
    jitter = random.gauss(1.0, 0.02)
    price = base_price * inflation * jitter
    return round(price, 2)

output_file = "sales_synthetic_2021_2025.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "store", "country", "lat", "lon", "product", "quantity_sold", "price"])

    for d in daterange(START_DATE, END_DATE):
        for st in STORES:
            for p in PRODUCTS:
                qty = simulate_quantity(p, d, st["store"])
                price = simulate_price(p["base_price"], d)
                writer.writerow([d.isoformat(), st["store"], st["country"], st["lat"], st["lon"], p["product"], qty, price])

print(f"Created {output_file}")
