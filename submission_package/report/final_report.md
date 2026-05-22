# Final C2O Strategy Report

## Executive Summary

The promoted final strategy is `phase2_g5_05_expanding`: a daily, dollar-neutral, close-to-open long-short strategy using the volatility-scaled overnight-return target with expanding-window transparent feature-weight estimation. The target is:

```text
target = overnight_next / (vol20 / sqrt(252))
```

`overnight_next` is the next close-to-open return, and `vol20` is a trailing 20-day close-to-close volatility estimate shifted by one trading day. The feature set, basket rule, weighting, raw-score ranking, tiered borrow-cost treatment, transaction costs, 5% ADV20 participation cap, close-to-open execution, and development cutoff remain unchanged from the previous final implementation.

At the main headline AUM of 250M, the promoted final strategy earns `7.31%` net annual return, `4.97%` net volatility, net Sharpe `1.445`, and maximum drawdown `-10.19%` over 2010-2024. The previous 4-year rolling champion had 250M net Sharpe `0.811`; that value is now only a comparison point, not the final strategy.

The controlled Phase 2 screen supports promotion: validation 2019-2022 250M Sharpe improves to `2.279`, internal holdout 2023-2024 remains positive at `0.620`, and full 2010-2024 Sharpe is `1.445`. The holdout result is much lower than validation, so the report treats this as controlled evidence of improvement, not a promise of live performance.

2025-2026 remains held out for marker evaluation. No 2025+ data is used in development outputs.

## Final Strategy Configuration

- Target: `volatility_scaled_overnight_return`.
- Target definition: `overnight_next / (vol20 / sqrt(252))`.
- Training window: expanding. For each scored year Y, training starts at 2010-01-01 and ends before year Y begins.
- Alpha learning: 50% prior / 50% learned transparent correlation weights.
- Basket: top/bottom 3% of eligible names, with minimum 15 names per side.
- Weighting: equal weight within each side, subject to capacity caps.
- Ranking: raw alpha score.
- Short treatment: tiered borrow cost only; no hard short exclusion.
- Execution: enter at day-t closing auction and exit at day-t+1 opening auction.
- Development cutoff: 2024-12-31.

Volatility scaling makes the training label risk-adjusted. Expanding-window training uses more historical overnight evidence as time progresses, which can stabilise transparent feature-weight estimation relative to a fixed 4-year rolling window. The performance improvement is not from cost relaxation, borrow relaxation, participation-cap relaxation, execution-timing changes, external data, intraday data, or new features.

## Headline Performance

| AUM   | Net annual return   | Net vol   |   Net Sharpe | Max drawdown   |   Gross Sharpe | Avg gross exposure   |   Cap-binding days |
|:------|:--------------------|:----------|-------------:|:---------------|---------------:|:---------------------|-------------------:|
| 50M   | 6.66%               | 5.03%     |        1.308 | -13.82%        |          3.539 | 99.92%               |               3547 |
| 250M  | 7.31%               | 4.97%     |        1.445 | -10.19%        |          3.112 | 74.97%               |               3773 |
| 1B    | 3.50%               | 2.69%     |        1.293 | -5.56%         |          2.321 | 25.35%               |               3773 |

250M is the main headline AUM because it balances realised gross exposure, capacity use, and cost drag. 1B is included as a capacity boundary case.

## Champion-Challenger Evidence

| Metric                                     | Previous champion   | Promoted final   |
|:-------------------------------------------|:--------------------|:-----------------|
| Validation 2019-2022 250M net Sharpe       | 1.107               | 2.279            |
| Internal holdout 2023-2024 250M net Sharpe | 0.003               | 0.620            |
| Full 2010-2024 250M net Sharpe             | 0.811               | 1.445            |
| Full 2010-2024 max drawdown                | -10.19%             | -10.19%          |
| Full 2010-2024 worst 12m return            | -10.09%             | -10.09%          |

The selected challenger passes the promotion audit. It improves validation Sharpe, remains positive in 2023-2024 internal holdout, improves full-period Sharpe, and does not worsen full-period maximum drawdown. The previous 0.811 Sharpe strategy is archived under `outputs/previous_champion_archive_after_phase2/` and `outputs/current_champion_archive/`.

The 2023-2024 holdout Sharpe of `0.620` is materially lower than the validation Sharpe of `2.279`. This degradation is expected in a controlled screen and should be disclosed plainly.

## Costs And Execution

The cost model is unchanged:

- Commission: 0.5 bps per leg.
- Auction slippage: 1.5 bps per leg.
- Total non-borrow round-trip cost: 4.0 bps.
- Borrow Tier A: 40 bps p.a.
- Borrow Tier B: 200 bps p.a.
- Borrow Tier C: 800 bps p.a.
- Borrow daily charge: annual rate / 252.
- Participation cap: 5% ADV20.

