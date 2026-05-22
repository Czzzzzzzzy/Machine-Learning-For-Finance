# Final C2O Strategy Audit Report

**Coursework strategy:** close-to-open equity strategy using the promoted volatility-scaled overnight return target.  
**Final target:** `volatility_scaled_overnight_return = overnight_next / (vol20 / sqrt(252))`.  
**Volatility denominator:** trailing 20-day close-to-close volatility shifted by one trading day.  
**Development cutoff:** 2024-12-31. 2025-2026 is not used for development and is treated as held out for marker evaluation.  
**Headline 250M result:** 3.93% net annual return, 4.90% net volatility, 0.811 net Sharpe, and -10.19% maximum drawdown.  
**Primary sources:** `outputs/performance_summary.csv`, `outputs/report_ready/final_strategy_config.md`, `outputs/report_ready/final_strategy_selection_memo.md`, and `outputs/report_ready/final_reproduction_log.md`.

## 1. Executive Summary

The final promoted C2O strategy is not the original baseline. The original baseline remains the starting point and is archived in `outputs/baseline_archive/`. The archive readme records an original baseline pipeline Sharpe of about 0.374 at 250M and a logged experiment-harness baseline Sharpe of about 0.379 at 250M. The difference is disclosed in `outputs/baseline_archive/baseline_readme.md` and is treated as an implementation/logging distinction rather than a change in economic thesis.

The final strategy uses the same point-in-time feature set as the baseline, but changes the supervised learning target from raw overnight return to a volatility-scaled overnight return. Economically, this asks the model to rank stocks by risk-adjusted overnight opportunity rather than by raw overnight magnitude. That is a narrower and more defensible improvement than adding new signals after seeing results: the feature set, universe rules, costs, borrow treatment, participation cap, and development cutoff remain frozen.

At 250M AUM the final strategy earns 3.93% net annual return with 4.90% net volatility, a net Sharpe of 0.811, and a maximum drawdown of -10.19%. These numbers come from `outputs/performance_summary.csv`. The result is modest rather than spectacular. It is credible precisely because it is reported net of commission, auction slippage, and borrow costs; because the 5% ADV20 participation cap is enforced in the positions files; and because the final audit acknowledges that performance degrades under larger capital.

The strongest caution is capacity. At 50M the strategy uses nearly the full target gross exposure and records a net Sharpe of 0.850. At 250M average gross exposure falls to 70.43% because the participation cap binds on almost every trading day. At 1B it falls to 22.82%, and the net Sharpe falls to 0.266. This is not presented as a scalable institutional anomaly at arbitrary size. It is a small-to-mid-capacity overnight implementation whose economics are materially shaped by trading constraints.

The second major caution is costs. The 250M gross Sharpe is 2.427, but commission, auction slippage, and borrow reduce it to 0.811. Auction slippage is the largest single degradation item. The report therefore avoids gross-return marketing and treats implementation as part of the strategy, not an afterthought.

### Final Performance by AUM

| AUM   | Net annual return   | Net vol   |   Net Sharpe | Max drawdown   |   Gross Sharpe |   Avg turnover | Avg gross exposure   | IC mean   |   IC t-stat |
|:------|:--------------------|:----------|-------------:|:---------------|---------------:|---------------:|:---------------------|:----------|------------:|
| $50m  | 4.30%               | 5.11%     |        0.85  | -15.50%        |          3.071 |          1.998 | 99.90%               | 2.82%     |       9.465 |
| $250m | 3.93%               | 4.90%     |        0.811 | -10.19%        |          2.427 |          1.409 | 70.43%               | 2.82%     |       9.465 |
| $1bn  | 0.67%               | 2.64%     |        0.266 | -16.06%        |          1.239 |          0.456 | 22.82%               | 2.82%     |       9.465 |

Source: `outputs/performance_summary.csv`. Basket selection rule, participation cap, cost schedule, and target version are documented in `outputs/report_ready/final_strategy_config.md`.

### Baseline Versus Final Candidate at 250M

| Strategy                               | Net annual return   | Net vol   |   Net Sharpe | Max DD   |   Gross Sharpe |   Commission drag |   Slippage drag |   Borrow drag |   Turnover | Avg gross exp.   | IC mean   |   IC t-stat | Worst 12m   |
|:---------------------------------------|:--------------------|:----------|-------------:|:---------|---------------:|------------------:|----------------:|--------------:|-----------:|:-----------------|:----------|------------:|:------------|
| Original baseline (experiment harness) | 1.69%               | 4.71%     |        0.379 | -24.58%  |          1.729 |             0.309 |           0.928 |         0.112 |      1.158 | 57.89%           | 2.73%     |       8.363 | -12.98%     |
| Final volatility-scaled target         | 3.93%               | 4.90%     |        0.811 | -10.19%  |          2.427 |             0.361 |           1.084 |         0.17  |      1.409 | 70.43%           | 2.82%     |       9.465 | -10.09%     |

Source: `outputs/report_ready/final_candidate_comparison.csv`; baseline archive explanation in `outputs/baseline_archive/baseline_readme.md`.

## 2. Data, Return Construction, and Point-in-Time Controls

The strategy is built around overnight returns from close on day `t` to open on day `t+1`. The final modelling target is the next overnight return scaled by trailing realized volatility. The denominator is `vol20 / sqrt(252)`, where `vol20` is a 20-trading-day close-to-close volatility estimate shifted by one trading day. This shift is the critical point-in-time control: the target transformation cannot see the close-to-close return that is still unknown at the 15:50 ET decision time on day `t`.

The point-in-time audit in `outputs/report_ready/volatility_scaled_target_point_in_time_audit.md` is the basis for promoting the candidate. It verifies that the volatility denominator uses trailing information, is shifted, does not use future overnight returns, does not use future close/high/low observations, does not use full-sample volatility, and does not introduce 2025+ data. The audit also confirms that the target transformation changes only the training target and not the live feature set.

