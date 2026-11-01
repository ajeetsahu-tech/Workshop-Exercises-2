# Service Desk Performance — Interpretation

## Data and summary

This report uses **synthetic workshop data only**: 36 valid tickets and 0 rejected malformed row(s). No people or real support operations are represented. Average resolution-time measures below include the recorded elapsed hours for both open and resolved records; for open tickets these are elapsed-to-date values, not completed resolution times.

| Metric | Tickets | Mean hours | Median hours | Maximum hours |
|---|---:|---:|---:|---:|
| Overall | 36 | 10.8 | 8.3 | 31.0 |
| Open | 7 | 24.4 | 24.0 | 31.0 |
| Resolved | 29 | 7.5 | 7.0 | 16.0 |

## What the plots show

- **Tickets by category:** Software has the highest count (12 tickets) in this sample. Counts describe this generated dataset, not expected real-world workload.
- **Resolution-time histogram:** shows the spread and concentration of recorded hours. Open tickets are elapsed-to-date, so their values are not final resolution durations.
- **Weekly ticket volume:** All 9 weeks tie for the highest volume (4 tickets per week). Weekly totals can move because of the small synthetic sample.
- **Priority versus hours:** priority is coded P1=1 (highest) through P4=4 (lowest); the scatter plot displays individual records but does not establish a causal relationship. Each priority band has few examples and category/case complexity is not controlled.


The synthetic open-ticket group has a mean recorded elapsed time of 24.4 hours, compared with 7.5 hours for resolved tickets. This is descriptive only: status groups can differ in age and case mix, so this comparison does not show that status caused a delay.

## Limitations

All rows are simulated, the sample is small, priority uses an ordinal code with equal numeric spacing only for plotting, and no service-level targets or case complexity are included. Do not use these plots to judge staff or make operational claims.
