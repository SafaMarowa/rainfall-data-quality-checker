import sys
import unittest
from pathlib import Path

import pandas as pd


# Allow this test file to import the program from src/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from quality_checker import check_quality


class TestQualityChecker(unittest.TestCase):

    def test_detects_negative_rainfall(self):
        data = pd.DataFrame({
            "date": ["2024-01-01"],
            "location": ["Test Station"],
            "rainfall_mm": [-2.0],
        })

        results, summary = check_quality(data)

        self.assertIn(
            "negative_rainfall",
            results.loc[0, "issue_flags"],
        )
        self.assertEqual(summary["negative_rainfall"], 1)
    
    def test_detects_missing_date(self):
        data = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-03"],
            "location": ["Test Station", "Test Station"],
            "rainfall_mm": [10.0, 12.0],
        })

        results, summary = check_quality(data)

        self.assertEqual(summary["missing_dates_count"], 1)
        self.assertEqual(
            summary["locations_with_missing_dates"], 1
        )

    def test_detects_duplicate_date_and_location(self):
        data = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-01"],
            "location": ["Test Station", "Test Station"],
            "rainfall_mm": [10.0, 12.0],
        })

        results, summary = check_quality(data)

        self.assertIn(
            "duplicate_date_location",
            results.loc[0, "issue_flags"],
        )
        self.assertIn(
            "duplicate_date_location",
            results.loc[1, "issue_flags"],
        )

        self.assertEqual(
            summary["duplicate_date_location_records"], 2
        )

    def test_detects_missing_rainfall(self):
        data = pd.DataFrame({
            "date": ["2024-01-01"],
            "location": ["Test Station"],
            "rainfall_mm": [float("nan")],
        })

        results, summary = check_quality(data)

        self.assertIn(
            "missing_rainfall",
            results.loc[0, "issue_flags"],
        )
        self.assertEqual(summary["missing_rainfall"], 1)

    def test_detects_invalid_date(self):
        data = pd.DataFrame({
            "date": ["not-a-date"],
            "location": ["Test Station"],
            "rainfall_mm": [10.0],
        })

        results, summary = check_quality(data)

        self.assertIn(
            "invalid_date",
            results.loc[0, "issue_flags"],
        )
        self.assertEqual(summary["invalid_dates"], 1)

    def test_detects_non_numeric_rainfall(self):
        data = pd.DataFrame({
            "date": ["2024-01-01"],
            "location": ["Test Station"],
            "rainfall_mm": ["unknown"],
        })

        results, summary = check_quality(data)

        self.assertIn(
            "non_numeric_rainfall",
            results.loc[0, "issue_flags"],
        )
        self.assertEqual(summary["non_numeric_rainfall"], 1)

    def test_detects_infinite_rainfall(self):
        data = pd.DataFrame({
            "date": ["2024-01-01"],
            "location": ["Test Station"],
            "rainfall_mm": [float("inf")],
        })

        results, summary = check_quality(data)

        self.assertIn(
            "non_finite_rainfall",
            results.loc[0, "issue_flags"],
        )
        self.assertEqual(summary["non_finite_rainfall"], 1)

    def test_rejects_missing_required_column(self):
        data = pd.DataFrame({
            "date": ["2024-01-01"],
            "location": ["Test Station"],
        })

        with self.assertRaisesRegex(
            ValueError, "Missing required columns"
        ):
            check_quality(data)

    def test_rejects_empty_dataset(self):
        data = pd.DataFrame({
            "date": [],
            "location": [],
            "rainfall_mm": [],
        })

        with self.assertRaisesRegex(
            ValueError, "contains no records"
        ):
            check_quality(data)


if __name__ == "__main__":
    unittest.main()
