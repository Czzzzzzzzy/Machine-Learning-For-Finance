# Final Strategy Selection Memo

Generated from the Phase 2 champion-challenger matrix and the promoted final
outputs. No additional variants were run during promotion, no parameters were
tuned, and all cached panels are capped at `2024-12-31`.

## Decision

**Promote `phase2_g5_05_expanding` as the final strategy.**

The final strategy uses the volatility-scaled overnight-return target with
expanding-window transparent feature-weight estimation. It preserves the same
feature set, top/bottom 3% basket, equal weighting, raw-score ranking, tiered
borrow-cost-only short treatment, Section 6.3 cost schedule, 5% ADV20 cap, and
close-to-open execution.

## 1. 250M Net Sharpe Improvement Versus Previous Champion

Previous champion 250M net Sharpe was `0.811` with
annual return `3.93%`. The promoted expanding
window final has 250M net Sharpe `1.445` with annual return
`7.31%`.

Validation 2019-2022 250M net Sharpe is `2.279`. Internal holdout
2023-2024 250M net Sharpe is `0.620`. The holdout result remains
positive but is materially lower than validation, so the improvement should not
be overclaimed.

## 2. Drawdown And Worst 12 Months

Max drawdown is `-10.19%` versus previous champion
`-10.19%`. Worst rolling 12-month return is
`-10.09%` versus previous champion
`-10.09%`.

## 3. IC Versus Volatility

IC mean changes from `0.028` to
`0.029`, and IC t-stat changes from
`9.465` to `9.934`. The promoted
strategy improves performance without adding features or lowering realized
costs.

## 4. Costs, Turnover, and Capacity

Turnover and cost drag remain explicitly charged. Average 250M turnover is
`1.499` and average gross exposure used is
`74.97%`, versus previous champion
turnover `1.409` and gross exposure
`70.43%`. The improvement is not caused
by relaxed costs, relaxed borrow, relaxed participation caps, or a change in
execution timing.

## 5. AUM Credibility

- 50M Sharpe changes from `0.850` to `1.308`.
- 250M Sharpe changes from `0.811` to `1.445`.
- 1B Sharpe changes from `0.266` to `1.293`.

250M remains the main headline AUM. The 1B result is improved but should still
be interpreted through the realized gross exposure and cap-binding evidence.

## 6. Year-by-year Stability

At 250M, previous champion positive annual-return years:
`11/15`. Promoted
final positive annual-return years:
`13/15`.

Worst previous-champion year is `2010` at
`-10.09%`. Worst promoted-final year is
`2010` at `-10.09%`.

## 7. Stress Windows

| strategy_name                |              AUM | window        | start      | end        |   net_return |   annual_sharpe |   max_drawdown |   average_gross_exposure_used |   average_turnover |   n_days |
|:-----------------------------|-----------------:|:--------------|:-----------|:-----------|-------------:|----------------:|---------------:|------------------------------:|-------------------:|---------:|
| final_expanding_window       | 250000000.000000 | covid_q1_2020 | 2020-01-01 | 2020-03-31 |     0.075478 |        2.798751 |      -0.041378 |                      0.889505 |           1.779010 |       62 |
| previous_champion_4y_rolling | 250000000.000000 | covid_q1_2020 | 2020-01-01 | 2020-03-31 |     0.022408 |        1.020440 |      -0.030515 |                      0.879664 |           1.759328 |       62 |
| final_expanding_window       | 250000000.000000 | drawdown_2022 | 2022-01-01 | 2022-12-31 |     0.320946 |        3.524723 |      -0.026347 |                      0.992267 |           1.984534 |      251 |
| previous_champion_4y_rolling | 250000000.000000 | drawdown_2022 | 2022-01-01 | 2022-12-31 |     0.280878 |        3.111259 |      -0.028597 |                      0.954632 |           1.909264 |      251 |
| final_expanding_window       | 250000000.000000 | late_2018     | 2018-10-01 | 2018-12-31 |    -0.005931 |       -0.482211 |      -0.019200 |                      0.852784 |           1.705568 |       63 |
| previous_champion_4y_rolling | 250000000.000000 | late_2018     | 2018-10-01 | 2018-12-31 |     0.001694 |        0.234512 |      -0.013002 |                      0.679473 |           1.358946 |       63 |

## 8. Economic Explanation

The target asks the same features to predict a risk-adjusted next overnight
move. High-volatility event names no longer dominate the training label simply
because their raw overnight returns are large. Expanding-window training then
uses more accumulated historical overnight evidence as time progresses, which
can stabilise transparent feature-weight estimation relative to a fixed 4-year
window.

## 9. Look-ahead Safety

The denominator `vol20 / sqrt(252)` is trailing and shifted by one trading day.
For each scored year, expanding-window training uses only dates strictly before
that year. The future overnight return is used only as a historical training
label under the walk-forward protocol. Cached panels end at `2024-12-31`, and no
2025+ development data is used.
