# Corrected Final Report: Close-to-Open Overnight Equity Strategy

## Executive Summary

The final strategy is `phase2_g5_05_expanding`: a daily, dollar-neutral, close-to-open long-short strategy using a volatility-scaled overnight-return target and expanding-window transparent feature-weight estimation.

The target is:

```text
overnight_next / (vol20 / sqrt(252))
```

`overnight_next` is the close-to-next-open return being predicted and traded. `vol20` is trailing 20-day close-to-close volatility, annualised, and shifted by one trading day before use. The final strategy uses the unchanged feature set, top/bottom 3% baskets, equal weighting, raw alpha-score ranking, tiered borrow-cost treatment, fixed transaction costs, 5% ADV20 participation cap, and close-to-open execution.

At the main headline AUM of 250M, the final strategy earns **7.31%** net annual return, **4.97%** net volatility, net Sharpe **1.445**, and max drawdown **-10.19%** over 2010-2024. The previous champion Sharpe of **0.811** is retained only as an archived comparison.

The promotion evidence is controlled: validation 2019-2022 250M Sharpe is **2.279**, internal holdout 2023-2024 Sharpe is **0.620**, and full 2010-2024 Sharpe is **1.445**. The holdout Sharpe is much lower than the validation Sharpe; this is disclosed as expected performance degradation, not hidden.

2025-2026 remains held out for marker evaluation. No 2025+ data is used in the development outputs or in this report.

## Coursework Question Map

The brief contains **24 explicit report questions** across Sections 2-6:

| Brief section   | Topic                   |   Explicit questions | Where answered here                                                                                |
|:----------------|:------------------------|---------------------:|:---------------------------------------------------------------------------------------------------|
| Section 2       | Daily panel questions   |                    6 | Data sources, return identity, earnings timing, short-interest lag, universe, return decomposition |
| Section 3       | Capacity-aware universe |                    4 | Thresholds, participation cap, AUM capacity, binding constraints                                   |
| Section 4       | Borrow filtering        |                    4 | Borrow proxy, validation limitation, tiered cost treatment, gross-to-net borrow impact             |
| Section 5       | Alpha model             |                    5 | Information set, target, model/training, IC, ablation, weak periods                                |
| Section 6       | Portfolio and costs     |                    5 | Basket/weighting/turnover, 50M/250M/1B performance, cost drag, QuantStats, stress windows          |

Section 7 adds sceptical-marker audit questions rather than a separate numbered deliverable list. This report answers those by tying look-ahead, capacity, borrow, robustness, and cost claims to frozen output files.

Detailed checklist of the 24 explicit Section 2-6 questions:

| Brief item | Direct answer/evidence in this report |
|:--|:--|
| S2.1 data source, window, survivorship | Provided coursework daily panel, 2010-2024 development window, year-start large-cap universe frozen from prior information. |
| S2.2 return reconciliation | Adjusted open/close identity checked on 5,469,968 stock-days; tolerance 1e-08; zero failures. |
| S2.3 earnings timing | BMO/AMC/Same-Day timing rules are shifted to the trader clock and audited on named examples. |
| S2.4 short-interest construction | `dsi`, `dtcn`, and `ddtcn` are shifted one trading day for decision use; representative HLT series is plotted. |
| S2.5 universe evolution | Year-start counts and mid-year exits are reported in the universe table. |
| S2.6 stylised fact | Equal-weight universe decomposition is plotted and quantified by year; close-to-close is larger cumulatively, while overnight has higher Sharpe than intraday. |
| S3.1 eligibility thresholds | Dollar volume, market cap, price, volatility, and earnings-window thresholds are listed with numeric justifications. |
| S3.2 participation cap and slippage | 5% ADV20 cap is used; impact examples quantify mid-cap and large-cap trade sizes under the square-root diagnostic. |
| S3.3 eligible set by AUM | 50M, 250M, and 1B capacity summaries are reported. |
| S3.4 binding constraints | Binding exclusion reasons are summarised by year and capacity diagnostics. |
| S4.1 borrow proxy | Hard-to-borrow proxy uses lagged short-interest stress tiers from `dsi`, `dtcn`, and `ddtcn`. |
| S4.2 external borrow validation | GME 2020-2021 and CVNA 2023 public crowded-short episodes are compared to internal proxy tiers. |
| S4.3 hard exclusion or tiered cost | Final strategy uses tiered borrow cost, not hard exclusion; affected short-signal fractions are reported. |
| S4.4 borrow impact | Gross, post-commission, post-slippage, and net-of-borrow Sharpe degradation are tabulated. |
| S5.1 information set and target | 15:50 ET information set, volatility-scaled overnight target, and line-by-line feature formulas are listed. |
| S5.2 model class and training | Transparent linear rank-score model with expanding-window annual re-estimation is justified. |
| S5.3 Information Coefficient | Daily, yearly, rolling, and regime IC diagnostics are reported. |
| S5.4 ablation | Feature-group ablation shows marginal contribution without single-feature collapse. |
| S5.5 weak regimes | 2010, late 2018, 2024, and lower 2023-2024 holdout performance are discussed. |
| S6.1 basket and turnover | Top/bottom 3% equal-weight dollar-neutral baskets and average turnover are reported. |
| S6.2 headline performance | 50M, 250M, and 1B costed performance table is reported for 2010-2024. |
| S6.3 gross-to-net degradation | Commission, slippage, and borrow Sharpe drags are decomposed. |
| S6.4 QuantStats tear-sheet | 250M QuantStats HTML is generated from the notebook outputs and included in the package. |
| S6.5 stress windows | Late 2018, 2020 Q1, and 2022 drawdown stress windows are reported. |

