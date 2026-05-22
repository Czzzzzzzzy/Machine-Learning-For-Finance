# Final Reproduction Log

## Environment

- Python executable: `/opt/anaconda3/bin/python3`
- Python version: `3.13.5`
- Platform: `macOS-26.5-arm64-arm-64bit-Mach-O`
- Package freeze: `outputs/report_ready/pip_freeze.txt`

## Commands

- `make reproduce`: passed on 2026-05-22 via `PYTHON=/opt/anaconda3/bin/python3 make reproduce`
- `make test`: passed on 2026-05-22 via `PYTHON=/opt/anaconda3/bin/python3 make test`
- Tests passed: `13 passed`

## Final 250M Result

- Net Sharpe: `1.445318`
- Net annual return: `0.073099`
- Net volatility: `0.049673`
- Max drawdown: `-0.101865`
- Final strategy: `phase2_g5_05_expanding`
- Training window: `expanding`

## Validation And Holdout

- Validation 2019-2022 250M net Sharpe: `2.278993`
- Internal holdout 2023-2024 250M net Sharpe: `0.620163`

## Cutoff Confirmation

- Final cached expanding-window panel max date: `2024-12-31`
- Development cutoff: `2024-12-31`
- No 2025+ development data used: `True`

## Archive Confirmation

- Baseline archive exists: `True`
- Current champion archive exists: `True`
- Previous champion archive after Phase 2 exists: `True`

## Assumption Confirmation

- Commission, auction slippage, borrow Tier A/B/C, 5% ADV20 participation cap, and close-to-open execution assumptions are unchanged.
- Final strategy outputs were overwritten only after promotion audit passed and user approval was provided.
