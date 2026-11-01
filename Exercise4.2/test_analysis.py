"""Validation and output checks for the service desk analysis."""

import tempfile
import unittest
from pathlib import Path

from service_desk_analysis import analyze, build_summary, load_tickets


class ServiceDeskAnalysisTests(unittest.TestCase):
    def test_sample_rows_load_and_have_expected_summaries(self):
        tickets, rejected = load_tickets(Path(__file__).with_name("tickets.csv"))
        self.assertEqual(len(tickets), 36)
        self.assertEqual(rejected, 0)
        summary = build_summary(tickets)
        overall = summary.loc[summary["metric"] == "Overall"].iloc[0]
        self.assertAlmostEqual(overall["mean_hours"], tickets["resolution_hours"].mean())
        self.assertAlmostEqual(overall["median_hours"], tickets["resolution_hours"].median())
        self.assertAlmostEqual(overall["maximum_hours"], tickets["resolution_hours"].max())

    def test_bad_rows_are_counted_and_missing_columns_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text(
                "ticket_id,category,priority,opened_date,resolution_hours,status\n"
                "T1,Access,P1,2026-10-01,1,Resolved\n"
                "T2,Access,P8,2026-10-01,2,Resolved\n"
                "T3,Access,P1,bad,3,Resolved\n"
                "T4,Access,P1,2026-10-01,inf,Open\n"
                "T1,Network,P2,2026-10-02,4,Open\n",
                encoding="utf-8",
            )
            data, rejected = load_tickets(path)
            self.assertEqual(len(data), 1)
            self.assertEqual(rejected, 4)
            path.write_text("ticket_id,category\nT1,Access\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "opened_date"):
                load_tickets(path)

    def test_analysis_writes_summary_interpretation_and_four_pngs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            analyze(Path(__file__).with_name("tickets.csv"), output)
            expected = {
                "summary_table.csv", "interpretation.md", "tickets_by_category.png",
                "resolution_histogram.png", "weekly_ticket_volume.png", "priority_vs_hours.png",
            }
            self.assertTrue(expected.issubset({item.name for item in output.iterdir()}))
            self.assertTrue(all((output / name).stat().st_size > 1000 for name in expected if name.endswith(".png")))


if __name__ == "__main__":
    unittest.main()
