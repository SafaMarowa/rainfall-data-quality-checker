from pathlib import Path

import pandas as pd


# 1. Find the project folders.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "rainfall_dhaka.csv"
OUTPUT_FOLDER = PROJECT_ROOT / "outputs"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def check_quality(data):
    """Check rainfall data and return flagged records and a summary."""

    # 2. Check that the expected columns exist.
    required_columns = {"date", "location", "rainfall_mm"}
    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if data.empty:
        raise ValueError(
            "The dataset contains no records to check."
        )

    checked = data.copy()

    # 3. Interpret dates without deleting the original values.
    parsed_date = pd.to_datetime(
        checked["date"],
        errors="coerce",
    )

    # 4. Standardize location text for checking.
    location = checked["location"].astype("string").str.strip()

    missing_location = (
        location.isna() | location.eq("").fillna(True)
    )

    # 5. Check rainfall values.
    raw_rainfall = checked["rainfall_mm"]

    missing_rainfall = (
        raw_rainfall.isna()
        | raw_rainfall.astype("string").str.strip().eq("").fillna(True)
    )

    numeric_rainfall = pd.to_numeric(
        raw_rainfall,
        errors="coerce",
    )

    non_numeric_rainfall = (
        ~missing_rainfall & numeric_rainfall.isna()
    )

    # Detect positive and negative infinity without NumPy.
    non_finite_rainfall = (
        numeric_rainfall.notna()
        & numeric_rainfall.isin([float("inf"), float("-inf")])
    )

    # Negative infinity is reported as non-finite, not negative.
    negative_rainfall = (
        numeric_rainfall.lt(0).fillna(False)
        & ~non_finite_rainfall
    )

    # 6. Identify duplicate valid date/location combinations.
    duplicate_keys = pd.DataFrame({
        "date": parsed_date.dt.strftime("%Y-%m-%d"),
        "location": location,
    })

    duplicate_record = (
        duplicate_keys.duplicated(
            subset=["date", "location"],
            keep=False,
        )
        & parsed_date.notna()
        & ~missing_location
    )
    
    # 6A. Identify missing calendar dates within each location's
    # observed date range.
    missing_dates_by_location = {}

    valid_date_rows = parsed_date.notna() & ~missing_location

    for loc in location[valid_date_rows].unique():
        loc_dates = parsed_date[
            valid_date_rows & location.eq(loc).fillna(False)
        ].dt.normalize()

        if loc_dates.empty:
            continue

        expected_dates = pd.date_range(
            start=loc_dates.min(),
            end=loc_dates.max(),
            freq="D",
        )

        observed_dates = pd.DatetimeIndex(loc_dates.unique())
        missing_dates = expected_dates.difference(observed_dates)

        if len(missing_dates) > 0:
            missing_dates_by_location[str(loc)] = [
                day.strftime("%Y-%m-%d")
                for day in missing_dates
            ]

    # 7. Give every record its own list of issues.
    flags = []

    for i in range(len(checked)):
        row_issues = []

        if pd.isna(parsed_date.iloc[i]):
            row_issues.append("invalid_date")

        if missing_location.iloc[i]:
            row_issues.append("missing_location")

        if missing_rainfall.iloc[i]:
            row_issues.append("missing_rainfall")

        if non_numeric_rainfall.iloc[i]:
            row_issues.append("non_numeric_rainfall")

        if non_finite_rainfall.iloc[i]:
            row_issues.append("non_finite_rainfall")

        if negative_rainfall.iloc[i]:
            row_issues.append("negative_rainfall")

        if duplicate_record.iloc[i]:
            row_issues.append("duplicate_date_location")

        if not row_issues:
            row_issues.append("OK")

        flags.append("; ".join(row_issues))

    # 8. Keep the original records and attach the flags.
    results = checked.copy()
    results["issue_flags"] = flags

    # 9. Calculate the summary.
    summary = {
        "rows_checked": len(checked),
        "locations_with_missing_dates": len(missing_dates_by_location),
        "missing_dates_count": sum(
            len(days) for days in missing_dates_by_location.values()
        ),
        "records_with_flags": int(
            (results["issue_flags"] != "OK").sum()
        ),
        "invalid_dates": int(parsed_date.isna().sum()),
        "missing_locations": int(missing_location.sum()),
        "missing_rainfall": int(missing_rainfall.sum()),
        "non_numeric_rainfall": int(non_numeric_rainfall.sum()),
        "non_finite_rainfall": int(non_finite_rainfall.sum()),
        "negative_rainfall": int(negative_rainfall.sum()),
        "duplicate_date_location_records": int(
            duplicate_record.sum()
        ),
    }

    return results, summary


def main():
    # 10. Load the saved dataset.
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Data file not found. Run src/fetch_data.py first."
        )

    data = pd.read_csv(DATA_FILE)

    # 11. Run the checks.
    results, summary = check_quality(data)

    # 12. Save only flagged records in the detailed report.
    flagged = results[results["issue_flags"] != "OK"]

    flagged_path = OUTPUT_FOLDER / "flagged_records.csv"
    flagged.to_csv(flagged_path, index=False)

    # 13. Save the summary in a readable text file.
    summary_lines = [
        "ENVIRONMENTAL DATA QUALITY REPORT",
        "",
        "Interpretation: OK means a record passed the checks "
        "implemented in this program.",
        "It does not prove that the source measurement is accurate "
        "or suitable for flood forecasting.",
        "",
    ]

    for name, value in summary.items():
        summary_lines.append(f"{name}: {value}")

    summary_path = OUTPUT_FOLDER / "summary.txt"
    summary_path.write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8",
    )

    # 14. Show the results.
    print("\nQUALITY CHECK SUMMARY")

    for name, value in summary.items():
        print(f"{name}: {value}")

    print(f"\nDetailed report: {flagged_path}")
    print(f"Summary report: {summary_path}")


if __name__ == "__main__":
    main()
