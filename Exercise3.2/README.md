# Exercise 3.2 — Streamlit Workshop Feedback Explorer

An interactive explorer for **synthetic, anonymous** workshop feedback. It validates CSV columns and ratings, summarizes satisfaction, filters sessions and rating ranges, and supports downloading the filtered rows.

## Run it

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app loads `feedback.csv` by default. Use the uploader to inspect another CSV. Required columns are `session`, `rating` (whole number 1–5), and `topic_category`. `comment` is optional. Missing required columns stop the app with a clear message; missing/invalid row values are skipped with a notice. If `comment` is absent it is added as blank.

## Features

- Response count, mean rating, rating distribution, low-rated session summary (mean below 3.0), and average rating by session.
- Session and rating-range filters update all summaries and the table.
- Optional comments appear as plain text; the data table also escapes uploaded values.
- Download filtered records as CSV.

## Validation test table

| Case | Input | Expected result |
|---|---|---|
| Empty data | Headers only, no rows | Empty result without a crash; app explains there are no valid responses |
| Missing required column | Omit `topic_category` | Clear validation error names the missing column |
| Missing optional column | Omit `comment` | Load succeeds, blank comment column is added with a notice |
| Missing values | Blank session/category/rating | Invalid row is skipped and counted |
| Invalid rating | Text, fraction, 0, or 6 | Row is skipped; only integer ratings 1–5 remain |

Run validation checks with `python -m unittest -v`.

## Sample interpretation

The supplied CSV contains 16 synthetic responses. Session 1 averages **4.00**, Session 2 **3.25**, Session 3 **3.50**, and Session 4 **2.75**. Session 4 is the only low-rated session under the app's mean-below-3.0 rule; its comments point to pacing and a desire for a longer practical demonstration. These small synthetic results are for demonstrating the interface only.

## Screenshots

Run the app and capture the filter and summary views for your lab submission. The app was opened locally and its filters, metrics, charts, and low-rated session table were verified.

## Privacy

This exercise uses synthetic feedback. Do not collect or upload names, email addresses, or other personal identifiers.