## 1. Return Objects And The Stylised Fact

The daily return identity is:

```text
(1 + r_overnight,t) * (1 + r_intraday,t) - 1 = close_t / close_(t-1) - 1
```

The project reconciles adjusted open, adjusted close, and close-to-close returns with tolerance `1e-08`. It checks `5,469,968` stock-days, with `0` failures and fail fraction `0.000000`.

The equal-weight eligible-universe decomposition is below. It supports the overnight-versus-intraday motivation, but it does **not** support the stronger claim that overnight is larger than total close-to-close return in this implementation. In our equal-weight universe, close-to-close/total has the largest cumulative return; overnight has a stronger Sharpe than intraday.

| Stream                 | Cumulative return   | Annual return   | Annual vol   |   Sharpe |
|:-----------------------|:--------------------|:----------------|:-------------|---------:|
| Overnight              | 297.90%             | 9.66%           | 11.75%       |    0.822 |
| Intraday               | 94.79%              | 4.55%           | 14.78%       |    0.308 |
| Close-to-close / total | 647.02%             | 14.37%          | 19.43%       |    0.74  |

![Equal-weight eligible-universe overnight/intraday/close-to-close decomposition, 2010-2024, no AUM, no strategy costs, annual large-cap universe](outputs/report_ready/return_decomposition_q1.png){ width=92% }

Year-by-year decomposition:

|   Year | Overnight   | Intraday   | Close-to-close   |   Names avg |
|-------:|:------------|:-----------|:-----------------|------------:|
|   2010 | 9.79%       | 16.05%     | 26.98%           |         986 |
|   2011 | 5.85%       | -3.61%     | 1.76%            |         986 |
|   2012 | 3.93%       | 16.36%     | 20.71%           |         988 |
|   2013 | 13.69%      | 22.09%     | 38.55%           |         988 |
|   2014 | 10.12%      | 2.41%      | 12.57%           |         987 |
|   2015 | -1.52%      | 0.55%      | -1.22%           |         986 |
|   2016 | -1.71%      | 21.59%     | 19.30%           |         987 |
|   2017 | 15.13%      | 4.96%      | 20.70%           |         988 |
|   2018 | 12.15%      | -17.76%    | -7.95%           |         988 |
|   2019 | 12.47%      | 15.52%     | 29.77%           |         988 |
|   2020 | 24.74%      | -3.04%     | 20.31%           |         989 |
|   2021 | 29.61%      | -1.40%     | 27.43%           |         990 |
|   2022 | -10.50%     | -2.61%     | -13.08%          |         988 |
|   2023 | 6.41%       | 12.04%     | 18.83%           |         988 |
|   2024 | 21.57%      | -5.89%     | 14.14%           |         989 |

## 2. Data Source, Panel Construction, And Timing

The data source is the provided coursework data package in `data/`, using daily OHLCV, market capitalisation, daily fundamentals, earnings timing, short-interest proxies, regime labels, and SP500 total-return benchmark files. The development window is 2010-01-01 through 2024-12-31.

Open, high, low, and close are adjusted consistently by the adjusted-close ratio before return construction. The strategy uses:

- `r_overnight = adj_open_t / adj_close_(t-1) - 1`
- `r_intraday = adj_close_t / adj_open_t - 1`
- `overnight_next = adj_open_(t+1) / adj_close_t - 1`

The annual universe is frozen at each year start from the top available market-cap names using only the prior year-end reference date. The output universe is close to 1,000 names each year because the source data has slightly fewer valid names in early years.

|   Year |   Universe count | Reference date   | Median year-start market cap   |   Mid-year exits |
|-------:|-----------------:|:-----------------|:-------------------------------|-----------------:|
|   2010 |              986 | 2009-12-31       | $2457.84M                      |                0 |
|   2011 |              986 | 2010-12-31       | $3250.24M                      |                0 |
|   2012 |              988 | 2011-12-30       | $3247.62M                      |                0 |
|   2013 |              988 | 2012-12-31       | $3860.83M                      |                0 |
|   2014 |              987 | 2013-12-31       | $5421.07M                      |                0 |
|   2015 |              986 | 2014-12-31       | $6065.73M                      |                0 |
|   2016 |              987 | 2015-12-31       | $6059.59M                      |                0 |
|   2017 |              988 | 2016-12-30       | $7065.93M                      |                0 |
|   2018 |              988 | 2017-12-29       | $8728.87M                      |                0 |
|   2019 |              988 | 2018-12-31       | $7474.18M                      |                0 |
|   2020 |              989 | 2019-12-31       | $9622.86M                      |                0 |
|   2021 |              990 | 2020-12-31       | $11618.99M                     |                0 |
|   2022 |              988 | 2021-12-31       | $14160.49M                     |                0 |
|   2023 |              988 | 2022-12-30       | $11498.14M                     |                0 |
|   2024 |              989 | 2023-12-29       | $13055.11M                     |                0 |