The return construction was reconciled against the available price fields. The frozen reconciliation file reports the following checks:

| Metric              | Value     |
|:--------------------|:----------|
| tolerance           | 1.000e-08 |
| stock_days_checked  | 5,469,968 |
| fail_count          | 0         |
| fail_fraction       | 0         |
| median_abs_residual | 0.000e+00 |
| p99_abs_residual    | 2.220e-16 |
| max_abs_residual    | 4.441e-16 |

Source: `outputs/return_reconciliation_summary.csv`.

### Earnings Timing Controls

Earnings data are a classic look-ahead risk in close-to-open strategies. The frozen audit examples include one after-market-close case, one before-market-open case, and a same-day example. The rules preserve decision-time availability: before-market events can be known before that day’s close, while after-market events are not available before that close.

| Ticker   |   Instrument | Reporting date   | Timing   | Raw event date   | Strategy trading date   | Excluded decision dates            | Rule applied                                                                              |
|:---------|-------------:|:-----------------|:---------|:-----------------|:------------------------|:-----------------------------------|:------------------------------------------------------------------------------------------|
| MOS      |           18 | 2010-01-05       | after    | 2010-01-05       | 2010-01-05              | 2010-01-04, 2010-01-05, 2010-01-06 | After-market event is not known before the close; use provided strategy trading date.     |
| RPM      |         1275 | 2010-01-06       | before   | 2010-01-06       | 2010-01-05              | 2010-01-04, 2010-01-05, 2010-01-06 | Before-market event is known before that day's close; use provided strategy trading date. |
| MOS      |           18 | 2010-01-05       | after    | 2010-01-05       | 2010-01-05              | 2010-01-04, 2010-01-05, 2010-01-06 | After-market event is not known before the close; use provided strategy trading date.     |

Source: `outputs/earnings_timing_examples.csv` and `outputs/report_ready/earnings_timing_audit.md`.

The hand-checkable examples matter because an earnings feature can accidentally become a future-information feature if all reporting dates are treated identically. The final audit does not rely on a generic statement that the data are lagged; it exports concrete examples with `raw_event_date`, `strat_trading_date`, excluded decision dates, the rule applied, and a text explanation.

### Short-Interest Timing Controls

Short-interest data are lagged relative to economic reality and can be dangerous if the model is allowed to use a value before it could have been published or vendor-processed. The frozen implementation applies a one-trading-day strategy lag to the processed `all_data` source panel. The audit examples are:

| Ticker   |   Instrument | Source feature date   | Decision date using lag1   |      DSI |    DTCN |     DDTCN | Rule applied                                                                                                               |
|:---------|-------------:|:----------------------|:---------------------------|---------:|--------:|----------:|:---------------------------------------------------------------------------------------------------------------------------|
| HLT      |            1 | 2015-01-27            | 2015-01-28                 | 0.004074 | 1.66949 | -0.245679 | Short-interest proxies are read from the daily all_data panel, then shifted one trading day in add_point_in_time_features. |
| HLT      |            1 | 2015-01-28            | 2015-01-29                 | 0.004074 | 1.66949 | -0.245679 | Short-interest proxies are read from the daily all_data panel, then shifted one trading day in add_point_in_time_features. |
| HLT      |            1 | 2015-01-29            | 2015-01-30                 | 0.004074 | 1.66949 | -0.245679 | Short-interest proxies are read from the daily all_data panel, then shifted one trading day in add_point_in_time_features. |

Source: `outputs/short_interest_lag_examples.csv` and `outputs/report_ready/short_interest_lag_audit.md`.

The limitation is explicit: the frozen outputs do not contain raw FINRA settlement and publication dates. The report therefore does not claim independent validation of the original short-interest publication lag. It claims only what is supported by the repository evidence: the strategy consumes a processed source panel and adds a one-trading-day decision lag. This is also listed in `outputs/report_ready/report_missing_items.md`.

### Feature Inventory and Observability

The final feature set is unchanged from the baseline. The report-ready feature inventory records the formula, data source, required lag, and whether the feature is observable at 15:50 ET on day `t`. A compact extract is shown below; the complete table is in `outputs/report_ready/feature_inventory.csv`.

| Feature                        | Formula                                                                                | Data source                                   | Required lag                                                 | Observable at 15:50 ET day t                      |
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

Source: `outputs/report_ready/feature_inventory.csv`.

## 3. Universe Construction and Capacity Filters

The final universe, eligibility filters, basket rule, and participation cap are frozen in `outputs/report_ready/final_strategy_config.md`. The final report treats these implementation choices as part of the strategy definition, because the overnight signal is only investable if it can be traded near the close and open with realistic size.

The final capacity constraint is a 5% ADV20 participation cap. Positions are clipped against the cap before final weights and dollar positions are recorded. The frozen positions files include `adv20_dollar`, `participation_rate`, `cap_dollar`, and `cap_binding_flag`, which allows the reported exposure reduction to be checked from position-level evidence rather than from summary claims alone.

### Universe Evolution

