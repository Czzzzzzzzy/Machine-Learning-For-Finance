# Report-ready C2O Audit Tables and Text Snippets

Generated from the current repository outputs under `outputs/`, with non-numeric implementation details taken from the existing source code where required. Missing numeric results are explicitly labelled rather than inferred.

## 1. Feature Inventory

| feature_name                   | formula                                                                                | data_source                                   | required_lag                                                 | observable_1550_et_day_t                          |
|:-------------------------------|:---------------------------------------------------------------------------------------|:----------------------------------------------|:-------------------------------------------------------------|:--------------------------------------------------|
| rank_r_on_1d                   | r_overnight = adj_open_t / adj_close_{t-1} - 1                                         | prices.parquet: adjusted open, adjusted close | 0 trading days; Open_t is known after the 09:30 auction      | Yes                                               |
| rank_r_on_5d                   | rolling mean of r_overnight over 5 sessions, min_periods=3                             | prices.parquet: adjusted open, adjusted close | 0 trading days; uses overnight returns available by 15:50 ET | Yes                                               |
| rank_r_id_1d                   | r_intraday_{t-1} = adj_close_{t-1} / adj_open_{t-1} - 1                                | prices.parquet: adjusted open, adjusted close | 1 trading day                                                | Yes                                               |
| rank_ret_cc_5d                 | adj_close_{t-1} / adj_close_{t-6} - 1                                                  | prices.parquet: adjusted close                | 1 trading day                                                | Yes                                               |
| rank_ret_cc_20d                | adj_close_{t-1} / adj_close_{t-21} - 1                                                 | prices.parquet: adjusted close                | 1 trading day                                                | Yes                                               |
| rank_ret_cc_60d                | adj_close_{t-1} / adj_close_{t-61} - 1                                                 | prices.parquet: adjusted close                | 1 trading day                                                | Yes                                               |
| rank_vol20                     | annualised rolling std of close-to-close returns over 20 sessions, shifted 1 day       | prices.parquet: adjusted close                | 1 trading day                                                | Yes                                               |
| rank_vol60                     | annualised rolling std of close-to-close returns over 60 sessions, shifted 1 day       | prices.parquet: adjusted close                | 1 trading day                                                | Yes                                               |
| rank_amihud20                  | rolling mean over 20 sessions of abs(r_close_close) / dollar_volume, shifted 1 day     | prices.parquet: adjusted close, volume        | 1 trading day                                                | Yes                                               |
| rank_adv20_log                 | log(1 + trailing 20-day average dollar volume), shifted 1 day                          | prices.parquet: adjusted close, volume        | 1 trading day                                                | Yes                                               |
| rank_market_cap_log            | log(1 + market_cap_{t-1})                                                              | prices.parquet: market_cap                    | 1 trading day                                                | Yes                                               |
| rank_piot_norm_lag1            | piot_norm_{t-1}                                                                        | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_gross_profit_margin_lag1  | gross_profit_margin_{t-1}                                                              | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_asset_turnover_ratio_lag1 | asset_turnover_ratio_{t-1}                                                             | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_net_debt_to_equity_lag1   | net_debt_to_equity_{t-1}                                                               | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_price_to_book_lag1        | price_to_book_{t-1}                                                                    | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_ev_to_ebit_lag1           | ev_to_ebit_{t-1}                                                                       | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_sue_lag1                  | sue_{t-1}                                                                              | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_deps_lag1                 | deps_{t-1}                                                                             | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_reps1_lag1                | reps1_{t-1}                                                                            | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_repsf4_lag1               | repsf4_{t-1}                                                                           | all_data.parquet                              | 1 trading day                                                | Yes                                               |
| rank_final_score_lag1          | final_score_{t-1}                                                                      | cheapness_scores.parquet                      | 1 trading day                                                | Yes                                               |
| rank_score_velocity_lag1       | score_velocity_{t-1}                                                                   | cheapness_scores.parquet                      | 1 trading day                                                | Yes                                               |
| rank_momentum_score_lag1       | momentum_score_{t-1}                                                                   | cheapness_scores.parquet                      | 1 trading day                                                | Yes                                               |
| rank_dsi_lag1                  | dsi_{t-1}; daily short-interest proxy after publication/vendor lag already in source   | all_data.parquet                              | 1 trading day after source availability                      | Yes, if source obeys Section 2.1.3 lag convention |
| rank_dtcn_lag1                 | dtcn_{t-1}; daily days-to-cover proxy after publication/vendor lag already in source   | all_data.parquet                              | 1 trading day after source availability                      | Yes, if source obeys Section 2.1.3 lag convention |
| rank_ddtcn_lag1                | ddtcn_{t-1}; lagged change/stress proxy after publication/vendor lag already in source | all_data.parquet                              | 1 trading day after source availability                      | Yes, if source obeys Section 2.1.3 lag convention |
| rank_industry_return_lag1      | industry_return_{t-1}                                                                  | all_data.parquet                              | 1 trading day                                                | Yes                                               |