Earnings timing uses `earnings_calendar.strat_trading_date`. The eligibility filter excludes plus/minus one trading day around the strategy trading date. Existing hand-checkable examples include MOS as an AMC example and RPM as a BMO example in `outputs/earnings_timing_examples.csv`.

Short-interest fields `dsi`, `dtcn`, and `ddtcn` are treated as provided point-in-time transformed proxies from the coursework data package, then shifted by one additional trading day before decision use. The report does not claim independent reconstruction of raw FINRA settlement/publication dates because those raw inputs are not present.

The representative series below shows HLT's decision-lagged short-interest proxies. The figure is a timing diagnostic, not a strategy return chart; it confirms that the report is using the same lag convention as the feature and borrow-tier pipeline.

![Representative short-interest proxy series; HLT, 2015-2024, provided point-in-time proxies plus one-trading-day decision lag, no AUM, no portfolio cost assumption](outputs/report_ready/short_interest_representative_series.png){ width=92% }

## 3. Capacity-Aware Universe

The implementation thresholds are:

- Annual universe: top available US common equities by year-start market capitalisation, target size 1,000.
- Minimum history: 252 price observations.
- Minimum price: $5.
- Minimum ADV20: $10,000,000.
- Volatility band: 5% to 120% annualised trailing `vol20`.
- Earnings exclusion: plus/minus one trading day around `strat_trading_date`.
- Participation cap: 5% of ADV20.

The fixed brief cost model charges auction slippage directly as 1.5 bps per leg. The code does not introduce a separate square-root impact model into performance. Capacity is therefore evidenced by realised gross exposure, participation rate, and cap-binding frequency rather than by changing the cost schedule.

For scale, the table below computes the brief-style square-root impact estimate at the fixed 5% ADV20 cap for one typical mid-cap and one typical large-cap name in the final eligible universe. It uses `0.7 * sigma_daily * sqrt(0.05)` and is reported only as an impact diagnostic; realised performance still uses the fixed 0.5 bps commission per leg and 1.5 bps auction slippage per leg.

| Example           | Date       | Ticker   | Market cap   | ADV20    | Vol20   | Daily sigma   | Participation   |   Impact bps |
|:------------------|:-----------|:---------|:-------------|:---------|:--------|:--------------|:----------------|-------------:|
| typical_mid_cap   | 2024-12-31 | EXE      | $23072.69M   | $220.57M | 18.69%  | 1.18%         | 5.00%           |        18.43 |
| typical_large_cap | 2024-12-31 | FISV     | $115856.88M  | $492.70M | 9.79%   | 0.62%         | 5.00%           |         9.65 |

| AUM   | Avg gross exposure   | Avg abs position   | Max abs position   | Avg participation   | Position-days at cap   |
|:------|:---------------------|:-------------------|:-------------------|:--------------------|:-----------------------|
| 50M   | 99.92%               | $1.00M             | $7.40M             | 2.04%               | 16.16%                 |
| 250M  | 74.97%               | $3.76M             | $98.01M            | 4.02%               | 66.29%                 |
| 1B    | 25.35%               | $5.09M             | $393.90M           | 4.29%               | 75.40%                 |

![Capacity by AUM for final top/bottom 3% equal-weight strategy, 50M/250M/1B, fixed 5% ADV20 cap, full commission/slippage/borrow schedule](outputs/report_ready/corrected_report_capacity.png){ width=75% }

The 1B case is a capacity boundary case. Its average gross exposure is only **25.35%**, so the strategy cannot deploy target risk under the fixed 5% ADV20 cap. This is evidence of backtest honesty, not a bug. The final report should not imply that the basket expands to solve 1B capacity; it does not.

Binding eligibility reasons by year are:

|   Year |     OK |   MCAP_FAIL |   ADV_FAIL |   PRICE_FAIL |   VOL_FAIL |   EARN_WINDOW |   DATA_FAIL |
|-------:|-------:|------------:|-----------:|-------------:|-----------:|--------------:|------------:|
|   2010 | 154218 |       46003 |      96974 |         5995 |        307 |          2066 |           0 |
|   2011 | 165277 |       52286 |      84995 |         5303 |        355 |          3629 |           0 |
|   2012 | 165866 |       59329 |      82506 |         4103 |        661 |          3364 |           0 |
|   2013 | 184151 |       69941 |      67903 |         2766 |        392 |          3339 |           0 |
|   2014 | 204266 |       82144 |      47834 |         1369 |        915 |          4672 |           0 |
|   2015 | 211190 |       93048 |      38791 |         1350 |        326 |          7901 |           0 |
|   2016 | 218103 |      101424 |      30514 |         1115 |        905 |          8417 |           0 |
|   2017 | 223058 |      110866 |      23282 |          977 |       1372 |          8837 |           0 |
|   2018 | 234750 |      119731 |      12302 |          344 |        537 |          9592 |           0 |
|   2019 | 236744 |      127586 |      10527 |          915 |        468 |          9887 |           0 |
|   2020 | 226493 |      134223 |       9139 |         1386 |      12078 |          9976 |           0 |
|   2021 | 243163 |      143615 |       2723 |           48 |        811 |         10799 |           0 |
|   2022 | 242388 |      148362 |       2717 |           13 |       1332 |         11076 |           0 |
|   2023 | 241675 |      151095 |       2026 |          623 |        693 |         11465 |           0 |
|   2024 | 242803 |      156668 |       1034 |            0 |       1306 |         11905 |        1000 |

