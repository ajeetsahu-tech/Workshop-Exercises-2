"""Clean synthetic service desk tickets, summarize them, and save charts."""

import argparse
import csv
import math
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import mean, median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REQUIRED = {"ticket_id", "category", "priority", "opened_date", "resolution_hours", "status"}
PRIORITY_CODES = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
VALID_STATUS = {"open", "resolved"}


def load_tickets(path):
    """Return a validated DataFrame and count of rejected rows."""
    accepted, rejected, ids = [], 0, set()
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        columns = {column.strip().lower() for column in (reader.fieldnames or [])}
        missing = sorted(REQUIRED - columns)
        if missing:
            raise ValueError("Missing required column(s): " + ", ".join(missing))
        # Normalize case/whitespace in the header while preserving original CSV rows.
        source.seek(0)
        reader = csv.DictReader(source)
        reader.fieldnames = [name.strip().lower() for name in (reader.fieldnames or [])]
        for row in reader:
            try:
                ticket_id = (row.get("ticket_id") or "").strip()
                category = (row.get("category") or "").strip()
                priority = (row.get("priority") or "").strip().upper()
                opened = date.fromisoformat((row.get("opened_date") or "").strip())
                hours = float(row.get("resolution_hours", ""))
                status = (row.get("status") or "").strip().title()
                if (not ticket_id or ticket_id in ids or not category or priority not in PRIORITY_CODES
                        or hours < 0 or not math.isfinite(hours) or status.lower() not in VALID_STATUS):
                    raise ValueError("Invalid field")
                ids.add(ticket_id)
                accepted.append({"ticket_id": ticket_id, "category": category, "priority": priority,
                                 "priority_code": PRIORITY_CODES[priority], "opened_date": pd.Timestamp(opened),
                                 "resolution_hours": hours, "status": status})
            except (ValueError, TypeError, AttributeError):
                rejected += 1
    columns = ["ticket_id", "category", "priority", "priority_code", "opened_date", "resolution_hours", "status"]
    return pd.DataFrame(accepted, columns=columns), rejected


def build_summary(tickets):
    """Build overall numeric summary rows and a per-status comparison."""
    values = tickets["resolution_hours"].tolist()
    rows = []
    if values:
        rows.extend([
            {"metric": "Overall", "responses": len(values), "mean_hours": mean(values),
             "median_hours": median(values), "maximum_hours": max(values)},
        ])
    for status, group in tickets.groupby("status", sort=True):
        sample = group["resolution_hours"].tolist()
        rows.append({"metric": status, "responses": len(sample), "mean_hours": mean(sample),
                     "median_hours": median(sample), "maximum_hours": max(sample)})
    return pd.DataFrame(rows, columns=["metric", "responses", "mean_hours", "median_hours", "maximum_hours"])


