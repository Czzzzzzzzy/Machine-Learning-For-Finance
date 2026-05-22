# Innovation Declaration

The final submitted strategy is `phase2_g5_05_expanding`: a volatility-scaled close-to-open target with expanding-window transparent feature-weight estimation.

## What Changed Versus Baseline

The original baseline predicted raw next overnight returns using the provided point-in-time feature set. The final strategy keeps that feature set unchanged but trains on a risk-adjusted label:

```text
overnight_next / (vol20 / sqrt(252))
```

where `vol20` is trailing 20-day close-to-close volatility shifted by one trading day. The promoted Phase 2 improvement changes the training window from the previous 4-year rolling champion to an expanding window. For each scored year, the model uses only earlier years and never includes the year being scored.

## Why This Is An Innovation

The change is transparent and economically motivated. Volatility scaling reduces the influence of noisy high-volatility overnight labels. Expanding-window estimation uses more accumulated overnight evidence as time progresses, which stabilises the simple feature-weight learner without adding opaque modelling complexity.

## What Did Not Change

The promotion did not use external data, intraday data, 2025+ data, new feature families, lower transaction costs, lower borrow costs, a relaxed participation cap, or different execution timing. Commission, auction slippage, Tier A/B/C borrow costs, the 5% ADV20 cap, and close-to-open execution all remain fixed.

## Evidence

At 250M, validation 2019-2022 net Sharpe is `2.279`, internal holdout 2023-2024 net Sharpe is `0.620`, and full 2010-2024 net Sharpe is `1.445`. The holdout result is lower than validation, so the result is presented as a controlled improvement rather than an overfit-free guarantee.
