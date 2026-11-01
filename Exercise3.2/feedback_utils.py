"""CSV loading and validation helpers for the feedback explorer."""

from pathlib import Path
from typing import BinaryIO

import pandas as pd

REQUIRED_COLUMNS = {"session", "rating", "topic_category"}
OPTIONAL_COLUMNS = {"comment"}


def load_feedback(source: str | Path | BinaryIO) -> tuple[pd.DataFrame, list[str]]:
    """Load CSV data, standardize expected columns, and report row issues."""
    try:
        frame = pd.read_csv(source)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse CSV: {exc}") from exc

    frame.columns = [str(column).strip().lower() for column in frame.columns]
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))

    issues: list[str] = []
    if "comment" not in frame.columns:
        frame["comment"] = ""
        issues.append("Optional 'comment' column not found; comments are blank.")

    frame["session"] = frame["session"].astype("string").str.strip()
    frame["topic_category"] = frame["topic_category"].astype("string").str.strip()
    rating = pd.to_numeric(frame["rating"], errors="coerce")
    valid_rating = rating.between(1, 5) & (rating % 1 == 0)
    valid = (
        frame["session"].notna()
        & frame["session"].ne("")
        & frame["topic_category"].notna()
        & frame["topic_category"].ne("")
        & valid_rating
    )
    rejected = int((~valid).sum())
    if rejected:
        issues.append(
            f"Skipped {rejected} row(s) with missing session/category or invalid rating (ratings must be whole numbers 1–5)."
        )

    frame = frame.loc[valid].copy()
    frame["rating"] = rating.loc[valid].astype("int64")
    frame["comment"] = frame["comment"].fillna("").astype("string")
    return frame.reset_index(drop=True), issues