def write_interpretation(tickets, rejected, summary, output_dir):
    total = len(tickets)
    category_counts = tickets["category"].value_counts()
    if total:
        busiest_names = category_counts[category_counts == category_counts.max()].index.tolist()
        if len(busiest_names) > 1:
            busiest_summary = (f"{', '.join(busiest_names)} tie for the highest count "
                               f"({int(category_counts.max())} tickets each) in this sample.")
        else:
            busiest_summary = (f"{busiest_names[0]} has the highest count "
                               f"({int(category_counts.max())} tickets) in this sample.")
    else:
        busiest_summary = "No category counts are available."
    weekly = tickets.assign(week=tickets["opened_date"].dt.to_period("W")).groupby("week").size() if total else pd.Series(dtype=int)
    if len(weekly):
        peak_weeks = len(weekly[weekly == weekly.max()])
        if peak_weeks > 1:
            peak_week_summary = f"All {peak_weeks} weeks tie for the highest volume ({int(weekly.max())} tickets per week)."
        else:
            peak_week_summary = (f"{weekly.idxmax()} is busiest at {int(weekly.max())} tickets.")
    else:
        peak_week_summary = "No weekly volume is available."
    resolved = tickets[tickets["status"] == "Resolved"]["resolution_hours"]
    opened = tickets[tickets["status"] == "Open"]["resolution_hours"]
    comparison = ""
    if len(resolved) and len(opened):
        comparison = (f"\n\nThe synthetic open-ticket group has a mean recorded elapsed time of {opened.mean():.1f} hours, "
                      f"compared with {resolved.mean():.1f} hours for resolved tickets. This is descriptive only: "
                      "status groups can differ in age and case mix, so this comparison does not show that status caused a delay.")
    text = f"""# Service Desk Performance — Interpretation

## Data and summary

This report uses **synthetic workshop data only**: {total} valid tickets and {rejected} rejected malformed row(s). No people or real support operations are represented. Average resolution-time measures below include the recorded elapsed hours for both open and resolved records; for open tickets these are elapsed-to-date values, not completed resolution times.

| Metric | Tickets | Mean hours | Median hours | Maximum hours |
|---|---:|---:|---:|---:|
"""
    for row in summary.itertuples(index=False):
        text += f"| {row.metric} | {row.responses} | {row.mean_hours:.1f} | {row.median_hours:.1f} | {row.maximum_hours:.1f} |\n"
    text += f"""
## What the plots show

- **Tickets by category:** {busiest_summary} Counts describe this generated dataset, not expected real-world workload.
- **Resolution-time histogram:** shows the spread and concentration of recorded hours. Open tickets are elapsed-to-date, so their values are not final resolution durations.
- **Weekly ticket volume:** {peak_week_summary} Weekly totals can move because of the small synthetic sample.
- **Priority versus hours:** priority is coded P1=1 (highest) through P4=4 (lowest); the scatter plot displays individual records but does not establish a causal relationship. Each priority band has few examples and category/case complexity is not controlled.
{comparison}

## Limitations

All rows are simulated, the sample is small, priority uses an ordinal code with equal numeric spacing only for plotting, and no service-level targets or case complexity are included. Do not use these plots to judge staff or make operational claims.
"""
    (Path(output_dir) / "interpretation.md").write_text(text, encoding="utf-8")


def analyze(input_csv, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    tickets, rejected = load_tickets(input_csv)
    if tickets.empty:
        raise ValueError("No valid ticket rows remain after validation.")

    summary = build_summary(tickets)
    summary.to_csv(output / "summary_table.csv", index=False, float_format="%.2f")
    write_interpretation(tickets, rejected, summary, output)
    plt.style.use("seaborn-v0_8-whitegrid")

    counts = tickets["category"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(counts.index, counts.values, color="#278c98", label="Tickets")
    ax.set(title="Synthetic Tickets by Category", xlabel="Category", ylabel="Ticket count")
    ax.tick_params(axis="x", rotation=20)
    ax.legend()
    fig.tight_layout(); fig.savefig(output / "tickets_by_category.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(tickets["resolution_hours"], bins=8, color="#6c8ebf", edgecolor="white", label="Tickets")
    ax.set(title="Recorded Ticket Time Distribution", xlabel="Elapsed / resolution time (hours)", ylabel="Ticket count")
    ax.legend()
    fig.tight_layout(); fig.savefig(output / "resolution_histogram.png", dpi=180); plt.close(fig)

    weekly = tickets.assign(week=tickets["opened_date"].dt.to_period("W")).groupby("week").size()
    fig, ax = plt.subplots(figsize=(9, 5))
    xlabels = [str(week) for week in weekly.index]
    ax.plot(xlabels, weekly.values, marker="o", linewidth=2, color="#c05a36", label="Tickets opened")
    ax.set(title="Weekly Ticket Volume (Synthetic)", xlabel="Week opened", ylabel="Ticket count")
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    fig.tight_layout(); fig.savefig(output / "weekly_ticket_volume.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for priority, group in tickets.groupby("priority", sort=True):
        ax.scatter(group["priority_code"], group["resolution_hours"], s=56, alpha=.78, label=priority)
    ax.set(title="Priority Code vs Recorded Hours", xlabel="Priority code (1=P1 highest, 4=P4 lowest)", ylabel="Elapsed / resolution time (hours)")
    ax.set_xticks([1, 2, 3, 4], ["P1", "P2", "P3", "P4"])
    ax.legend(title="Priority")
    fig.tight_layout(); fig.savefig(output / "priority_vs_hours.png", dpi=180); plt.close(fig)
    return tickets, rejected, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("tickets.csv"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("output"))
    args = parser.parse_args()
    tickets, rejected, summary = analyze(args.input, args.output)
    print(f"Analyzed {len(tickets)} valid tickets; rejected {rejected} row(s).")
    print(summary.to_string(index=False))
    print(f"Saved reports and charts to {args.output}")


if __name__ == "__main__":
    main()
