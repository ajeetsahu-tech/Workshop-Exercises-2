# Exercise 4.2 — Service Desk Performance Visualization

Analysis of simulated service desk tickets with row validation, descriptive statistics, four Matplotlib charts, a CSV summary table, and a written interpretation.

## Run

```bash
python -m pip install -r requirements.txt
python service_desk_analysis.py
```

Defaults to `tickets.csv` and writes files under `output/`. To select paths, use `--input PATH --output DIRECTORY`.

## Data rules

Required columns: `ticket_id`, `category`, `priority`, `opened_date`, `resolution_hours`, and `status`. Priority must be P1–P4; dates use ISO `YYYY-MM-DD`; hours must be finite, numeric, and nonnegative; status must be Open or Resolved. Malformed or duplicate-ID rows are counted and skipped. Missing required columns stop analysis with an error.

## Outputs

- `output/summary_table.csv` — mean, median, and maximum recorded hours overall and by status.
- `output/tickets_by_category.png` — category counts.
- `output/resolution_histogram.png` — recorded hours distribution.
- `output/weekly_ticket_volume.png` — weekly opened-ticket volume.
- `output/priority_vs_hours.png` — priority code against recorded hours.
- `output/interpretation.md` — one-page style interpretation, open/resolved comparison, and limitations.

The input is synthetic. For open tickets, `resolution_hours` is elapsed-to-date, not a completed resolution duration. P1=1 to P4=4 is an ordinal label; numeric spacing does not represent equal priority differences. Neither the scatter plot nor open/resolved comparison supports causal claims.

## Validation checks

Run `python -m unittest -v` to check required-column handling, malformed/missing rows, descriptive statistics, and generation of all chart files.