|   Year |   Universe Count | Ref Date   | Median Year Start Mcap   |   Mid Year Exits |
|-------:|-----------------:|:-----------|:-------------------------|-----------------:|
|   2010 |              986 | 2009-12-31 | $2.46bn                  |                0 |
|   2011 |              986 | 2010-12-31 | $3.25bn                  |                0 |
|   2012 |              988 | 2011-12-30 | $3.25bn                  |                0 |
|   2013 |              988 | 2012-12-31 | $3.86bn                  |                0 |
|   2014 |              987 | 2013-12-31 | $5.42bn                  |                0 |
|   2015 |              986 | 2014-12-31 | $6.07bn                  |                0 |
|   2016 |              987 | 2015-12-31 | $6.06bn                  |                0 |
|   2017 |              988 | 2016-12-30 | $7.07bn                  |                0 |
|   2018 |              988 | 2017-12-29 | $8.73bn                  |                0 |
|   2019 |              988 | 2018-12-31 | $7.47bn                  |                0 |
|   2020 |              989 | 2019-12-31 | $9.62bn                  |                0 |
|   2021 |              990 | 2020-12-31 | $11.62bn                 |                0 |
|   2022 |              988 | 2021-12-31 | $14.16bn                 |                0 |
|   2023 |              988 | 2022-12-30 | $11.50bn                 |                0 |
|   2024 |              989 | 2023-12-29 | $13.06bn                 |                0 |

Source: `outputs/universe_summary.csv`.

### Eligibility Exclusions

| Eligibility reason   | Stock-days   |
|:---------------------|:-------------|
| OK                   | 3,194,145    |
| MCAP_FAIL            | 1,596,321    |
| ADV_FAIL             | 513,267      |
| EARN_WINDOW          | 116,925      |
| PRICE_FAIL           | 26,307       |
| VOL_FAIL             | 22,458       |
| DATA_FAIL            | 1,000        |

Source: `outputs/eligibility_summary.csv`.

### Capacity Evidence

| AUM   | Avg gross exposure used   |   Cap-binding days | Fraction cap-binding days   | Avg per-stock abs position   | Max per-stock abs position   | Avg participation   | Max participation   | Position-days at cap   |
|:------|:--------------------------|-------------------:|:----------------------------|:-----------------------------|:-----------------------------|:--------------------|:--------------------|:-----------------------|
| $50m  | 99.90%                    |               3464 | 91.79%                      | $1.00m                       | $7.40m                       | 1.99%               | 5.00%               | 16.16%                 |
| $250m | 70.43%                    |               3773 | 99.97%                      | $3.53m                       | $98.01m                      | 3.76%               | 5.00%               | 61.68%                 |
| $1bn  | 22.82%                    |               3773 | 99.97%                      | $4.58m                       | $414.68m                     | 3.96%               | 5.00%               | 67.87%                 |

Source: `outputs/report_ready/position_capacity_summary.csv`.

The capacity table is one of the most important controls in the report. At 250M, the strategy is not simply choosing to run lower risk. It is capacity constrained: cap-binding days are nearly the whole sample, average gross exposure used is 70.43%, and 61.68% of position-days sit at the cap. At 1B, average gross exposure drops to 22.82% and 67.87% of position-days are capped. That explains why the 1B result is much weaker even though the underlying ranking signal remains the same.

The frozen outputs report fixed auction slippage and realized participation, but do not export a separate square-root market-impact estimate at the 5% cap. The report therefore does not introduce a new impact model. This limitation is listed in `outputs/report_ready/report_missing_items.md`.

## 4. Borrow Proxy and Short-Leg Treatment

The short leg is not treated as free. The final strategy applies tiered borrow costs based on the hard-to-borrow proxy documented in `outputs/report_ready/borrow_proxy_methodology.md`. The proxy uses short-interest and borrow-stress style variables from the processed data. The final implementation applies borrow cost tiers to short positions; it does not hard-exclude short candidates during selection.

The hard-to-borrow proxy is deterministic and uses lagged short-interest stress fields from the point-in-time panel. Tier A is the default borrow tier at 40 bps per annum. Tier B applies when `dsi_lag1 >= 0.08`, or `dtcn_lag1 >= 5.0`, or `ddtcn_lag1 >= 1.0`, and is charged at 200 bps per annum. Tier C applies when `dsi_lag1 >= 0.15`, or `dtcn_lag1 >= 10.0`, or both `dsi_lag1 >= 0.10` and `ddtcn_lag1 >= 1.5`, and is charged at 800 bps per annum. Borrow is charged daily on short notional as `borrow_rate_annual / 252`. Source: `outputs/report_ready/borrow_proxy_methodology.md`.

| Borrow tier | Proxy threshold | Annual borrow rate | Final treatment |
|---|---|---:|---|
| A | Default tier when Tier B/C thresholds are not met | 40 bps | Cost applied to short notional |
| B | `dsi_lag1 >= 0.08`, or `dtcn_lag1 >= 5.0`, or `ddtcn_lag1 >= 1.0` | 200 bps | Cost applied to short notional |
| C | `dsi_lag1 >= 0.15`, or `dtcn_lag1 >= 10.0`, or both `dsi_lag1 >= 0.10` and `ddtcn_lag1 >= 1.5` | 800 bps | Cost applied to short notional |

The final audit reports that 94,035 raw short position-days were observed, of which 57,039 are Tier B or Tier C. This is 60.66% of raw short position-days. The same file reports that the fraction of raw short signal affected by borrow treatment is 0.00% because borrow treatment is cost-only in the final configuration, not a selection filter. Source: `outputs/report_ready/short_signal_affected_by_borrow.csv`.

### Borrow Cost Degradation

| AUM   |   Gross Sharpe |   Commission drag |   Auction slippage drag |   Borrow drag |   Net Sharpe |   Avg daily borrow bps |
|:------|---------------:|------------------:|------------------------:|--------------:|-------------:|-----------------------:|
| $50m  |          3.071 |             0.493 |                   1.48  |         0.249 |        0.85  |                  0.503 |
| $250m |          2.427 |             0.361 |                   1.084 |         0.17  |        0.811 |                  0.331 |
| $1bn  |          1.239 |             0.218 |                   0.654 |         0.1   |        0.266 |                  0.105 |

Source: `outputs/report_ready/borrow_sharpe_degradation.csv`.

### Borrow Tier Summary

