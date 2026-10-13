from pathlib import Path
from datetime import date

import pandas as pd
import requests


# 1. Define where the downloaded files will be saved.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "data"

DATA_FOLDER.mkdir(parents=True, exist_ok=True)


# 2. Set the location and dates for the data request.
latitude = 23.8103
longitude = 90.4125

start_date = "20240101"
end_date = "20251231"


# 3. Build the NASA POWER API request.
url = "https://power.larc.nasa.gov/api/temporal/daily/point"

params = {
    "parameters": "PRECTOTCORR",
    "community": "RE",
    "longitude": longitude,
    "latitude": latitude,
    "start": start_date,
    "end": end_date,
    "format": "JSON",
    "time-standard": "UTC",
}


# 4. Request the data and check for a failed response.
response = requests.get(url, params=params, timeout=60)
response.raise_for_status()

try:
    payload = response.json()
except ValueError as exc:
    raise ValueError(
        "NASA POWER returned a response that is not valid JSON."
    ) from exc


# 5. Extract the daily precipitation values.
try:
    values = payload["properties"]["parameter"]["PRECTOTCORR"]
except (KeyError, TypeError) as exc:
    raise ValueError(
        "The NASA POWER response did not contain the expected "
        "PRECTOTCORR data. Check the API response and parameters."
    ) from exc

if not isinstance(values, dict) or not values:
    raise ValueError(
        "NASA POWER returned no precipitation records."
    )


# 6. Convert the API response into a DataFrame.
try:
    dates = pd.to_datetime(
        list(values.keys()),
        format="%Y%m%d",
        errors="raise",
    )
except (ValueError, TypeError) as exc:
    raise ValueError(
        "NASA POWER returned a date that could not be parsed."
    ) from exc

data = pd.DataFrame({
    "date": dates,
    "location": "Dhaka_grid_point",
    "rainfall_mm": list(values.values()),
})

# Convert rainfall values to numbers.
data["rainfall_mm"] = pd.to_numeric(
    data["rainfall_mm"],
    errors="coerce",
)

# Treat the documented -999 missing-data marker as missing.
data["rainfall_mm"] = data["rainfall_mm"].replace(
    -999,
    float("nan"),
)

if data.empty:
    raise ValueError("No data rows were created.")

if data["date"].duplicated().any():
    raise ValueError(
        "The downloaded data contains duplicate dates."
    )


# 7. Save the downloaded data.
csv_path = DATA_FOLDER / "rainfall_dhaka.csv"
data.to_csv(csv_path, index=False)


# 8. Save the source details for future readers.
source_text = f"""
Source: NASA POWER Daily API
Parameter: PRECTOTCORR (corrected precipitation)
Expected unit: mm/day; verify against NASA POWER parameter metadata
Location: Dhaka-area grid point
Latitude: {latitude}
Longitude: {longitude}
Requested period: {start_date} to {end_date}
Time standard: UTC
Date retrieved: {date.today().isoformat()}

Note:
These are gridded meteorological estimates, not necessarily
direct measurements from a local rain gauge.
Missing values are represented as NaN in the saved CSV.
The data have not been used to produce a flood forecast.
"""

source_path = DATA_FOLDER / "SOURCE.txt"
source_path.write_text(
    source_text.strip() + "\n",
    encoding="utf-8",
)


# 9. Display a short confirmation.
print("Data download completed.")
print(f"Rows downloaded: {len(data)}")
print(f"Saved data to: {csv_path}")
print(f"Saved source details to: {source_path}")
print(data.head())