## 4. Borrow Proxy And Short Leg

The borrow proxy uses lagged short-interest stress variables available in the prepared point-in-time panel. Borrow tiers are charged as:

- Tier A: 40 bps p.a.
- Tier B: 200 bps p.a.
- Tier C: 800 bps p.a.
- Daily borrow charge: annual rate / 252.

The final strategy applies tiered borrow cost only. It does not hard-exclude Tier B/C shorts. Therefore borrow affects net performance through explicit costs, not through selected-name changes.

At 250M, borrow tier exposure and cost are:

| Tier   | Share of short position-days   | Avg short notional   | Total borrow cost   |
|:-------|:-------------------------------|:---------------------|:--------------------|
| A      | 43.21%                         | $4.35M               | $2,807,163          |
| B      | 38.25%                         | $3.57M               | $10,188,096         |
| C      | 18.54%                         | $2.78M               | $15,382,819         |

The fraction of selected short position-days in Tier B or C is **56.79%**. The fraction of raw short signal changed by borrow treatment is **0.00%**, because tiered costs do not alter raw short selection.

The report does not use a complete prime-broker borrow-fee, locate-rate, or securities-lending history. That is a limitation. To avoid leaving the borrow proxy totally unanchored, I added two anecdotal external checks for names that are present in the coursework panel. They are not a statistical validation, but they do check whether the proxy catches public crowded-short episodes.

| Ticker   | Window                   | External anecdote                                                                                                                                                                                          |   Mean DSI |   Max DSI |   Mean DTCN |   Max DTCN | Tier B/C days   | Tier C days   | Internal read                                                         |
|:---------|:-------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------:|----------:|------------:|-----------:|:----------------|:--------------|:----------------------------------------------------------------------|
| GME      | 2020-12-01 to 2021-02-15 | SEC staff report: GME short interest was around 100% of public float through most of 2020, reached 109.26% on 2020-12-31, and borrow fees were around 25% in January 2021 after exceeding 100% in Q2 2020. |      0.938 |     1.035 |       5.538 |     10.134 | 100.00%         | 100.00%       | Proxy flags the anecdotal crowded-short window as high borrow stress. |
| CVNA     | 2023-05-01 to 2023-07-31 | Reuters reported a May 2023 Carvana short-squeeze episode: the stock rose as much as 55%, short positions were about $488m, and Ortex described short sellers adding buy pressure while covering.          |      0.247 |     0.259 |       2.051 |      5.727 | 100.00%         | 100.00%       | Proxy flags the anecdotal crowded-short window as high borrow stress. |

Sources used for the anecdotal checks are the SEC staff report on early-2021 equity/options market structure for GME and a Reuters report on the May-2023 CVNA short-squeeze episode, available respectively at `https://www.sec.gov/files/staff-report-equity-options-market-struction-conditions-early-2021.pdf` and `https://www.investing.com/news/stock-market-news/usedcar-retailer-carvanas-shares-soar-on-upbeat-secondquarter-forecast-3074273`. The internal result is directionally sensible: both public crowded-short windows are classified as Tier C on 100% of local panel days. The limitation remains that this is a small sanity check, not a full external borrow-fee tape.

For the brief's high-short-interest honesty check, names with decision-lagged `dsi > 10%` account for the following gross-return contribution on the selected short leg:

| AUM   | DSI > 10% short-days   |   Total gross contribution bps |   Avg daily contribution bps | Share of all gross PnL   |
|:------|:-----------------------|-------------------------------:|-----------------------------:|:-------------------------|
| 50M   | 12.97%                 |                       1289.54  |                        0.342 | 4.84%                    |
| 250M  | 12.97%                 |                       1683.25  |                        0.446 | 7.25%                    |
| 1B    | 12.97%                 |                        579.371 |                        0.154 | 6.16%                    |

As a sensitivity, the audit re-runs the final selection while excluding `dsi > 10%` names from the short leg only. This is not promoted as a new strategy and does not alter the submitted final outputs. It keeps the same target, top/bottom 3% basket rule, equal weighting, 5% ADV20 cap, close-to-open execution, commission, slippage, and tiered borrow rates.

