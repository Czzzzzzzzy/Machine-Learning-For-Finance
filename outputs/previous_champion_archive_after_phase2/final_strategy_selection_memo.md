# Final Strategy Selection Memo

Generated from existing logged experiment outputs and cached scored experiment
panels. No additional experiment variants were run, no parameters were tuned,
no baseline outputs were overwritten before archiving, and all cached panels are
capped at `2024-12-31`.

## Decision

**Promote `E_target_transform / volatility_scaled_overnight_return` as the
final strategy.**

The candidate passes the point-in-time audit and improves 250M net Sharpe,
drawdown, worst rolling 12-month return, IC, and average capacity usage while
preserving the same point-in-time feature set and the same Section 6.3 cost
schedule.

## 1. 250M Net Sharpe Improvement

Baseline 250M net Sharpe is `0.379` with annual return
`1.69%`. The final candidate has 250M net Sharpe
`0.811` with annual return
`3.93%`.

## 2. Drawdown

Max drawdown improves from `-24.58%` to
`-10.19%`. Worst rolling 12-month return improves from
`-12.98%` to `-10.09%`.

## 3. IC Versus Volatility

IC mean improves from `0.027` to
`0.028` and IC t-stat from `8.363` to
`9.465`. Net volatility is slightly higher, not lower, so
the Sharpe improvement is not merely a low-volatility denominator effect.

## 4. Costs, Turnover, and Capacity

Turnover and cost drag rise under the final candidate, so the improvement does
not come from cheaper trading. The candidate improves average gross exposure
used from `57.89%` to
`70.43%` at 250M, indicating better
capacity usage under the same 5% ADV20 cap.

## 5. AUM Credibility

- 50M Sharpe improves from `0.280` to `0.850`.
- 250M Sharpe improves from `0.379` to `0.811`.
- 1B Sharpe improves from `-0.070` to `0.266`.

The 1B version remains capacity-constrained, but it is no longer negative in
the logged development-window comparison.

## 6. Year-by-year Stability

At 250M, baseline positive annual-return years:
`10/15`. Final
candidate positive annual-return years:
`11/15`.

Worst baseline year is `2024` at
`-10.96%`. Worst final-candidate year is
`2010` at `-10.09%`.

## 7. Stress Windows

| strategy_name                        |              AUM | window        | start      | end        |   net_return |   annual_sharpe |   max_drawdown |   average_gross_exposure_used |   average_turnover |   n_days |
|:-------------------------------------|-----------------:|:--------------|:-----------|:-----------|-------------:|----------------:|---------------:|------------------------------:|-------------------:|---------:|
| baseline_rank_target_top_bottom_3pct | 250000000.000000 | covid_q1_2020 | 2020-01-01 | 2020-03-31 |    -0.024528 |       -0.743456 |      -0.067739 |                      0.549945 |           1.099891 |       62 |
| candidate_volatility_scaled_target   | 250000000.000000 | covid_q1_2020 | 2020-01-01 | 2020-03-31 |     0.022408 |        1.020440 |      -0.030515 |                      0.879664 |           1.759328 |       62 |
| baseline_rank_target_top_bottom_3pct | 250000000.000000 | drawdown_2022 | 2022-01-01 | 2022-12-31 |    -0.071592 |       -0.788106 |      -0.133588 |                      0.936386 |           1.872771 |      251 |
| candidate_volatility_scaled_target   | 250000000.000000 | drawdown_2022 | 2022-01-01 | 2022-12-31 |     0.280878 |        3.111259 |      -0.028597 |                      0.954632 |           1.909264 |      251 |
| baseline_rank_target_top_bottom_3pct | 250000000.000000 | late_2018     | 2018-10-01 | 2018-12-31 |    -0.009470 |       -2.093024 |      -0.010792 |                      0.308901 |           0.617802 |       63 |
| candidate_volatility_scaled_target   | 250000000.000000 | late_2018     | 2018-10-01 | 2018-12-31 |     0.001694 |        0.234512 |      -0.013002 |                      0.679473 |           1.358946 |       63 |

## 8. Economic Explanation

The target asks the same features to predict a risk-adjusted next overnight
move. High-volatility event names no longer dominate the training label simply
because their raw overnight returns are large. This is economically coherent
for a daily, capacity-constrained, costed overnight strategy.

## 9. Look-ahead Safety

The denominator `vol20 / sqrt(252)` is trailing and shifted by one trading day.
The future overnight return is used only as a historical training label under a
walk-forward training protocol. Cached panels end at `2024-12-31`, and no 2025+
development data is used.
