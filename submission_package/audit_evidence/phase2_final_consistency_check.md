# Phase 2 Final Consistency Check

Audit date: 2026-05-22.

| Check | Status | Evidence |
|---|---:|---|
| final_report.pdf exists and renders | PASS | 5 pages |
| QuantStats HTML exists and is not fallback | PASS | outputs/quantstats_250m.html |
| New final 250M metrics match performance_summary.csv | PASS | Sharpe 1.445318 |
| Old 0.811 champion is not mislabeled as final | PASS | OK |
| New 1.445 challenger is not mislabeled as previous champion | PASS | OK |
| Cost drag values are not formatted as percentages | PASS | Report labels Sharpe drag units |
| AUM labels are consistent: 50M, 250M, 1B | PASS | OK |
| No stale claim remains saying 50M/1B positions are missing | PASS | OK |
| No unresolved placeholders remain in active docs | PASS | OK |
| All report numbers trace to output files | PASS | performance_summary.csv |
| Final cached panels max out at 2024-12-31 | PASS | 2024-12-31 |
| Cost, borrow, cap, and execution assumptions are unchanged | PASS | commission 0.0001 RT, slippage 0.0003 RT, cap 0.05 |

## Final Headline

- Final strategy: `phase2_g5_05_expanding`
- 250M net annual return: `7.31%`
- 250M net volatility: `4.97%`
- 250M net Sharpe: `1.445`
- 250M max drawdown: `-10.19%`
- Validation 2019-2022 250M net Sharpe: `2.279`
- Internal holdout 2023-2024 250M net Sharpe: `0.620`

All checks passed.
