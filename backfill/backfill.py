#!/bin/bash
set -euo pipefail

FUNCTION_NAME="weather_ingest_openmeteo"

# Backfill range: 2021-01 to 2025-12
START_YEAR=2021
END_YEAR=2025

# Small pause between calls to be polite to the API and avoid throttling
SLEEP_SECONDS=1

echo "Starting backfill for ${START_YEAR}-01 to ${END_YEAR}-12..."

for year in $(seq $START_YEAR $END_YEAR); do
  for month in $(seq -w 1 12); do

    # Compute start_date = first of month
    start_date="${year}-${month}-01"

    # Compute end_date = last day of month using Python (portable)
    end_date=$(python3 - <<PY
import calendar
y=${year}
m=int("${month}")
last_day=calendar.monthrange(y,m)[1]
print(f"{y}-{m:02d}-{last_day:02d}")
PY
)

    payload="{\"start_date\":\"${start_date}\",\"end_date\":\"${end_date}\"}"

    echo "Invoking Lambda for ${start_date} to ${end_date} ..."

    # Invoke Lambda and store response
    aws lambda invoke \
      --function-name "${FUNCTION_NAME}" \
      --cli-binary-format raw-in-base64-out \
      --payload "${payload}" \
      "out_${year}_${month}.json" > /dev/null

    # Print a quick summary line from response
    status=$(python3 - <<PY
import json
f="out_${year}_${month}.json"
d=json.load(open(f))
print(d.get("status"), d.get("rows_written"), d.get("s3_key"))
PY
)
    echo "  -> ${status}"

    sleep ${SLEEP_SECONDS}
  done
done

echo "Backfill completed."
