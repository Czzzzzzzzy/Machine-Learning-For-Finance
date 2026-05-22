# Submission Package README

This package contains the promoted final C2O close-to-open strategy submission.

## Final Strategy

- Experiment id: `phase2_g5_05_expanding`
- Target: `volatility_scaled_overnight_return`
- Target definition: `overnight_next / (vol20 / sqrt(252))`
- Training window: expanding
- Alpha learning: 50% prior / 50% learned
- Basket: top/bottom 3%, equal weight
- Ranking: raw alpha score
- Short treatment: tiered borrow cost only
- Cutoff: 2024-12-31

## Headline 250M Result

- Net annual return: `7.31%`
- Net annual volatility: `4.97%`
- Net Sharpe: `1.445`
- Max drawdown: `-10.19%`

Validation 2019-2022 250M Sharpe is `2.279`. Internal holdout 2023-2024 250M Sharpe is `0.620`. The previous champion Sharpe `0.811` is included only as a preserved comparison.

## Key Files

- `report/final_report.pdf`
- `report/innovation_declaration.md`
- `quantstats/quantstats_250m.html`
- `final_outputs/performance_summary.csv`
- `final_outputs/daily_returns_50m.csv`, `daily_returns_250m.csv`, `daily_returns_1b.csv`
- `final_outputs/positions_50m.parquet`, `positions_250m.parquet`, `positions_1b.parquet`
- `audit_evidence/phase2_promotion_audit.md`
- `audit_evidence/final_reproduction_log.md`
- `audit_evidence/phase2_final_consistency_check.md`
- `baseline_archive/baseline_readme.md`
- `previous_champion_archive_after_phase2/readme.md`

## Reproduction

From the repository root:

```bash
PYTHON=/opt/anaconda3/bin/python3 make reproduce
PYTHON=/opt/anaconda3/bin/python3 make test
```

Latest recorded result: `13 passed`.