## 2. Feature Ablation Audit Table

| model_variant                                | feature_group_removed                 |    ic_mean |   ic_tstat |   net_sharpe_250m |   annual_return_250m |   annual_volatility_250m |   max_drawdown_250m | status                                                                  |
|:---------------------------------------------|:--------------------------------------|-----------:|-----------:|------------------:|---------------------:|-------------------------:|--------------------:|:------------------------------------------------------------------------|
| Full model                                   | None                                  |   0.027312 |   8.362962 |          0.373744 |             0.016627 |                 0.047088 |           -0.245771 | Generated from outputs/ic_daily.csv and outputs/performance_summary.csv |
| Remove return/reversal features              | return/reversal features              | MISSING    | MISSING    |        MISSING    |           MISSING    |               MISSING    |          MISSING    | Missing: current outputs do not contain feature-group ablation reruns   |
| Remove risk/liquidity/size features          | risk/liquidity/size features          | MISSING    | MISSING    |        MISSING    |           MISSING    |               MISSING    |          MISSING    | Missing: current outputs do not contain feature-group ablation reruns   |
| Remove fundamental/value/quality features    | fundamental/value/quality features    | MISSING    | MISSING    |        MISSING    |           MISSING    |               MISSING    |          MISSING    | Missing: current outputs do not contain feature-group ablation reruns   |
| Remove earnings-surprise/revision features   | earnings-surprise/revision features   | MISSING    | MISSING    |        MISSING    |           MISSING    |               MISSING    |          MISSING    | Missing: current outputs do not contain feature-group ablation reruns   |
| Remove short-interest/borrow-stress features | short-interest/borrow-stress features | MISSING    | MISSING    |        MISSING    |           MISSING    |               MISSING    |          MISSING    | Missing: current outputs do not contain feature-group ablation reruns   |
| Remove industry-return feature               | industry-return feature               | MISSING    | MISSING    |        MISSING    |           MISSING    |               MISSING    |          MISSING    | Missing: current outputs do not contain feature-group ablation reruns   |

Feature-group ablation results are not present in the current outputs; the table keeps the full-model baseline and marks the missing reruns explicitly.

## 3. Borrow Proxy Validation Section

The hard-to-borrow proxy used by the current implementation is deterministic and based on lagged short-interest stress variables. Tier A is the default general-collateral bucket. Tier B is assigned when `dsi_lag1 >= 0.08`, or `dtcn_lag1 >= 5.0`, or `ddtcn_lag1 >= 1.0`. Tier C is assigned when `dsi_lag1 >= 0.15`, or `dtcn_lag1 >= 10.0`, or both `dsi_lag1 >= 0.10` and `ddtcn_lag1 >= 1.5`. Borrow is then charged daily on the gross short notional at annualised rates of 40 bps for Tier A, 200 bps for Tier B, and 800 bps for Tier C, divided by 252.

The current outputs do not include the borrow tier attached to each short position, so the fraction of short positions in Tier A/B/C cannot be computed from `outputs/` alone. The file/function that should generate this is `src/c2o_strategy/portfolio.py::run_backtest`, by adding `borrow_tier` and `borrow_rate_annual` to the exported positions, or by writing a `borrow_tier_summary.csv` during the AUM loop in `src/c2o_strategy/run.py`.

Available gross-to-net Sharpe degradation by AUM:

|               aum |   gross_sharpe |   commission_sharpe_drag |   slippage_sharpe_drag |   borrow_sharpe_drag |   net_sharpe |   avg_borrow_bps_per_day |
|------------------:|---------------:|-------------------------:|-----------------------:|---------------------:|-------------:|-------------------------:|
|   50000000.000000 |       2.230864 |                 0.443168 |               1.329551 |             0.188195 |     0.269951 |                 0.423222 |
|  250000000.000000 |       1.723940 |                 0.309030 |               0.928677 |             0.112488 |     0.373744 |                 0.210237 |
| 1000000000.000000 |       0.800988 |                 0.201260 |               0.602233 |             0.070753 |    -0.073258 |                 0.060977 |

For the 250M headline strategy, borrow costs reduce Sharpe by 0.112 points after commission and slippage. Average borrow cost is 0.210 bps per day.

## 4. AMC/BMO Earnings Timing Example

