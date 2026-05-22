# Numerical Consistency Audit

Audit date: 2026-05-22.

Files checked:

- `report/final_report.md`
- `report/final_report.tex`
- `outputs/performance_summary.csv`
- `outputs/report_ready/final_strategy_summary.md`
- `outputs/report_ready/final_strategy_selection_memo.md`
- `outputs/report_ready/final_reproduction_log.md`
- `submission_package/` files after package regeneration

## Final 250M Headline

| Metric | Source value | Report label | Status |
|---|---:|---:|---|
| Net annual return | `0.0730994973` | `7.31%` | OK |
| Net volatility | `0.0496733221` | `4.97%` | OK |
| Net Sharpe | `1.4453177677` | `1.445` | OK |
| Max drawdown | `-0.1018648300` | `-10.19%` | OK |

The old `0.811` Sharpe is now labelled only as the previous 4-year rolling champion. It is not the final promoted strategy. The new final `1.445` Sharpe is labelled as the promoted expanding-window strategy.

## Baseline Labels

- Original baseline Sharpe around `0.374` remains labelled as the original baseline from `outputs/baseline_archive/performance_summary.csv`.
- Logged experiment baseline Sharpe around `0.379` remains labelled as the logged experiment baseline from `outputs/strategy_experiment_summary.csv`.

## Formatting Checks

- Cost drag values are presented as Sharpe drag units, not percentages: commission `0.378`, slippage `1.137`, borrow `0.152` at 250M.
- AUM labels are standardised as `50M`, `250M`, and `1B`.
- No current report-ready file claims that 50M or 1B position files are missing.
- Final cache max date is checked separately in `outputs/report_ready/phase2_final_consistency_check.md`.
