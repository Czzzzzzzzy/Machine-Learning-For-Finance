# Final Strategy Feature Ablation Audit

Feature-group ablation was run for the final volatility-scaled target strategy
with expanding-window weight estimation. Basket rules, weighting, costs,
borrow treatment, participation cap, and the development cutoff are unchanged.

Full output: `outputs/feature_ablation_summary.csv`.

## 250M Summary

| model_variant                       | removed_group                |              AUM |   IC_mean |   IC_tstat |   net_annual_return |   net_vol |   net_sharpe |   max_drawdown |   avg_turnover |   avg_gross_exposure_used |
|:------------------------------------|:-----------------------------|-----------------:|----------:|-----------:|--------------------:|----------:|-------------:|---------------:|---------------:|--------------------------:|
| full_model                          | none                         | 250000000.000000 |  0.028940 |   9.934090 |            0.073099 |  0.049673 |     1.445318 |      -0.101865 |       1.499426 |                  0.749713 |
| remove_return/reversal              | return/reversal              | 250000000.000000 |  0.011262 |   3.332858 |           -0.036228 |  0.032647 |    -1.113876 |      -0.466622 |       0.953596 |                  0.476798 |
| remove_risk/liquidity/size          | risk/liquidity/size          | 250000000.000000 |  0.027814 |  10.863295 |            0.058921 |  0.051223 |     1.143509 |      -0.082442 |       1.612358 |                  0.806179 |
| remove_fundamental/value/quality    | fundamental/value/quality    | 250000000.000000 |  0.029606 |  10.203432 |            0.070140 |  0.049025 |     1.407451 |      -0.097542 |       1.490900 |                  0.745450 |
| remove_earnings/revision            | earnings/revision            | 250000000.000000 |  0.028372 |   9.753544 |            0.073096 |  0.048579 |     1.476684 |      -0.101865 |       1.497669 |                  0.748835 |
| remove_short-interest/borrow-stress | short-interest/borrow-stress | 250000000.000000 |  0.028908 |   9.846413 |            0.076977 |  0.050010 |     1.508078 |      -0.113176 |       1.566479 |                  0.783239 |
| remove_industry-return              | industry-return              | 250000000.000000 |  0.028955 |   9.942310 |            0.072742 |  0.049557 |     1.441862 |      -0.101865 |       1.498674 |                  0.749337 |

## Interpretation

The full model row now corresponds to the promoted expanding-window final
strategy. Removing return/reversal remains the clearest test of the core
overnight alpha. If other removals improve Sharpe, that should be disclosed
rather than hidden: those groups may be acting as risk, capacity, crowding, or
cost-control inputs rather than pure alpha contributors.

## Feature Groups

| Group | Removed rank columns |
|---|---|
| return/reversal | `rank_r_on_1d, rank_r_on_5d, rank_r_id_1d, rank_ret_cc_5d, rank_ret_cc_20d, rank_ret_cc_60d` |
| risk/liquidity/size | `rank_vol20, rank_vol60, rank_amihud20, rank_adv20_log, rank_market_cap_log` |
| fundamental/value/quality | `rank_piot_norm_lag1, rank_gross_profit_margin_lag1, rank_asset_turnover_ratio_lag1, rank_net_debt_to_equity_lag1, rank_price_to_book_lag1, rank_ev_to_ebit_lag1, rank_final_score_lag1, rank_score_velocity_lag1, rank_momentum_score_lag1` |
| earnings/revision | `rank_sue_lag1, rank_deps_lag1, rank_reps1_lag1, rank_repsf4_lag1` |
| short-interest/borrow-stress | `rank_dsi_lag1, rank_dtcn_lag1, rank_ddtcn_lag1` |
| industry-return | `rank_industry_return_lag1` |