| AUM   | Tier   |   Short position-days | Share   | Avg short notional   | Total borrow cost   |   Avg daily borrow bps |
|:------|:-------|----------------------:|:--------|:---------------------|:--------------------|-----------------------:|
| $50m  | A      |                 36996 | 39.34%  | $1.10m               | $645.08k            |                  0.503 |
| $50m  | B      |                 36226 | 38.52%  | $948.06k             | $2.73m              |                  0.503 |
| $50m  | C      |                 20813 | 22.13%  | $926.10k             | $6.12m              |                  0.503 |
| $250m | A      |                 36996 | 39.34%  | $4.02m               | $2.36m              |                  0.331 |
| $250m | B      |                 36226 | 38.52%  | $3.40m               | $9.78m              |                  0.331 |
| $250m | C      |                 20813 | 22.13%  | $2.89m               | $19.10m             |                  0.331 |
| $1bn  | A      |                 36996 | 39.34%  | $5.48m               | $3.22m              |                  0.105 |
| $1bn  | B      |                 36226 | 38.52%  | $4.16m               | $11.97m             |                  0.105 |
| $1bn  | C      |                 20813 | 22.13%  | $3.70m               | $24.44m             |                  0.105 |

Source: `outputs/report_ready/borrow_tier_summary.csv`.

The borrow table is deliberately reported in position-days, not just dollars, because a strategy can hide borrow risk by netting costs into aggregate returns. At 250M, Tier A accounts for 39.34% of short position-days, Tier B for 38.52%, and Tier C for 22.13%. Tier C has fewer position-days than the other tiers but a larger annualized cost assumption, so it accounts for a material share of total borrow cost.

The external validation limitation is also explicit. No independent locate-fee or borrow-fee file is present in the frozen outputs, so the report cannot claim external validation of the proxy thresholds. It reports the proxy definition, thresholds, tier shares, and cost consequences instead. This is a sceptical rather than promotional treatment of the short leg.

## 5. Alpha Model and Target Engineering

The final model is a cross-sectional overnight alpha model. Its key design choice is the promoted target: `overnight_next / (vol20 / sqrt(252))`. This target is economically interpretable. Raw overnight returns can be dominated by volatile stocks; volatility scaling rewards names whose expected overnight opportunity is large relative to their recent close-to-close risk. The change is therefore a target-engineering decision, not a new data source.

The final feature set remains unchanged from the baseline. This matters for look-ahead control. If the Sharpe improvement had come from adding new features, the audit burden would be wider. Here the main question is narrower: whether the denominator in the transformed target is point-in-time valid. The dedicated audit passed that question.

The final 250M IC mean is 2.82% with an IC t-stat of 9.465. The baseline experiment-harness IC mean is 2.73% with an IC t-stat of 8.363. Source: `outputs/report_ready/final_candidate_comparison.csv`. The improvement is not only a realized volatility artifact; the ranking statistic is slightly stronger as well. However, the report does not overstate this. The realized performance improvement is larger than the IC improvement, indicating that risk scaling and realized portfolio volatility also contribute.

### Feature Ablation at 250M

| Variant                             | Removed group                | IC mean   |   IC t-stat | Net annual return   | Net vol   |   Net Sharpe | Max DD   |   Avg turnover | Avg gross exposure   |
|:------------------------------------|:-----------------------------|:----------|------------:|:--------------------|:----------|-------------:|:---------|---------------:|:---------------------|
| full_model                          | none                         | 2.82%     |       9.465 | 3.93%               | 4.90%     |        0.811 | -10.19%  |          1.409 | 70.43%               |
| remove_return/reversal              | return/reversal              | 0.79%     |       2.106 | -4.80%              | 5.02%     |       -0.954 | -55.66%  |          1.011 | 50.53%               |
| remove_risk/liquidity/size          | risk/liquidity/size          | 2.85%     |      11.364 | 4.49%               | 4.82%     |        0.934 | -8.48%   |          1.605 | 80.27%               |
| remove_fundamental/value/quality    | fundamental/value/quality    | 2.92%     |       9.784 | 4.14%               | 4.75%     |        0.878 | -10.38%  |          1.382 | 69.10%               |
| remove_earnings/revision            | earnings/revision            | 2.75%     |       9.177 | 4.05%               | 4.85%     |        0.841 | -10.19%  |          1.407 | 70.34%               |
| remove_short-interest/borrow-stress | short-interest/borrow-stress | 2.85%     |       9.52  | 4.99%               | 5.22%     |        0.959 | -11.32%  |          1.474 | 73.69%               |
| remove_industry-return              | industry-return              | 2.82%     |       9.469 | 3.84%               | 4.90%     |        0.795 | -10.19%  |          1.408 | 70.40%               |

Source: `outputs/feature_ablation_summary.csv` and `outputs/report_ready/feature_ablation_audit.md`.

The ablation audit is mixed, which is useful. Removing return/reversal features sharply damages performance: the 250M net Sharpe falls from 0.811 to -0.954. That is consistent with an overnight reversal/continuation mechanism being central to the strategy. Removing risk/liquidity/size improves the 250M net Sharpe in the frozen ablation table, which means those features are not automatically valuable in this specification. This does not invalidate the final strategy, but it warns against telling a simple story that every feature group contributes positively.

The final strategy was not retuned during ablation. The ablation is therefore an audit of feature dependence under the frozen modelling setup, not a fresh search over hyperparameters.

## 6. Portfolio Construction and Cost Model

The final strategy selects a daily long and short basket according to the frozen basket selection rule in `outputs/report_ready/final_strategy_config.md`. The positions are held overnight from the decision close to the next open. The final positions files are exported for 50M, 250M, and 1B AUM and include the fields needed to audit score, target weight, final clipped weight, dollar position, cap binding, gross PnL, commission, slippage, borrow cost, net PnL, and borrow tier.