| AUM   |   Final Sharpe |   DSI>10 excluded Sharpe | Final return   | DSI>10 excluded return   | Final max DD   | DSI>10 excluded max DD   | Final gross exposure   | DSI>10 excluded gross exposure   |
|:------|---------------:|-------------------------:|:---------------|:-------------------------|:---------------|:-------------------------|:-----------------------|:---------------------------------|
| 50M   |          1.308 |                    1.149 | 6.66%          | 5.72%                    | -13.82%        | -14.33%                  | 99.92%                 | 99.91%                           |
| 250M  |          1.445 |                    1.24  | 7.31%          | 5.98%                    | -10.19%        | -10.43%                  | 74.97%                 | 75.71%                           |
| 1B    |          1.293 |                    1.125 | 3.50%          | 2.89%                    | -5.56%         | -5.63%                   | 25.35%                 | 25.31%                           |

## 5. Alpha, Training, And Point-In-Time Controls

The final trading model is **not LightGBM**. The final model used to create submitted positions is a transparent expanding-window linear rank-score model. LightGBM, HistGradientBoosting, and other model families appear only as diagnostic or robustness comparisons.

| Item                         | Final report value                                                                            |
|:-----------------------------|:----------------------------------------------------------------------------------------------|
| Final model used for trading | Transparent expanding-window linear rank-score model                                          |
| Not the final model          | LightGBM and HistGradientBoosting; included only as diagnostics and robustness evidence       |
| Score formula                | `alpha_score_t,i = sum_j weight_{Y,j} * rank_feature_{t,i,j}`                                 |
| Training target              | `overnight_next / (vol20 / sqrt(252))`                                                        |
| Target use                   | Future overnight return is used only as a historical training label                           |
| Feature transform            | Cross-sectional ranks within the decision-date available universe                             |
| Weight estimation            | 50% fixed prior weights plus 50% learned feature-target correlation weights                   |
| Training window              | Expanding window: for scored year `Y`, train only on dates strictly before `Y`                |
| Prediction timing            | Features observable by 15:50 ET on day `t`; no year being scored or future years in training  |
| Portfolio mapping            | Long top 3% and short bottom 3% by alpha score; equal weight before capacity sizing           |
| Capacity/costs               | 5% ADV20 cap, day-t close entry, day-t+1 open exit, fixed commission/slippage/borrow schedule |

### 5.1 Feature Design And Information Set

The information set at decision time is data observable by 15:50 ET on day `t`. The final feature set is unchanged from the baseline and is stored as ranked features such as return/reversal, lagged intraday return, trailing volatility/liquidity/size, lagged fundamentals, lagged earnings/revision variables, lagged short-interest stress variables, and lagged industry return.

Line-by-line feature inventory used by the final score:

- `rank_r_on_1d`: r_overnight = adj_open_t / adj_close_{t-1} - 1; source `prices.parquet: adjusted open, adjusted close`; lag `0 trading days; Open_t is known after the 09:30 auction`; 15:50 ET observable: Yes.
- `rank_r_on_5d`: rolling mean of r_overnight over 5 sessions, min_periods=3; source `prices.parquet: adjusted open, adjusted close`; lag `0 trading days; uses overnight returns available by 15:50 ET`; 15:50 ET observable: Yes.
- `rank_r_id_1d`: r_intraday_{t-1} = adj_close_{t-1} / adj_open_{t-1} - 1; source `prices.parquet: adjusted open, adjusted close`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_ret_cc_5d`: adj_close_{t-1} / adj_close_{t-6} - 1; source `prices.parquet: adjusted close`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_ret_cc_20d`: adj_close_{t-1} / adj_close_{t-21} - 1; source `prices.parquet: adjusted close`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_ret_cc_60d`: adj_close_{t-1} / adj_close_{t-61} - 1; source `prices.parquet: adjusted close`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_vol20`: annualised rolling std of close-to-close returns over 20 sessions, shifted 1 day; source `prices.parquet: adjusted close`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_vol60`: annualised rolling std of close-to-close returns over 60 sessions, shifted 1 day; source `prices.parquet: adjusted close`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_amihud20`: rolling mean over 20 sessions of abs(r_close_close) / dollar_volume, shifted 1 day; source `prices.parquet: adjusted close, volume`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_adv20_log`: log(1 + trailing 20-day average dollar volume), shifted 1 day; source `prices.parquet: adjusted close, volume`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_market_cap_log`: log(1 + market_cap_{t-1}); source `prices.parquet: market_cap`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_piot_norm_lag1`: piot_norm_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_gross_profit_margin_lag1`: gross_profit_margin_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_asset_turnover_ratio_lag1`: asset_turnover_ratio_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_net_debt_to_equity_lag1`: net_debt_to_equity_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_price_to_book_lag1`: price_to_book_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_ev_to_ebit_lag1`: ev_to_ebit_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_sue_lag1`: sue_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_deps_lag1`: deps_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_reps1_lag1`: reps1_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_repsf4_lag1`: repsf4_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_final_score_lag1`: final_score_{t-1}; source `cheapness_scores.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_score_velocity_lag1`: score_velocity_{t-1}; source `cheapness_scores.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_momentum_score_lag1`: momentum_score_{t-1}; source `cheapness_scores.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.
- `rank_dsi_lag1`: dsi_{t-1}; daily short-interest proxy after publication/vendor lag already in source; source `all_data.parquet`; lag `1 trading day after source availability`; 15:50 ET observable: Yes, if source obeys Section 2.1.3 lag convention.
- `rank_dtcn_lag1`: dtcn_{t-1}; daily days-to-cover proxy after publication/vendor lag already in source; source `all_data.parquet`; lag `1 trading day after source availability`; 15:50 ET observable: Yes, if source obeys Section 2.1.3 lag convention.
- `rank_ddtcn_lag1`: ddtcn_{t-1}; lagged change/stress proxy after publication/vendor lag already in source; source `all_data.parquet`; lag `1 trading day after source availability`; 15:50 ET observable: Yes, if source obeys Section 2.1.3 lag convention.
- `rank_industry_return_lag1`: industry_return_{t-1}; source `all_data.parquet`; lag `1 trading day`; 15:50 ET observable: Yes.

