"""Small validation checks for empty, incomplete, and malformed feedback."""

from io import StringIO
import unittest

from feedback_utils import load_feedback


class FeedbackLoadingTests(unittest.TestCase):
    def test_empty_csv_returns_empty_data_with_notice(self):
        data, issues = load_feedback(StringIO("session,rating,topic_category,comment\n"))
        self.assertTrue(data.empty)
        self.assertEqual(issues, [])

    def test_missing_optional_comment_is_added(self):
        data, issues = load_feedback(StringIO("session,rating,topic_category\nA,5,Data\n"))
        self.assertEqual(data.loc[0, "comment"], "")
        self.assertTrue(any("Optional 'comment'" in issue for issue in issues))

    def test_missing_required_column_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "topic_category"):
            load_feedback(StringIO("session,rating\nA,4\n"))

    def test_missing_values_and_invalid_ratings_are_skipped(self):
        csv = "session,rating,topic_category,comment\nA,5,Data,ok\nA,,Data,missing\nB,6,Tools,too high\n,3,Data,no session\n"
        data, issues = load_feedback(StringIO(csv))
        self.assertEqual(len(data), 1)
        self.assertEqual(data.loc[0, "rating"], 5)
        self.assertTrue(any("Skipped 3 row(s)" in issue for issue in issues))

    def test_non_numeric_and_fractional_ratings_are_skipped(self):
        csv = "session,rating,topic_category\nA,good,Data\nB,2.5,Tools\nC,1,Data\n"
        data, issues = load_feedback(StringIO(csv))
        self.assertEqual(data["session"].tolist(), ["C"])
        self.assertTrue(any("Skipped 2 row(s)" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
