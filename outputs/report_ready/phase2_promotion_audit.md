# Phase 2 Promotion Audit

Promotion candidate: `phase2_g5_05_expanding`.

Audit result: `PASS`.

## 1. Expanding-Window Training Definition

In code, `expanding` means that for a scored calendar year `Y`, the training
sample starts at the configured strategy start date, `2010-01-01`, and ends at
`Y-01-01 - 1 calendar day`. The scored year itself is never included in the
training sample.

Implementation reference: `src/c2o_strategy/phase2.py`,
`training_start_for_window()`, `score_panel_phase2()`, and
`add_walk_forward_alpha_return_phase2()`.

Checks:

- For each scored year `Y`, training uses only rows with dates strictly before
  year `Y`.
- The year being scored is not part of that year's training sample.
- Future years are not included in training.
- Phase 2 scored caches max out at `2024-12-31`.
- No 2025+ data is used.
- Feature weights are deterministic: the correlation learner has no random
  sampling, no stochastic optimizer, and no external data dependency.

## 2. Point-In-Time Validity

Checks:

- The volatility-scaled target uses `overnight_next` only as a historical
  training label.
- The denominator `vol20 / sqrt(252)` remains a trailing 20-day close-to-close
  volatility estimate shifted by one trading day.
- The feature set remains unchanged from the previous final strategy and is
  observable by 15:50 ET on day `t`.
- Earnings timing still uses `earnings_calendar.strat_trading_date` and the
  existing AMC/BMO-aware exclusion window.
- Short-interest fields still use the provided point-in-time proxies from
  `all_data.parquet`, then apply an additional one-trading-day decision lag
  before feature use or borrow-tier assignment.
- Cross-sectional ranks are computed within the same decision-date
  cross-section and do not use future dates.
- No day-`t` close/high/low enters a decision-time feature unless shifted
  appropriately. Close-to-close returns, volatility, ADV20, and Amihud-style
  liquidity features use lagged/rolling shifted inputs.

Result: `PASS`.

## 3. Cost And Execution Invariance

The promotion does not change implementation assumptions:

| Assumption | Promoted setting | Status |
|---|---:|---|
| Commission | 0.5 bps per leg | unchanged |
| Auction slippage | 1.5 bps per leg | unchanged |
| Total non-borrow round-trip cost | 4.0 bps | unchanged |
| Borrow Tier A | 40 bps p.a. | unchanged |
| Borrow Tier B | 200 bps p.a. | unchanged |
| Borrow Tier C | 800 bps p.a. | unchanged |
| Borrow daily charge | annual rate / 252 | unchanged |
| Participation cap | 5% ADV20 | unchanged |
| Execution | enter day-`t` close, exit day-`t+1` open | unchanged |

Result: `PASS`.

## 4. Selection Discipline

`phase2_g5_05_expanding` is selected because it passes the pre-specified
champion-challenger screen:

- Validation 2019-2022 250M net Sharpe improves from previous champion `1.107`
  to `2.279`.
- Internal holdout 2023-2024 250M net Sharpe remains positive at `0.620`,
  versus previous champion `0.003`.
- Full 2010-2024 250M net Sharpe improves from `0.811` to `1.445`.
- Full max drawdown remains about `-10.19%`, not worse than the previous
  champion.
- Average gross exposure used rises from `70.43%` to `74.97%`; the improvement
  is not a low-exposure artifact.
- The cost schedule, borrow rates, participation cap, execution timing, target,
  feature set, basket rule, weighting, ranking, and short-leg treatment are
  unchanged.
- IC is stable/slightly stronger: full-sample 250M IC mean rises from `0.0282`
  to about `0.0289`, and IC t-stat rises from `9.465` to about `9.934`.

Economic explanation: the volatility-scaled label asks the same transparent
feature set to predict risk-adjusted overnight opportunities, while expanding
window estimation uses more accumulated overnight evidence as the sample grows.
That can stabilise feature-weight estimates versus a fixed 4-year rolling
window without relaxing implementation frictions or adding new data.

Result: `PASS`.

## 5. Caution

The internal holdout result is positive but clearly lower than the validation
result: 2023-2024 250M net Sharpe is `0.620`, versus `2.279` in validation
2019-2022. This degradation should be disclosed as expected out-of-period
weakening and should not be hidden or oversold.

Promotion may proceed, but the report should describe the new strategy as a
controlled improvement over the previous champion, not as a guarantee of live
performance.