### 5.2 Model Class: Linear Combination

The alpha score is a linear combination of the rank features. For each scored year `Y`, the model estimates one deterministic weight vector using only dates before `Y`; the same weights then score every eligible stock-day in year `Y`:

```text
alpha_score_t,i = sum_j weight_Y,j * rank_feature_t,i,j
```

Important timing rules:

- The target uses future overnight return only as a historical training label.
- `vol20` in the target denominator is trailing and shifted.
- Day-`t` close/high/low cannot enter decision-time features unless shifted appropriately.
- Earnings timing uses `strat_trading_date` and respects BMO/AMC handling.
- Cross-sectional ranks are computed within the same available decision-date cross-section.
- For scored year `Y`, expanding-window training uses dates from 2010-01-01 through the day before year `Y` starts. The scored year and future years are not used.

The final alpha score is intentionally transparent: 50% prior feature weights and 50% learned correlation weights against the volatility-scaled target. Expanding-window training uses more historical overnight evidence as time progresses, stabilising the transparent weight estimates versus a fixed 4-year rolling window. The improvement is not from lower costs, lower borrow rates, relaxed caps, new data, or intraday inputs.

The latest-year weight chart shows the economic shape of the model. Return/reversal features carry the largest absolute weights, while volatility, liquidity, fundamentals, earnings, short-interest, and industry features mainly adjust risk, capacity, crowding, or regime exposure around that core signal.

![Largest 2024 final linear score feature weights, transparent expanding-window model, same feature set, no LightGBM portfolio promotion](outputs/report_ready/model_feature_weights_2024.png){ width=88% }

Final full-sample IC is **0.029** with t-stat **9.934**.

### 5.3 Machine Learning Benchmark: LightGBM

LightGBM was first run as an optional IC diagnostic to check the same data panel for nonlinear signal. It is not the final strategy. The table is ordered with the final transparent model first, then the LightGBM diagnostic rows.

| Model                                           | Period                     | Train rows   | Test rows   |   IC days |   IC mean |   IC t-stat | Notes                                                                |
|:------------------------------------------------|:---------------------------|:-------------|:------------|----------:|----------:|------------:|:---------------------------------------------------------------------|
| Final transparent expanding-window linear score | internal_holdout_2023_2024 |              | 484,478     |       502 |     0.019 |       2.421 | Reference final score IC over the same test period.                  |
| Final transparent expanding-window linear score | validation_2019_2022       |              | 948,788     |      1008 |     0.02  |       3.336 | Reference final score IC over the same test period.                  |
| LightGBM                                        | internal_holdout_2023_2024 | 2,709,667    | 484,478     |       502 |     0.02  |       3.161 | Diagnostic only; fixed parameters; no portfolio promotion or tuning. |
| LightGBM                                        | validation_2019_2022       | 1,760,879    | 948,788     |      1008 |     0.029 |       6.288 | Diagnostic only; fixed parameters; no portfolio promotion or tuning. |

![Final linear score versus LightGBM diagnostic IC, validation and internal holdout, same data panel and cutoff, LightGBM not promoted as a costed strategy](outputs/report_ready/model_ic_comparison.png){ width=78% }

Interpretation: LightGBM's positive IC in both validation and internal holdout supports that the panel contains real predictive signal. It does not by itself promote a LightGBM trading rule, because model-family promotion requires a separate audit beyond this diagnostic.

### 5.4 Model-Family Robustness Screen

After the main champion-challenger selection, I ran a limited model-family robustness screen using the same point-in-time features, volatility-scaled overnight target, annual expanding walk-forward protocol, top/bottom 3% baskets, equal weighting, tiered borrow costs, fixed transaction costs, 5% ADV20 cap, and close-to-open execution. The screen compared the submitted expanding linear rank-score model with regularised linear models and nonlinear tree/boosting models.

| Model | Validation 2019-2022 250M Sharpe | Internal holdout 2023-2024 250M Sharpe | Full 2010-2024 250M Sharpe |
|:------|----------------------------------:|----------------------------------------:|----------------------------:|
| Expanding linear ranking model | 2.279 | 0.620 | 1.445 |
| LightGBM | 6.095 | 5.281 | 5.096 |
| HistGradientBoosting | 6.054 | 6.362 | 5.248 |

