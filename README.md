# rainfall-data-quality-checker
A Python project that retrieves daily precipitation data from NASA POWER and checks for missing values, invalid dates, duplicate records, non-numeric values, and other data-quality issues.
# Bangladesh Environmental Data Quality Checker

## Overview

The Bangladesh Environmental Data Quality Checker is a beginner-level Python project that retrieves daily precipitation data for a grid point near Dhaka, Bangladesh, and checks the dataset for selected data-quality issues.

The program generates a detailed CSV report containing flagged records and a text summary of the quality checks.

## Motivation

Environmental data can contain missing values, invalid entries, repeated records, and unexpected values. Identifying these issues is an important step before using environmental data in further analysis.

This project was developed to practice Python programming, data validation, automated testing, and basic environmental data processing.

It is an introductory data-quality tool. It does not predict rainfall or floods, issue warnings, or establish the accuracy of the source data.

## Data Source

- **Source:** NASA POWER Daily API
- **Official documentation:** https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- **Parameter:** `PRECTOTCORR` (corrected precipitation)
- **Location:** A grid point near Dhaka, Bangladesh
- **Latitude:** 23.8103° N
- **Longitude:** 90.4125° E
- **Requested period:** 1 January 2024 to 31 December 2025
- **Time standard:** UTC

The source details recorded by the download script are available in `data/SOURCE.txt`.

NASA POWER provides gridded meteorological data. These values are not necessarily direct measurements from a local rain gauge and may differ from observations at a specific location.

## Quality Checks

The program checks for the following issues:

- Invalid or unparseable dates
- Missing location names
- Missing rainfall values
- Non-numeric rainfall values
- Non-finite rainfall values, such as infinity
- Negative rainfall values
- Duplicate date-location records

The program also checks that the dataset contains the required columns and at least one record.

Each record receives an issue flag or an `OK` status if it passes the checks implemented in the program. A record marked `OK` is not guaranteed to be accurate or suitable for every type of analysis.

## Tools and Technologies

- Python
- pandas
- requests
- unittest
- NASA POWER Daily API

## Project Structure

```text
rainfall-data-quality-checker/
├── README.md
├── requirements.txt
├── data/
│   ├── SOURCE.txt
│   └── rainfall_dhaka.csv
├── src/
│   ├── fetch_data.py
│   └── quality_checker.py
├── tests/
│   └── test_quality_checker.py
└── outputs/
    ├── flagged_records.csv
    └── summary.txt
```

This structure describes the intended project organization. Generated data and report files may be created when the scripts are run.

## Installation

Python must be installed before running the project.

Install the required packages from the project directory:

```bash
py -m pip install -r requirements.txt
```

The `requirements.txt` file should list the Python packages required by the project, including `pandas` and `requests`.

## How to Run

### 1. Download the rainfall data

```bash
py src/fetch_data.py
```

This script requests daily precipitation data from NASA POWER and saves the downloaded records and source information in the `data/` directory.

### 2. Run the quality checker

```bash
py src/quality_checker.py
```

This script checks the downloaded dataset and generates the quality reports in the `outputs/` directory.

### 3. Run the automated tests

```bash
py -m unittest discover -s tests -v
```

The tests check whether selected quality issues are detected as expected. Passing tests indicate that the tested behavior worked for the test cases provided; they do not guarantee that every possible data-quality issue has been identified.

If your system uses `python` instead of `py`, replace `py` with `python` in these commands.

## Outputs

The quality checker generates two reports:

- `outputs/flagged_records.csv` — contains records identified as having one or more quality issues.
- `outputs/summary.txt` — contains a summary of the checks and the number of records affected by each issue.

The number of flagged records and the individual issue counts may differ because one record can have multiple issues.

### Results

After running the project, record the actual results from `outputs/summary.txt` here.

- **Total records checked:** [Enter actual count]
- **Records with one or more flags:** [Enter actual count]
- **Invalid dates:** [Enter actual count]
- **Missing rainfall values:** [Enter actual count]
- **Non-numeric rainfall values:** [Enter actual count]
- **Non-finite rainfall values:** [Enter actual count]
- **Negative rainfall values:** [Enter actual count]
- **Duplicate date-location records:** [Enter actual count]

Replace these placeholders with your own results before publishing the repository.

## Limitations

- The checks identify possible data-quality issues but do not establish the cause of a flagged value.
- A record marked `OK` may still contain inaccurate or unsuitable data.
- Duplicate date-location records are flagged rather than automatically deleted.
- The current implementation does not detect missing calendar dates between observations.
- Gridded precipitation estimates may differ from local rain-gauge measurements.
- The checks do not validate every possible scientific or meteorological property of the dataset.
- The project does not perform rainfall forecasting, flood prediction, or warning generation.

## Future Improvements

Possible future improvements include:

- Detecting missing calendar dates within the observed period
- Expanding automated test coverage
- Adding visual summaries of data-quality results
- Comparing gridded precipitation estimates with independent observations
- Applying the quality checks to additional environmental datasets

## Author

Safa Marowa Tasfia

## Citation and Data Use

The precipitation data are obtained from NASA POWER. Users should consult NASA POWER's current documentation and data-use guidance when reusing or citing the source data.

Any licence applied to this project's code does not automatically apply to the source data.
