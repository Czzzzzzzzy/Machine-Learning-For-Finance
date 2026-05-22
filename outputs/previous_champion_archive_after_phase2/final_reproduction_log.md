# Final Reproduction Log

## Environment

- Python executable: `/opt/anaconda3/bin/python3`
- Python version: `3.13.5`
- Platform: `macOS-26.4.1-arm64-arm-64bit-Mach-O`
- Package freeze: `outputs/report_ready/pip_freeze.txt`

## Commands

- `make reproduce`: passed on 2026-05-15 via PYTHON=/opt/anaconda3/bin/python3 make reproduce; final outputs refreshed afterward with make reproduce-final after position cap-flag clarification
- `make test`: passed on 2026-05-22 via PYTHON=/opt/anaconda3/bin/python3 make test
- Tests passed: 13 passed

## Final 250M Result

- Net Sharpe: `0.811479`
- Net annual return: `0.039314`
- Net volatility: `0.049002`
- Max drawdown: `-0.101865`

## Cutoff Confirmation

- Final cached volatility-scaled panel max date: `2024-12-31`
- Development cutoff: `2024-12-31`
- No 2025+ development data used: `True`

## Baseline Archive

- Baseline outputs archived before final regeneration: `True`
