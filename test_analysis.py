"""Unit and smoke tests. Run: python -m unittest -v"""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from analysis import DATA_FILE, WARNING, build_summary, generate, load_data, validate_data


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.document, self.rows = load_data()

    def test_source_values_and_provenance(self):
        self.assertEqual(self.document["warning"], WARNING)
        self.assertIn("no observed trips", self.document["provenance"])
        self.assertEqual(
            [(r["mode"], r["p50"], r["p90"]) for r in self.rows],
            [
                ("Bicycle", 14, 20),
                ("Public bus", 18, 38),
                ("Campus shuttle", 20, 30),
                ("Walking", 25, 28),
            ],
        )

    def test_exact_derived_values_and_orders(self):
        summary = build_summary(self.document, self.rows)
        self.assertEqual(
            {r["mode"]: r["extra_allowance"] for r in summary["rows"]},
            {"Bicycle": 6, "Public bus": 20, "Campus shuttle": 10, "Walking": 3},
        )
        self.assertEqual(summary["p50_order"],
                         ["Bicycle", "Public bus", "Campus shuttle", "Walking"])
        self.assertEqual(summary["extra_allowance_order"],
                         ["Public bus", "Campus shuttle", "Bicycle", "Walking"])
        self.assertEqual(summary["public_bus_minus_walking"],
                         {"p50_minutes": -7, "p90_minutes": 10})
        self.assertEqual(summary["observed_trip_count"], 0)

    def test_valid_zero_and_equal_quantiles(self):
        document = copy.deepcopy(self.document)
        document["data"] = [{"mode": "Illustration", "p50": 0, "p90": 0}]
        rows = validate_data(document)
        self.assertEqual(build_summary(document, rows)["rows"][0]["extra_allowance"], 0)

    def test_decimal_values(self):
        document = copy.deepcopy(self.document)
        document["data"] = [{"mode": "Illustration", "p50": 1.5, "p90": 2.75}]
        rows = validate_data(document)
        self.assertEqual(build_summary(document, rows)["rows"][0]["extra_allowance"], 1.25)

    def test_empty_and_non_list_data_rejected(self):
        for invalid in ([], None, {}, "data"):
            with self.subTest(invalid=invalid):
                document = copy.deepcopy(self.document)
                document["data"] = invalid
                with self.assertRaises(ValueError):
                    validate_data(document)

    def test_duplicate_modes_rejected_case_insensitively(self):
        document = copy.deepcopy(self.document)
        document["data"].append({"mode": " bicycle ", "p50": 10, "p90": 20})
        with self.assertRaises(ValueError):
            validate_data(document)

    def test_bad_numbers_and_reversed_quantiles_rejected(self):
        for invalid in (-1, True, "14", None, float("inf"), float("nan")):
            for field in ("p50", "p90"):
                with self.subTest(invalid=invalid, field=field):
                    document = copy.deepcopy(self.document)
                    document["data"][0][field] = invalid
                    with self.assertRaises(ValueError):
                        validate_data(document)
        document = copy.deepcopy(self.document)
        document["data"][0]["p90"] = 13
        with self.assertRaises(ValueError):
            validate_data(document)

    def test_missing_metadata_rejected(self):
        for key in ("warning", "units", "provenance"):
            with self.subTest(key=key):
                document = copy.deepcopy(self.document)
                del document[key]
                with self.assertRaises(ValueError):
                    validate_data(document)

    def test_invalid_record_and_mode_rejected(self):
        for invalid_row in (None, [], {"mode": "", "p50": 1, "p90": 2},
                            {"mode": 5, "p50": 1, "p90": 2}):
            with self.subTest(row=invalid_row):
                document = copy.deepcopy(self.document)
                document["data"] = [invalid_row]
                with self.assertRaises(ValueError):
                    validate_data(document)
        with self.assertRaises(ValueError):
            validate_data([])

    def test_input_not_mutated(self):
        before = copy.deepcopy(self.document)
        rows = validate_data(self.document)
        build_summary(self.document, rows)
        self.assertEqual(self.document, before)
        rows[0]["p50"] = 999
        self.assertEqual(self.document, before)

    def test_outputs_are_complete_and_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first", Path(directory) / "second"
            expected = generate(DATA_FILE, first)
            generate(DATA_FILE, second)
            files = sorted(p.name for p in first.iterdir())
            self.assertEqual(files, [
                "01_time_comparison.png", "01_time_comparison.svg",
                "02_extra_allowance.png", "02_extra_allowance.svg", "summary.json",
            ])
            for name in files:
                with self.subTest(name=name):
                    self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
                    if name.endswith(".svg"):
                        self.assertIn(WARNING, (first / name).read_text(encoding="utf-8"))
                    if name.endswith(".png"):
                        self.assertTrue((first / name).read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(
                json.loads((first / "summary.json").read_text(encoding="utf-8")), expected
            )


if __name__ == "__main__":
    unittest.main()