The cost model includes commission, auction slippage, and borrow. This report treats auction slippage as an essential part of the close/open implementation, not as a sensitivity to be added later. At 250M, gross Sharpe is 2.427, but commission drag is 0.361, auction slippage drag is 1.084, and borrow drag is 0.170, leaving net Sharpe of 0.811. Source: `outputs/report_ready/borrow_sharpe_degradation.csv`.

The same cost table shows why gross results are misleading. At 50M gross Sharpe is 3.071 and net Sharpe is 0.850; at 1B gross Sharpe is 1.239 and net Sharpe is 0.266. Costs are not a cosmetic adjustment; they decide whether the strategy is economically interesting.

## 7. Empirical Results

At the chosen reporting size of 250M, the final strategy has a net annual return of 3.93%, net volatility of 4.90%, net Sharpe of 0.811, and max drawdown of -10.19%. These are the headline numbers in `outputs/performance_summary.csv` and `outputs/report_ready/final_reproduction_log.md`.

The result is credible but not grand. A 3.93% annual return is not enough to survive careless implementation or inflated fees. It becomes interesting because volatility is controlled, because the drawdown is materially smaller than the archived baseline comparison, and because the result survives cost and capacity constraints at 250M. It is still not a claim of live profitability in 2025-2026. Those years are held out for marker evaluation.

### Year-by-Year Final Results at 250M

|   Year | Annual return   | Annual vol   |   Annual Sharpe | Max DD   | IC mean   | Avg gross exposure   |
|-------:|:----------------|:-------------|----------------:|:---------|:----------|:---------------------|
|   2010 | -10.09%         | 3.42%        |          -3.094 | -10.19%  | -3.48%    | 42.46%               |
|   2011 | 21.39%          | 5.63%        |           3.474 | -2.08%   | 6.22%     | 67.54%               |
|   2012 | 6.70%           | 2.80%        |           2.333 | -1.68%   | 4.67%     | 56.93%               |
|   2013 | 5.61%           | 2.38%        |           2.307 | -1.17%   | 7.22%     | 64.02%               |
|   2014 | 2.57%           | 3.66%        |           0.712 | -5.01%   | 4.23%     | 80.35%               |
|   2015 | 1.58%           | 2.31%        |           0.691 | -1.73%   | 3.75%     | 57.44%               |
|   2016 | 1.13%           | 1.97%        |           0.578 | -1.83%   | 4.21%     | 38.38%               |
|   2017 | -0.46%          | 1.38%        |          -0.331 | -1.60%   | 2.79%     | 42.84%               |
|   2018 | 2.82%           | 3.01%        |           0.939 | -1.99%   | 2.17%     | 69.11%               |
|   2019 | 5.85%           | 3.53%        |           1.63  | -1.38%   | 2.98%     | 83.78%               |
|   2020 | -3.15%          | 9.23%        |          -0.3   | -9.08%   | 0.81%     | 86.51%               |
|   2021 | 2.70%           | 5.47%        |           0.515 | -5.70%   | -2.11%    | 77.36%               |
|   2022 | 28.21%          | 8.10%        |           3.111 | -2.86%   | 6.29%     | 95.46%               |
|   2023 | 3.99%           | 5.95%        |           0.687 | -5.88%   | 2.82%     | 95.42%               |
|   2024 | -4.13%          | 6.17%        |          -0.652 | -8.30%   | -0.29%    | 98.81%               |

Source: `outputs/report_ready/baseline_vs_candidate_yearly.csv`.

The final strategy has positive annual returns in 11 out of 15 calendar years in the frozen 250M yearly table. Its weakest year is 2010, with annual return -10.09%. Its strongest year is 2022, with annual return 28.21%. These figures come from `outputs/report_ready/baseline_vs_candidate_yearly.csv`.

### QuantStats Tear Sheet

A QuantStats HTML tear sheet for the final 250M strategy is saved at `outputs/quantstats_250m.html`. Figure caption for any use of that tear sheet: AUM = 250M; basket selection rule = frozen final basket rule in `outputs/report_ready/final_strategy_config.md`; participation cap = 5% ADV20; cost schedule = commission, auction slippage, and tiered borrow costs from the frozen final configuration; target version = volatility-scaled overnight return.

## 8. Robustness, Feature Ablation, and Stress Windows

The stress-window analysis compares the archived logged baseline and the final volatility-scaled target in three difficult windows: late 2018, 2020 Q1, and the 2022 drawdown. The final result is not uniformly better on every metric, which is important. In late 2018 the final strategy has a positive net return but a slightly worse max drawdown than the baseline. In 2020 Q1 and 2022, it is materially stronger in the frozen outputs.

### Stress Windows at 250M

| Window        | Strategy   | Net return   |   Annualized Sharpe | Max DD   | Avg gross exposure   |   Avg turnover |   Days |
|:--------------|:-----------|:-------------|--------------------:|:---------|:---------------------|---------------:|-------:|
| covid_q1_2020 | Baseline   | -2.45%       |              -0.743 | -6.77%   | 54.99%               |          1.1   |     62 |
| covid_q1_2020 | Final      | 2.24%        |               1.02  | -3.05%   | 87.97%               |          1.759 |     62 |
| drawdown_2022 | Baseline   | -7.16%       |              -0.788 | -13.36%  | 93.64%               |          1.873 |    251 |
| drawdown_2022 | Final      | 28.09%       |               3.111 | -2.86%   | 95.46%               |          1.909 |    251 |
| late_2018     | Baseline   | -0.95%       |              -2.093 | -1.08%   | 30.89%               |          0.618 |     63 |
| late_2018     | Final      | 0.17%        |               0.235 | -1.30%   | 67.95%               |          1.359 |     63 |

Source: `outputs/report_ready/baseline_vs_candidate_stress_windows.csv`.

