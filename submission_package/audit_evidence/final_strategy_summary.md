# Final Strategy Summary

Final strategy: volatility-scaled overnight-return target with expanding-window
weight estimation.

At 250M AUM, the final strategy reports:

- Net annual return: `7.31%`
- Net volatility: `4.97%`
- Net Sharpe: `1.445`
- Max drawdown: `-10.19%`
- Average gross exposure used: `74.97%`

Phase 2 selection diagnostics:

- Validation 2019-2022 250M net Sharpe: about `2.279`
- Internal holdout 2023-2024 250M net Sharpe: about `0.620`
- Previous 4-year rolling champion 250M net Sharpe: about `0.811`

Main outputs:

- `outputs/performance_summary.csv`
- `outputs/daily_returns_50m.csv`
- `outputs/daily_returns_250m.csv`
- `outputs/daily_returns_1b.csv`
- `outputs/positions_50m.parquet`
- `outputs/positions_250m.parquet`
- `outputs/positions_1b.parquet`
- `outputs/quantstats_250m.html`

Baseline evidence is preserved under `outputs/baseline_archive/`.