Sharpe drag values below are Sharpe-unit drags, not percentages.

| AUM   |   Gross Sharpe |   Commission drag |   Slippage drag |   Borrow drag |   Net Sharpe |   Avg daily borrow bps |
|:------|---------------:|------------------:|----------------:|--------------:|-------------:|-----------------------:|
| 50M   |          3.539 |             0.501 |           1.503 |         0.227 |        1.308 |                  0.451 |
| 250M  |          3.112 |             0.378 |           1.137 |         0.152 |        1.445 |                  0.301 |
| 1B    |          2.321 |             0.233 |           0.704 |         0.091 |        1.293 |                  0.098 |

At 250M, gross Sharpe is `3.112` and net Sharpe is `1.445` after commission, auction slippage, and borrow costs. Auction slippage remains the largest explicit cost drag.

## Capacity

| AUM   | Avg gross exposure   |   Cap-binding days | Fraction cap-binding days   | Avg participation   | Position days at cap   |
|:------|:---------------------|-------------------:|:----------------------------|:--------------------|:-----------------------|
| 50M   | 99.92%               |               3547 | 93.99%                      | 2.04%               | 16.16%                 |
| 250M  | 74.97%               |               3773 | 99.97%                      | 4.02%               | 66.29%                 |
| 1B    | 25.35%               |               3773 | 99.97%                      | 4.29%               | 75.40%                 |

At 250M, average gross exposure used is `74.97%`. At 1B it falls to `25.35%`, which means the strategy cannot always deploy target risk under the fixed 5% ADV20 cap. This is an honest capacity result rather than an implementation error.

## Borrow Treatment

The strategy uses provided point-in-time short-interest proxies plus a one-trading-day decision lag to assign borrow tiers. Borrow affects net returns through the explicit daily charge; it does not change the raw short selection in the promoted final strategy.

| Tier | Annual rate | Daily charge |
|---|---:|---:|
| A | 40 bps p.a. | annual rate / 252 |
| B | 200 bps p.a. | annual rate / 252 |
| C | 800 bps p.a. | annual rate / 252 |

The report does not claim independent prime-broker borrow-fee validation. No direct securities-lending or locate-rate data is used.

## Feature Ablation Interpretation

| Variant                             | Removed group                |   IC mean |   IC t-stat | Net annual return   | Net vol   |   Net Sharpe | Max drawdown   |
|:------------------------------------|:-----------------------------|----------:|------------:|:--------------------|:----------|-------------:|:---------------|
| full_model                          | none                         |     0.029 |       9.934 | 7.31%               | 4.97%     |        1.445 | -10.19%        |
| remove_return/reversal              | return/reversal              |     0.011 |       3.333 | -3.62%              | 3.26%     |       -1.114 | -46.66%        |
| remove_risk/liquidity/size          | risk/liquidity/size          |     0.028 |      10.863 | 5.89%               | 5.12%     |        1.144 | -8.24%         |
| remove_fundamental/value/quality    | fundamental/value/quality    |     0.03  |      10.203 | 7.01%               | 4.90%     |        1.407 | -9.75%         |
| remove_earnings/revision            | earnings/revision            |     0.028 |       9.754 | 7.31%               | 4.86%     |        1.477 | -10.19%        |
| remove_short-interest/borrow-stress | short-interest/borrow-stress |     0.029 |       9.846 | 7.70%               | 5.00%     |        1.508 | -11.32%        |
| remove_industry-return              | industry-return              |     0.029 |       9.942 | 7.27%               | 4.96%     |        1.442 | -10.19%        |

The ablation is a dependence audit, not a retuning exercise. Return/reversal is the clearest alpha contributor: removing it lowers 250M Sharpe from `1.445` to `-1.114`. Some other removals improve Sharpe, especially short-interest/borrow-stress and earnings/revision in this frozen no-retuning table. That should not be hidden. It means some variables may be acting as risk, capacity, crowding, turnover, or cost-control information rather than standalone alpha predictors.

## Robustness

### Year-By-Year 250M Results