The stress table supports promotion, but not triumphalism. The 2022 window is particularly strong for the final strategy, with 28.09% net return and 3.111 annualized Sharpe. That helps the full-sample result. A sceptical marker should ask whether that is a single lucky sub-period. The year-by-year table partially addresses this: the final strategy is positive in 11 of 15 years, but not in every year, and 2010 remains a materially negative year.

The feature ablation table provides a different robustness check. The strategy depends heavily on return/reversal information. It is less clearly helped by every other group. This supports a focused economic interpretation rather than a broad claim that all available data sources are equally useful.

## 9. Limitations and Held-Out Evaluation Risk

The main limitations are capacity, cost realism, borrow validation, and future-period uncertainty.

Capacity is the cleanest limitation because it is measured directly. At 1B, the strategy cannot deploy enough capital under the 5% ADV20 cap. Average gross exposure used is only 22.82%, and the net Sharpe is 0.266. The negative intuition is not that the alpha disappears completely; it is that the tradable expression becomes too constrained. A rank signal with insufficient executable notional is not a scalable portfolio.

Costs are also central. The final 250M gross Sharpe of 2.427 would look impressive if shown alone. Net Sharpe is 0.811 after commission, auction slippage, and borrow. The difference is the implementation reality of trading a close-to-open basket.

Borrow honesty is incomplete but disclosed. The final output includes tiered borrow costs and short-position tier shares. It does not include external borrow-fee validation, and the strategy does not change selection based on borrow tier. That means hard-to-borrow exposure affects net returns through cost, not through avoided trades.

Short-interest timing is controlled at the processed-panel level, but the repository does not include raw publication-date evidence. The final report therefore avoids claiming more than the files support.

Finally, 2025-2026 is held out for marker evaluation. The report does not claim that the final 2010-2024 result necessarily persists. The correct interpretation is narrower: under the frozen data cutoff and final implementation, the volatility-scaled target is a point-in-time valid improvement over the archived baseline.

## 10. Section 7 Sceptical-Marker Questions

**Look-ahead.** The promoted target passed a point-in-time audit. `vol20` is trailing and shifted by one trading day; the feature set is unchanged; and the final reproduction log confirms the cached final panel maxes out at 2024-12-31. Earnings and short-interest audits provide hand-checkable examples. The remaining short-interest limitation is source-panel publication timing, disclosed in `outputs/report_ready/report_missing_items.md`.

**Statistical robustness.** The 250M IC mean is 2.82% with t-stat 9.465. The final strategy is positive in 11 of 15 calendar years. Feature ablation shows the model is materially dependent on return/reversal features; it is not robust to removing that group. The stress-window results are favorable in 2020 Q1 and 2022 but less clean in late 2018.

**Capacity and execution honesty.** The report shows 50M, 250M, and 1B AUM. The 5% ADV20 cap is enforced and exported at position level. The 1B result is weak because exposure cannot be deployed under the cap. Auction slippage is the largest Sharpe drag at 250M and is reported separately.

**Borrow honesty.** The report includes tiered borrow costs, borrow-tier position-day shares, and gross-to-net Sharpe degradation. It also states that external borrow-fee validation is not present and that borrow treatment is cost-only rather than a hard exclusion.

**Reporting integrity.** The original baseline is archived, the final strategy is frozen, final outputs are generated under `outputs/` and `outputs/report_ready/`, and reproducibility is documented. `outputs/report_ready/final_reproduction_log.md` records that `make reproduce` and `make test` passed, with 4 tests passing.

## 11. Conclusion

The final strategy should be presented as a disciplined improvement over the baseline, not as a discovered magic formula. The promoted target is economically sensible and point-in-time valid: it ranks overnight opportunities by expected return per unit of recent realized volatility. At 250M, the final net Sharpe of 0.811 is materially higher than the archived baseline comparison and the max drawdown is materially smaller.

The strategy is still capacity limited. It is most credible around the 50M to 250M scale and becomes weak at 1B under the 5% ADV20 cap. It is also highly sensitive to execution costs, especially auction slippage. These caveats are not side notes; they are part of the final conclusion.

The recommended final submission is therefore the frozen volatility-scaled overnight return strategy, with 2025-2026 left untouched for external evaluation.


## Appendix A. Frozen Final Configuration Crosswalk

The following configuration table is copied from the frozen strategy configuration rather than reconstructed from code. Its purpose is to make the submitted report auditable without asking the marker to infer the strategy settings from multiple files.