A manually verifiable AMC/BMO example cannot be produced from the current `outputs/` directory because no output file contains individual earnings events, timing flags, or effective strategy dates. The required export should be generated inside `src/c2o_strategy/data.py::build_earnings_window_flags`, or immediately after it is called in `prepare_data`, with columns such as `ticker`, `instrument_id`, `raw_announcement_date`, `timing_flag`, `strat_trading_date`, `excluded_decision_date`, and `rule_applied`. The current available evidence is aggregate only: `outputs/eligibility_summary.csv` reports rows removed under `EARN_WINDOW`, but it does not identify a hand-checkable event.

## 5. Capacity Analysis

|               aum |   average_gross_exposure |   fraction_days_cap_binding |   net_sharpe |   avg_abs_per_stock_position |   max_abs_per_stock_position | position_source                                   |
|------------------:|-------------------------:|----------------------------:|-------------:|-----------------------------:|-----------------------------:|:--------------------------------------------------|
|   50000000.000000 |                 0.996909 |                    0.951245 |     0.269951 |                   MISSING    |                   MISSING    | Missing: positions were not exported for this AUM |
|  250000000.000000 |                 0.578918 |                    0.999735 |     0.373744 |               2904287.069598 |              98014573.966590 | outputs/positions_250m.parquet                    |
| 1000000000.000000 |                 0.172499 |                    0.999735 |    -0.073258 |                   MISSING    |                   MISSING    | Missing: positions were not exported for this AUM |

The 250M row has position-size statistics because `outputs/positions_250m.parquet` is available. The 50M and 1B rows do not have average/max per-stock position statistics in the current outputs. To complete those cells, export `positions_50m.parquet` and `positions_1000m.parquet`, or add daily per-position capacity metrics in `src/c2o_strategy/run.py`.

## 6. Stress-window Results, 250M AUM

| window        | start      | end        |   net_return |   net_sharpe |   max_drawdown |   avg_gross_exposure |
|:--------------|:-----------|:-----------|-------------:|-------------:|---------------:|---------------------:|
| late_2018     | 2018-10-01 | 2018-12-31 |    -0.009470 |    -2.093024 |      -0.010792 |             0.308901 |
| covid_q1_2020 | 2020-01-01 | 2020-03-31 |    -0.024528 |    -0.743456 |      -0.067739 |             0.549945 |
| drawdown_2022 | 2022-01-01 | 2022-12-31 |    -0.071592 |    -0.788106 |      -0.133588 |             0.936386 |

## 7. Draft Report Paragraphs

The 250M result is modest but credible because the reported Sharpe is produced after applying the full daily trading-cost stack and the participation cap. At 250M AUM, the strategy earns a net annualised return of 1.66% with annualised volatility of 4.71%, giving a net Sharpe of 0.374 and maximum drawdown of -24.58%. The gap between gross Sharpe (1.724) and net Sharpe is large and explicit: commission contributes 0.309 Sharpe points of degradation, auction slippage contributes 0.929, and borrow contributes 0.112. The result is therefore not a frictionless alpha claim; it is a capacity-constrained, costed overnight implementation whose remaining positive Sharpe survives the assumptions imposed by the brief.

The 1B result turns negative because the portfolio cannot deploy the same proportion of capital into the selected names without binding the liquidity constraint. Average gross exposure falls from 99.69% at 50M and 57.89% at 250M to only 17.25% at 1B, while the participation cap is binding on 99.97% of trading days. The gross Sharpe at 1B is still positive at 0.801, but lower utilisation, persistent capacity binding, and fixed daily round-trip costs reduce the strategy to a net Sharpe of -0.073. Economically, the alpha is not scalable enough to absorb a billion-dollar book under a 5% ADV participation cap.

## Missing-output Checklist

Numbers not present in the current outputs:
- Feature-group ablation reruns are not present. They should be generated by adding an ablation loop around `score_panel`, `compute_information_coefficients`, and `run_backtest` in `src/c2o_strategy/run.py`, or by creating a dedicated `src/c2o_strategy/ablation.py` that writes one row per removed group.
- Borrow-tier fractions for short positions are not present. `run_backtest` in `src/c2o_strategy/portfolio.py` should include `borrow_tier` and `borrow_rate_annual` in `positions_250m.parquet` or export a separate `borrow_tier_summary.csv`.
- Average and maximum per-stock positions for 50M and 1B are not present because only `positions_250m.parquet` was exported. The AUM loop in `src/c2o_strategy/run.py` should export positions for all AUMs or append daily capacity statistics to `performance_summary.csv`.
- A manually auditable AMC/BMO example is not present in the current outputs. `build_earnings_window_flags` in `src/c2o_strategy/data.py` should export `earnings_timing_examples.csv` with ticker, announcement date, timing flag, effective strategy date, and excluded decision dates.