|   Year | Return   | Vol   |   Sharpe | Max drawdown   | Avg gross exposure   |
|-------:|:---------|:------|---------:|:---------------|:---------------------|
|   2010 | -10.09%  | 3.42% |   -3.094 | -10.19%        | 42.46%               |
|   2011 | 21.39%   | 5.63% |    3.474 | -2.08%         | 67.54%               |
|   2012 | 6.70%    | 2.80% |    2.333 | -1.68%         | 56.93%               |
|   2013 | 5.61%    | 2.38% |    2.307 | -1.17%         | 64.02%               |
|   2014 | 2.57%    | 3.66% |    0.712 | -5.01%         | 80.35%               |
|   2015 | 3.91%    | 2.46% |    1.575 | -1.06%         | 64.59%               |
|   2016 | 3.30%    | 2.33% |    1.41  | -1.53%         | 47.44%               |
|   2017 | 1.64%    | 2.05% |    0.804 | -1.35%         | 61.08%               |
|   2018 | 3.08%    | 3.84% |    0.808 | -3.38%         | 81.30%               |
|   2019 | 12.30%   | 3.64% |    3.206 | -1.03%         | 80.89%               |
|   2020 | 15.53%   | 9.57% |    1.557 | -4.78%         | 88.45%               |
|   2021 | 10.83%   | 5.96% |    1.755 | -5.47%         | 96.18%               |
|   2022 | 32.24%   | 8.02% |    3.525 | -2.63%         | 99.23%               |
|   2023 | 9.70%    | 5.32% |    1.768 | -4.85%         | 96.07%               |
|   2024 | -2.61%   | 5.73% |   -0.434 | -5.09%         | 98.07%               |

### Pre/Post Split

|   Subperiod | Return   | Vol   |   Sharpe | Max drawdown   | Avg gross exposure   |
|------------:|:---------|:------|---------:|:---------------|:---------------------|
|   2010_2016 | 4.42%    | 3.45% |    1.273 | -10.19%        | 60.48%               |
|   2017_2024 | 9.90%    | 5.99% |    1.608 | -7.64%         | 87.66%               |

### Stress Windows

| Window        | Return   | Vol    |   Sharpe | Max drawdown   | Avg gross exposure   |
|:--------------|:---------|:-------|---------:|:---------------|:---------------------|
| late_2018     | -2.35%   | 4.71%  |   -0.482 | -1.92%         | 85.28%               |
| 2020_q1       | 34.41%   | 10.78% |    2.799 | -4.14%         | 88.95%               |
| 2022_drawdown | 32.24%   | 8.02%  |    3.525 | -2.63%         | 99.23%               |

### Tail And Serial Correlation

At 250M, worst 3-month return is `-4.46%`, worst 6-month return is `-7.31%`, and worst 12-month return is `-10.09%`. The top 5% best days contribute `1.461` times total PnL, which means daily PnL is meaningfully concentrated. Lag-1 return autocorrelation is `-0.007`, so there is no large positive serial-correlation effect inflating annualised Sharpe in the final output.

## Point-In-Time Controls

The promotion audit passes the following controls:

- No 2025+ data is used; promoted cache max date is `2024-12-31`.
- The target uses the future overnight return only as a historical training label.
- `vol20` is trailing and shifted before use in the target denominator.
- For each scored year, expanding-window training uses only dates strictly before that year.
- Cross-sectional ranks use only the same-day available cross-section.
- Earnings filtering uses `strat_trading_date` and respects AMC/BMO timing.
- Short-interest fields use provided point-in-time proxies from the coursework data package plus a one-trading-day decision lag.
- No day-t close/high/low enters a decision-time feature unless shifted appropriately.

## Baseline And Previous Champion

The original baseline is preserved in `outputs/baseline_archive/`. Its original 250M net Sharpe was approximately `0.374`; the logged experiment baseline was approximately `0.379`. The previous 4-year rolling champion is preserved in `outputs/previous_champion_archive_after_phase2/` with 250M Sharpe `0.811`.

The promoted final strategy should be compared against those archives without relabelling them as final.

## Reproduction

The final outputs are regenerated with:

```bash
PYTHON=/opt/anaconda3/bin/python3 make reproduce
PYTHON=/opt/anaconda3/bin/python3 make test
```

The latest test run passed with `13 passed`. The submitted package includes final daily returns, positions for 50M/250M/1B, QuantStats HTML, report-ready audit evidence, and archive notes.

## Limitations

The main limitations are straightforward: no external prime-broker borrow validation, no independent raw FINRA short-interest publication-date reconstruction, no separate market-impact model beyond the fixed brief cost schedule and realised participation reporting, and visible capacity constraints at 1B. The 2025-2026 period remains held out for marker evaluation.

## Final Decision

Promotion passed. The final strategy is the volatility-scaled overnight-return target with expanding-window weight estimation: `phase2_g5_05_expanding`. The previous 0.811 champion remains preserved for audit comparison, while the live final headline is the promoted 250M result: `7.31%` net annual return, `4.97%` net volatility, Sharpe `1.445`, and max drawdown `-10.19%`.