| Configuration item | Frozen setting | Source |
|---|---|---|
| Final strategy name | `E_target_transform / volatility_scaled_overnight_return` | `outputs/report_ready/final_strategy_config.md` |
| Target | `volatility_scaled_overnight_return` | `outputs/report_ready/final_strategy_config.md` |
| Target definition | `overnight_next / (vol20 / sqrt(252))` | `outputs/report_ready/final_strategy_config.md` |
| Overnight return definition | `adj_open_(t+1) / adj_close_t - 1` | `outputs/report_ready/final_strategy_config.md` |
| Volatility denominator | trailing 20-day close-to-close volatility, annualised, shifted by one trading day | `outputs/report_ready/final_strategy_config.md` |
| Feature set | unchanged from the original baseline point-in-time feature set | `outputs/report_ready/final_strategy_config.md` |
| Universe | annual top-1000 US common-equity universe by market capitalisation | `outputs/report_ready/final_strategy_config.md` |
| Universe freeze | each year uses the last trading day of the previous year | `outputs/report_ready/final_strategy_config.md` |
| Minimum history | 252 price observations | `outputs/report_ready/final_strategy_config.md` |
| Minimum price | $5.00 | `outputs/report_ready/final_strategy_config.md` |
| Minimum ADV20 | $10,000,000 | `outputs/report_ready/final_strategy_config.md` |
| Volatility band | 5% to 120% annualised | `outputs/report_ready/final_strategy_config.md` |
| Earnings exclusion | +/- 1 trading day | `outputs/report_ready/final_strategy_config.md` |
| Long basket | top 3% of eligible names by alpha score | `outputs/report_ready/final_strategy_config.md` |
| Short basket | bottom 3% of eligible names by alpha score | `outputs/report_ready/final_strategy_config.md` |
| Minimum basket size | 15 names per side | `outputs/report_ready/final_strategy_config.md` |
| Weighting | equal weighting within each side, subject to capacity caps | `outputs/report_ready/final_strategy_config.md` |
| Dollar neutrality | long and short books matched after capacity sizing | `outputs/report_ready/final_strategy_config.md` |
| Participation cap | 5.0% of ADV20 per name | `outputs/report_ready/final_strategy_config.md` |
| AUM levels | 50M, 250M, 1B | `outputs/report_ready/final_strategy_config.md` |
| Commission | 0.5 bps per leg, 1.0 bps round trip | `outputs/report_ready/final_strategy_config.md` |
| Auction slippage | 1.5 bps per leg, 3.0 bps round trip | `outputs/report_ready/final_strategy_config.md` |
| Non-borrow round-trip cost | 4.0 bps on notional turnover | `outputs/report_ready/final_strategy_config.md` |
| Borrow Tier A | 40 bps per annum | `outputs/report_ready/final_strategy_config.md` |
| Borrow Tier B | 200 bps per annum | `outputs/report_ready/final_strategy_config.md` |
| Borrow Tier C | 800 bps per annum | `outputs/report_ready/final_strategy_config.md` |
| Borrow application | charged daily on short notional as annual rate / 252 | `outputs/report_ready/final_strategy_config.md` |
| Hard borrow exclusion | none in final strategy | `outputs/report_ready/final_strategy_config.md` |
| Start date | 2010-01-01 | `outputs/report_ready/final_strategy_config.md` |
| Development cutoff | 2024-12-31 | `outputs/report_ready/final_strategy_config.md` |
| Random seed | 42; deterministic implementation | `outputs/report_ready/final_strategy_config.md` |

This table is also the caption disclosure standard for any final strategy figure. Where a figure is strategy-specific, the caption must identify AUM, basket rule, 5% ADV20 participation cap, commission/slippage/borrow cost schedule, and volatility-scaled target version.

## Appendix B. Coursework Brief Crosswalk

This crosswalk states where the report answers the coursework brief. It is included to reduce ambiguity for marking: each answer is tied to a frozen output file, not a later calculation.

| Brief area | Report answer | Frozen source files |
|---|---|---|
| Section 2: return construction | Close-to-open return uses adjusted close at day `t` and adjusted open at day `t+1`; reconciliation reports zero failures under the exported tolerance. | `outputs/return_reconciliation_summary.csv` |
| Section 2: point-in-time controls | Volatility denominator is trailing and shifted; target transformation changes only the label, not features. | `outputs/report_ready/volatility_scaled_target_point_in_time_audit.md`, `outputs/report_ready/final_strategy_config.md` |
| Section 2: earnings timing | AMC, BMO, and same-day timing examples are exported with event date, strategy trading date, excluded decision dates, rule, and explanation. | `outputs/earnings_timing_examples.csv`, `outputs/report_ready/earnings_timing_audit.md` |
| Section 2: short-interest timing | Processed short-interest proxies are shifted one trading day before strategy use; raw publication-date limitation is disclosed. | `outputs/short_interest_lag_examples.csv`, `outputs/report_ready/short_interest_lag_audit.md`, `outputs/report_ready/report_missing_items.md` |
| Section 3: universe construction | Annual top-1000 universe is frozen from the prior year-end reference date; universe counts and median market cap are exported by year. | `outputs/universe_summary.csv`, `outputs/report_ready/final_strategy_config.md` |
| Section 3: capacity filters | Minimum price, ADV20, volatility band, earnings window, and required data filters are stated; exclusion stock-days are exported by reason. | `outputs/eligibility_summary.csv`, `outputs/report_ready/final_strategy_config.md` |
| Section 3: implementation capacity | 5% ADV20 cap is enforced and audited through average exposure, cap-binding days, position size, and participation summaries. | `outputs/report_ready/position_capacity_summary.csv`, `outputs/positions_50m.parquet`, `outputs/positions_250m.parquet`, `outputs/positions_1b.parquet` |
| Section 4: borrow proxy | Borrow treatment is tiered cost rather than hard exclusion; tier rates, tier shares, and cost impact are reported. | `outputs/report_ready/borrow_proxy_methodology.md`, `outputs/report_ready/borrow_tier_summary.csv`, `outputs/report_ready/borrow_sharpe_degradation.csv` |
| Section 5: alpha target | Final target is risk-adjusted overnight return, not raw overnight return. | `outputs/report_ready/final_strategy_config.md`, `outputs/report_ready/final_strategy_selection_memo.md` |
| Section 5: feature groups | Final feature set is unchanged; feature formulas and observability are exported. | `outputs/report_ready/feature_inventory.csv`, `outputs/report_ready/feature_inventory.md` |
| Section 5: IC evidence | IC mean and t-stat are reported for baseline and final candidate, and by calendar year in the yearly table. | `outputs/report_ready/final_candidate_comparison.csv`, `outputs/report_ready/baseline_vs_candidate_yearly.csv` |
| Section 5: ablation | Final-strategy feature-group ablation is reported at 50M, 250M, and 1B, with the report emphasizing the 250M table. | `outputs/feature_ablation_summary.csv`, `outputs/report_ready/feature_ablation_audit.md` |
| Section 6: portfolio construction | Long/short top-bottom 3% baskets, minimum 15 names per side, equal side weighting, dollar neutrality, and cap clipping are documented. | `outputs/report_ready/final_strategy_config.md` |
| Section 6: cost model | Commission, auction slippage, and borrow costs are included; gross-to-net Sharpe degradation is decomposed. | `outputs/report_ready/borrow_sharpe_degradation.csv`, `outputs/performance_summary.csv` |
| Section 6: empirical results | Final 50M, 250M, and 1B performance is reported net of costs, with yearly and stress-window checks. | `outputs/performance_summary.csv`, `outputs/report_ready/baseline_vs_candidate_yearly.csv`, `outputs/report_ready/baseline_vs_candidate_stress_windows.csv` |
| Section 7: look-ahead scepticism | Report answers target, feature, earnings, short-interest, and data-cutoff look-ahead risks separately. | `outputs/report_ready/volatility_scaled_target_point_in_time_audit.md`, `outputs/report_ready/final_reproduction_log.md` |
| Section 7: statistical robustness | Report uses IC, yearly results, ablation, and stress windows rather than only headline Sharpe. | `outputs/report_ready/final_candidate_comparison.csv`, `outputs/feature_ablation_summary.csv`, `outputs/report_ready/baseline_vs_candidate_stress_windows.csv` |
| Section 7: execution honesty | Capacity cap and cost drag are presented as central limitations. | `outputs/report_ready/position_capacity_summary.csv`, `outputs/report_ready/borrow_sharpe_degradation.csv` |
| Section 7: borrow honesty | Borrow tier costs and the absence of external validation are both disclosed. | `outputs/report_ready/borrow_tier_summary.csv`, `outputs/report_ready/report_missing_items.md` |
| Section 7: reporting integrity | Baseline archived; final strategy frozen; reproduction and tests logged. | `outputs/baseline_archive/baseline_readme.md`, `outputs/report_ready/final_reproduction_log.md` |

