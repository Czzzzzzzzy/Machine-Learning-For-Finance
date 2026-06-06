# C2O Close-to-Open Coursework Code

This repository contains the reproducible code pipeline for `C2O_Coursework_Brief.pdf`.

The promoted final strategy is `phase2_g5_05_expanding`: a volatility-scaled overnight-return target with expanding-window transparent feature-weight estimation.

## Final Strategy

The final strategy is a daily, dollar-neutral, close-to-open US large-cap long-short strategy. It keeps the original point-in-time feature set unchanged and trains the walk-forward alpha on:

```text
target = overnight_next / (vol20 / sqrt(252))
```

where `vol20` is trailing 20-day close-to-close volatility shifted by one trading day. For each scored year, expanding-window training uses only data strictly before that year.

The previous 4-year rolling champion is archived under:

```text
outputs/previous_champion_archive_after_phase2/
```

The original baseline outputs remain archived under:

```text
outputs/baseline_archive/
```

## Headline Final Result

Final 250M AUM result over the 2010-2024 development window:

- Net annual return: about `7.31%`
- Net annual volatility: about `4.97%`
- Net Sharpe: about `1.445`
- Max drawdown: about `-10.19%`

The previous champion Sharpe was about `0.811`; it is preserved only as a comparison archive.

## Data Cutoff

The development cutoff is fixed at `2024-12-31`. No 2025+ rows are used in development outputs unless the cutoff is explicitly changed by the user.

## Reproduction Commands

Regenerate all submitted final outputs:

```bash
PYTHON=/opt/anaconda3/bin/python3 make reproduce
```

Run tests:

```bash
PYTHON=/opt/anaconda3/bin/python3 make test
```

Latest recorded result: `13 passed`.

Additional targets:

```bash
PYTHON=/opt/anaconda3/bin/python3 make phase2
PYTHON=/opt/anaconda3/bin/python3 make reproduce-final
PYTHON=/opt/anaconda3/bin/python3 make ablation
PYTHON=/opt/anaconda3/bin/python3 make report-assets
```

## Main Outputs

- `outputs/performance_summary.csv`
- `outputs/daily_returns_50m.csv`
- `outputs/daily_returns_250m.csv`
- `outputs/daily_returns_1b.csv`
- `outputs/positions_50m.parquet`
- `outputs/positions_250m.parquet`
- `outputs/positions_1b.parquet`
- `outputs/quantstats_250m.html`
- `outputs/feature_ablation_summary.csv`
- `outputs/report_ready/phase2_promotion_audit.md`
- `outputs/report_ready/final_strategy_summary.md`
- `outputs/report_ready/final_reproduction_log.md`

## Fixed Assumptions

- Commission: 0.5 bps per leg.
- Auction slippage: 1.5 bps per leg.
- Total non-borrow round-trip cost: 4.0 bps.
- Borrow Tier A/B/C: 40/200/800 bps p.a., charged annual rate / 252 daily.
- Participation cap: 5% ADV20.
- Execution: day-t close entry and day-t+1 open exit.
- Cutoff: 2024-12-31.