These results show that the feature set contains nonlinear predictive structure. However, I did not replace the submitted strategy with these models. The nonlinear benchmarks were introduced after the main champion-challenger selection as a limited robustness screen. Although their validation and internal-holdout Sharpe ratios are strong, the magnitude of the improvement itself calls for additional audit work, including leakage checks, hyperparameter stability, turnover analysis, feature attribution, and implementation-risk review.

The nonlinear models are therefore kept as robustness evidence and future work rather than as the submitted final strategy. A dedicated nonlinear promotion audit would be required before replacing the final trading rule. The submitted final strategy prioritises auditability, feature-level transparency, a fully validated point-in-time pipeline, and a complete cost, capacity, borrow, and reproduction trail. This is especially important because the coursework marker evaluates 2025-2026 as held-out data, so the final strategy should not overfit to an unaudited high-capacity challenger.

### 5.5 IC Stability And Weak Regimes

The information coefficient is the Spearman rank correlation between the alpha score and the subsequent overnight return. The full-sample mean IC is modest, as expected for cross-sectional equity prediction, but statistically reliable over many stock-days and trading days. Yearly IC is not stable: 2010 and 2022 are negative, while 2024 is close to zero. This is why the report treats the 2023-2024 holdout as positive but much weaker than validation, rather than overclaiming live persistence.

![63-day rolling IC for the final linear score, Spearman correlation between alpha score and subsequent overnight return, 2010-2024](outputs/figures/rolling_ic.png){ width=84% }

![Final linear score mean IC by calendar year, 2010-2024, negative years highlighted](outputs/report_ready/model_yearly_ic.png){ width=84% }

## 6. Feature Ablation

Feature-group ablation is a dependence audit, not retuning. Return/reversal is the core alpha contributor: removing it lowers 250M Sharpe from **1.445** to **-1.114** and produces a negative net annual return.

Some removals improve Sharpe in the frozen no-retuning table, especially short-interest/borrow-stress and earnings/revision. This should not be hidden. It means those variables may act as risk, capacity, cost, or crowding controls rather than pure alpha predictors, and ablation improvement does not automatically imply the removed group is useless.

| Variant                             | Removed group                |   IC mean |   IC t-stat | Net annual return   | Net vol   |   Net Sharpe | Max drawdown   |
|:------------------------------------|:-----------------------------|----------:|------------:|:--------------------|:----------|-------------:|:---------------|
| full_model                          | none                         |     0.029 |       9.934 | 7.31%               | 4.97%     |        1.445 | -10.19%        |
| remove_return/reversal              | return/reversal              |     0.011 |       3.333 | -3.62%              | 3.26%     |       -1.114 | -46.66%        |
| remove_risk/liquidity/size          | risk/liquidity/size          |     0.028 |      10.863 | 5.89%               | 5.12%     |        1.144 | -8.24%         |
| remove_fundamental/value/quality    | fundamental/value/quality    |     0.03  |      10.203 | 7.01%               | 4.90%     |        1.407 | -9.75%         |
| remove_earnings/revision            | earnings/revision            |     0.028 |       9.754 | 7.31%               | 4.86%     |        1.477 | -10.19%        |
| remove_short-interest/borrow-stress | short-interest/borrow-stress |     0.029 |       9.846 | 7.70%               | 5.00%     |        1.508 | -11.32%        |
| remove_industry-return              | industry-return              |     0.029 |       9.942 | 7.27%               | 4.96%     |        1.442 | -10.19%        |

![Feature-group ablation at 250M for final top/bottom 3% equal-weight strategy, fixed 5% ADV20 cap and full cost schedule](outputs/report_ready/corrected_report_ablation.png){ width=85% }

## 7. Portfolio Construction And Costs

The portfolio takes the top 3% of eligible names as longs and bottom 3% as shorts, with at least 15 names per side. It uses equal weighting within each side before capacity scaling. Dollar neutrality is enforced after capacity sizing; if selected names cannot absorb target notional under the 5% ADV20 cap, gross exposure is reduced rather than relaxing the cap.

| AUM   | Net annual return   | Net vol   |   Net Sharpe | Max drawdown   |   Gross Sharpe |   Avg turnover | Avg gross exposure   |   Cap-binding days |
|:------|:--------------------|:----------|-------------:|:---------------|---------------:|---------------:|:---------------------|-------------------:|
| 50M   | 6.66%               | 5.03%     |        1.308 | -13.82%        |          3.539 |          1.998 | 99.92%               |               3547 |
| 250M  | 7.31%               | 4.97%     |        1.445 | -10.19%        |          3.112 |          1.499 | 74.97%               |               3773 |
| 1B    | 3.50%               | 2.69%     |        1.293 | -5.56%         |          2.321 |          0.507 | 25.35%               |               3773 |

![Final net cumulative returns by AUM, 50M/250M/1B, final top/bottom 3% equal-weight strategy, fixed 5% ADV20 cap and full commission/slippage/borrow schedule](outputs/report_ready/corrected_report_aum_cumulative_returns.png){ width=90% }

The gross-to-net Sharpe degradation is:

