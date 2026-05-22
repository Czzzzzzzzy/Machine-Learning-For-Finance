# Current Champion Archive

This archive preserves the current champion strategy before any Phase 2
champion-challenger experiments.

## Preserved Champion

- Strategy: `volatility_scaled_overnight_return`
- Target definition: `overnight_next / (vol20 / sqrt(252))`
- `vol20`: trailing 20-day close-to-close volatility shifted by one trading day
- Feature set: unchanged from the baseline feature set
- Development cutoff: `2024-12-31`

## 250M Headline Metrics

- Net annual return: `3.93%`
- Net volatility: `4.90%`
- Net Sharpe: `0.811`
- Max drawdown: `-10.19%`

## Reproduction Status

- `make reproduce` previously passed according to the preserved final
  reproduction log.
- `make test` previously passed according to the preserved final reproduction
  log.
- This version is preserved before Phase 2. The current champion remains the
  final strategy unless the user explicitly approves a replacement.