## Appendix C. Frozen Output Manifest

The final report deliberately uses a narrow source set. The table below records how each source is used, so that the reported numbers can be traced without rerunning experiments.

| Frozen artifact | Use in report |
|---|---|
| `outputs/performance_summary.csv` | final headline performance by AUM, including net return, volatility, Sharpe, drawdown, turnover, exposure, and IC |
| `outputs/report_ready/final_strategy_config.md` | final strategy definition, target, universe, eligibility filters, basket rule, costs, borrow, cutoff, and seed |
| `outputs/report_ready/final_strategy_selection_memo.md` | promotion rationale and comparison logic for the final candidate |
| `outputs/report_ready/final_strategy_summary.md` | final-strategy summary language and headline context |
| `outputs/baseline_archive/baseline_readme.md` | original baseline preservation and baseline Sharpe disclosure |
| `outputs/report_ready/final_candidate_comparison.csv` | baseline versus final candidate comparison across AUM levels |
| `outputs/report_ready/baseline_vs_candidate_yearly.csv` | calendar-year performance and IC stability |
| `outputs/report_ready/baseline_vs_candidate_stress_windows.csv` | late 2018, 2020 Q1, and 2022 stress-window comparison |
| `outputs/report_ready/position_capacity_summary.csv` | average gross exposure, cap-binding days, per-name positions, participation, and capped position-days |
| `outputs/report_ready/borrow_sharpe_degradation.csv` | gross-to-net Sharpe degradation by commission, slippage, and borrow |
| `outputs/report_ready/borrow_tier_summary.csv` | short position-day counts, shares, notional, and borrow cost by tier |
| `outputs/report_ready/short_signal_affected_by_borrow.csv` | distinction between borrow cost impact and selection impact |
| `outputs/feature_ablation_summary.csv` | final-strategy feature-group ablation results |
| `outputs/report_ready/feature_ablation_audit.md` | explanation of ablation method and no-retuning control |
| `outputs/report_ready/feature_inventory.csv` | formula, data source, lag, and observability for features |
| `outputs/earnings_timing_examples.csv` | hand-checkable AMC, BMO, and same-day earnings examples |
| `outputs/short_interest_lag_examples.csv` | hand-checkable short-interest lag examples |
| `outputs/return_reconciliation_summary.csv` | adjusted price return reconciliation check |
| `outputs/universe_summary.csv` | annual universe size and year-start market-cap reference evidence |
| `outputs/eligibility_summary.csv` | exclusion stock-days by eligibility reason |
| `outputs/report_ready/final_reproduction_log.md` | Python version, commands, test result, final metrics, cutoff confirmation, baseline archive confirmation |
| `outputs/quantstats_250m.html` | final 250M tear sheet artifact |
| `outputs/report_ready/report_missing_items.md` | evidence limitations that are not filled with unsupported estimates |

The manifest also sets a boundary on the report. If a claim is not supported by one of these frozen files, it is either omitted or disclosed as unavailable. This is why the report does not include external borrow-fee validation or a new market-impact model at the participation cap.

## File Traceability

- Final strategy configuration: `outputs/report_ready/final_strategy_config.md`
- Final headline performance: `outputs/performance_summary.csv`
- Baseline archive note: `outputs/baseline_archive/baseline_readme.md`
- Final comparison: `outputs/report_ready/final_candidate_comparison.csv`
- Yearly comparison: `outputs/report_ready/baseline_vs_candidate_yearly.csv`
- Stress windows: `outputs/report_ready/baseline_vs_candidate_stress_windows.csv`
- Capacity summary: `outputs/report_ready/position_capacity_summary.csv`
- Borrow degradation: `outputs/report_ready/borrow_sharpe_degradation.csv`
- Borrow tiers: `outputs/report_ready/borrow_tier_summary.csv`
- Feature ablation: `outputs/feature_ablation_summary.csv`
- Timing audits: `outputs/earnings_timing_examples.csv`, `outputs/short_interest_lag_examples.csv`
- Reproducibility: `outputs/report_ready/final_reproduction_log.md`
- Missing evidence list: `outputs/report_ready/report_missing_items.md`