| AUM   |   Gross Sharpe |   Commission drag |   Slippage drag |   Borrow drag |   Net Sharpe |   Avg daily borrow bps |
|:------|---------------:|------------------:|----------------:|--------------:|-------------:|-----------------------:|
| 50M   |          3.539 |             0.501 |           1.503 |         0.227 |        1.308 |                  0.451 |
| 250M  |          3.112 |             0.378 |           1.137 |         0.152 |        1.445 |                  0.301 |
| 1B    |          2.321 |             0.233 |           0.704 |         0.091 |        1.293 |                  0.098 |

These drag values are Sharpe-unit drags, not percentages. Auction slippage is the largest explicit drag.

The QuantStats tear-sheet for the 250M strategy is `outputs/quantstats_250m.html`.

## 8. Robustness And Weak Periods

250M year-by-year results:

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

Pre/post split:

|    Window | Return   | Vol   |   Sharpe | Max drawdown   | Avg gross exposure   |
|----------:|:---------|:------|---------:|:---------------|:---------------------|
| 2010_2016 | 4.42%    | 3.45% |    1.273 | -10.19%        | 60.48%               |
| 2017_2024 | 9.90%    | 5.99% |    1.608 | -7.64%         | 87.66%               |

Stress windows:

| Window        | Return   | Vol    |   Sharpe | Max drawdown   | Avg gross exposure   |
|:--------------|:---------|:-------|---------:|:---------------|:---------------------|
| late_2018     | -2.35%   | 4.71%  |   -0.482 | -1.92%         | 85.28%               |
| 2020_q1       | 34.41%   | 10.78% |    2.799 | -4.14%         | 88.95%               |
| 2022_drawdown | 32.24%   | 8.02%  |    3.525 | -2.63%         | 99.23%               |

Tail diagnostics at 250M:

- Worst 3-month return: **-4.46%**.
- Worst 6-month return: **-7.31%**.
- Worst 12-month return: **-10.09%**.
- Top 5% best days contribute **1.461** times total PnL.
- Lag-1 return autocorrelation is **-0.007**.

The Lo-style serial-correlation diagnostic below uses autocorrelation weights through lag 5. It is a diagnostic adjustment, not a replacement for the main reported Sharpe. For 250M, the adjusted Sharpe is slightly lower than the raw Sharpe because the weighted higher-lag autocorrelation variance multiplier is above one.

| AUM   |   Raw net Sharpe |   Lo-adjusted net Sharpe |   Variance multiplier |   Lag-1 autocorr |
|:------|-----------------:|-------------------------:|----------------------:|-----------------:|
| 50M   |            1.308 |                    1.3   |                 1.012 |           -0.014 |
| 250M  |            1.445 |                    1.423 |                 1.032 |           -0.007 |
| 1B    |            1.293 |                    1.254 |                 1.063 |           -0.011 |

The weak periods are visible: 2010 is strongly negative, late 2018 is negative, and 2024 is negative. This is consistent with the lower 2023-2024 holdout Sharpe.

## 9. Promotion Audit And Baselines

The selected Phase 2 challenger improves validation Sharpe, remains positive in holdout, improves full-period Sharpe, and does not worsen full-period max drawdown.

| Metric | Previous champion | Promoted final |
|---|---:|---:|
| Validation 2019-2022 250M Sharpe | 1.107 | 2.279 |
| Internal holdout 2023-2024 250M Sharpe | 0.003 | 0.620 |
| Full 2010-2024 250M Sharpe | 0.811 | 1.445 |
| Full 2010-2024 max drawdown | -10.19% | -10.19% |
| Full 2010-2024 worst 12m return | -10.09% | -10.09% |

The previous 0.811 champion remains a comparison point in the reproduced experiment evidence. The cleaned submission snapshot keeps the final reproducible outputs rather than bulky intermediate archive folders.

## 10. Limitations

The main limitations are:

- No complete external borrow-fee or locate-rate tape; only two anecdotal public crowded-short checks are included.
- No independent raw FINRA publication-date reconstruction for short interest; the pipeline uses provided point-in-time proxies plus an added one-trading-day decision lag.
- The square-root impact table is diagnostic only; realised performance deliberately keeps the fixed brief slippage schedule.
- The 1B AUM case is constrained and should not be presented as fully scalable.
- Holdout performance is positive but materially lower than validation performance.
- Nonlinear models such as LightGBM and HistGradientBoosting performed strongly in a limited model-family robustness screen, but they are not promoted final strategies without a dedicated nonlinear promotion audit.

## Reproduction

Final strategy reproduction commands:

```bash
PYTHONPATH=src python3 -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode all
PYTHONPATH=src python3 -m pytest -q
```

The latest recorded run passed with 13 tests. The optional LightGBM diagnostic writes `outputs/report_ready/lightgbm_diagnostic.csv` when LightGBM is available; the submitted final strategy does not depend on LightGBM.

## Final Decision

The recommended final strategy remains `phase2_g5_05_expanding`: volatility-scaled overnight target with expanding-window transparent weight estimation. The correct final 250M headline is **7.31%** net annual return, **4.97%** net volatility, net Sharpe **1.445**, and max drawdown **-10.19%**. The old **0.811** Sharpe appears only as previous champion comparison.
