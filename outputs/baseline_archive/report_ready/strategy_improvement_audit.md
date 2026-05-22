# Strategy Improvement Audit

Generated from `outputs/strategy_experiment_summary.csv` using the 2010-2024 development window only.

## Baseline

Baseline is the current top/bottom 3% equal-weight 250M strategy with tiered borrow costs and cross-sectional rank target.

- Net Sharpe: 0.379; net annual return: 1.69%; max drawdown: -24.58%; worst 12m return: -12.98%.

## 1. Changes That Improve 250M Net Sharpe

| experiment_group     | experiment_name                                |   net_sharpe |   net_annual_return |   net_vol |   max_drawdown |   worst_12m_return |   IC_mean | improvement_source               |
|:---------------------|:-----------------------------------------------|-------------:|--------------------:|----------:|---------------:|-------------------:|----------:|:---------------------------------|
| E_target_transform   | volatility_scaled_overnight_return             |     0.811479 |           0.0393139 | 0.0490024 |      -0.101865 |          -0.100903 | 0.028168  | better capacity use              |
| E_target_transform   | demeaned_overnight_return                      |     0.764228 |           0.0419523 | 0.0558152 |      -0.101865 |          -0.100903 | 0.0268948 | better capacity use              |
| E_target_transform   | winsorised_overnight_return                    |     0.763528 |           0.0432839 | 0.0576759 |      -0.113368 |          -0.100903 | 0.0280457 | better capacity use              |
| E_target_transform   | raw_overnight_return                           |     0.692414 |           0.0390731 | 0.0577654 |      -0.118771 |          -0.110513 | 0.0280807 | better capacity use              |
| B_weighting          | score_divided_by_volatility                    |     0.498271 |           0.0240452 | 0.0502172 |      -0.220742 |          -0.114101 | 0.0273122 | mixed or small mechanical change |
| B_weighting          | score_weighted                                 |     0.444001 |           0.0219216 | 0.0518696 |      -0.25022  |          -0.13648  | 0.0273122 | mixed or small mechanical change |
| B_weighting          | volatility_weighted                            |     0.42928  |           0.0189078 | 0.0461105 |      -0.220817 |          -0.121755 | 0.0273122 | mixed or small mechanical change |
| C_cost_aware_ranking | short_alpha_minus_borrow_and_liquidity_penalty |     0.418567 |           0.0192955 | 0.0484642 |      -0.240452 |          -0.131526 | 0.0273122 | mixed or small mechanical change |
| D_short_leg          | exclude_tier_c_shorts                          |     0.388033 |           0.0173486 | 0.0471931 |      -0.242452 |          -0.128763 | 0.0273122 | lower borrow drag                |

## 2. Robustness Improvements Without Higher Sharpe

| experiment_group     | experiment_name                       |   net_sharpe |   net_vol |   max_drawdown |   worst_12m_return |   average_gross_exposure_used |   average_daily_turnover |
|:---------------------|:--------------------------------------|-------------:|----------:|---------------:|-------------------:|------------------------------:|-------------------------:|
| D_short_leg          | downweight_tier_b_c_shorts_50pct      |     0.361159 | 0.0451677 |      -0.247195 |          -0.157088 |                      0.49102  |                 0.982041 |
| C_cost_aware_ranking | alpha_minus_estimated_round_trip_cost |    -0.339809 | 0.0318988 |      -0.303913 |          -0.175429 |                      0.997322 |                 1.99464  |
| A_basket_size        | top_bottom_10pct                      |    -0.571087 | 0.04405   |      -0.371657 |          -0.196095 |                      0.9942   |                 1.9884   |

## 3. Variants That Look Overfit Or Unstable

Flagged when 250M net Sharpe is negative, IC t-stat is below 2, or the worst rolling 12-month return is more than 5 percentage points worse than baseline.

| experiment_group     | experiment_name                       |   net_sharpe |   IC_tstat |   max_drawdown |   worst_12m_return |   average_gross_exposure_used |
|:---------------------|:--------------------------------------|-------------:|-----------:|---------------:|-------------------:|------------------------------:|
| A_basket_size        | top_bottom_10pct                      |    -0.571087 |    8.36296 |      -0.371657 |          -0.196095 |                      0.9942   |
| A_basket_size        | long_5pct_short_10pct                 |    -0.391878 |    8.36296 |      -0.366331 |          -0.18144  |                      0.973261 |
| C_cost_aware_ranking | alpha_minus_estimated_round_trip_cost |    -0.339809 |    8.36296 |      -0.303913 |          -0.175429 |                      0.997322 |
| A_basket_size        | top_bottom_7_5pct                     |    -0.234572 |    8.36296 |      -0.304727 |          -0.186218 |                      0.951406 |
| B_weighting          | score_times_liquidity                 |     0.347131 |    8.36296 |      -0.311516 |          -0.186408 |                      0.578925 |

## 4. Source Of Improvement

The source label compares each 250M variant with baseline. It is a diagnostic rather than a causal proof: stronger alpha is proxied by higher IC, lower cost by lower turnover or drag, better capacity by higher gross exposure, and lower risk by lower realised volatility.

| experiment_group     | experiment_name                                |   net_sharpe |   gross_sharpe |   commission_drag |   slippage_drag |   borrow_drag |   average_gross_exposure_used | improvement_source               |
|:---------------------|:-----------------------------------------------|-------------:|---------------:|------------------:|----------------:|--------------:|------------------------------:|:---------------------------------|
| E_target_transform   | volatility_scaled_overnight_return             |     0.811479 |        2.42678 |          0.360628 |        1.08438  |     0.170293  |                      0.704268 | better capacity use              |
| E_target_transform   | demeaned_overnight_return                      |     0.764228 |        2.05616 |          0.29783  |        0.89543  |     0.0986758 |                      0.662474 | better capacity use              |
| E_target_transform   | winsorised_overnight_return                    |     0.763528 |        2.11559 |          0.310849 |        0.934524 |     0.106687  |                      0.714413 | better capacity use              |
| E_target_transform   | raw_overnight_return                           |     0.692414 |        2.02548 |          0.304783 |        0.916216 |     0.112064  |                      0.701422 | better capacity use              |
| B_weighting          | score_divided_by_volatility                    |     0.498271 |        1.76446 |          0.289673 |        0.87058  |     0.105939  |                      0.578925 | mixed or small mechanical change |
| B_weighting          | score_weighted                                 |     0.444001 |        1.67055 |          0.280554 |        0.843007 |     0.102984  |                      0.578925 | mixed or small mechanical change |
| B_weighting          | volatility_weighted                            |     0.42928  |        1.80713 |          0.315444 |        0.948165 |     0.114245  |                      0.578925 | mixed or small mechanical change |
| C_cost_aware_ranking | short_alpha_minus_borrow_and_liquidity_penalty |     0.418567 |        1.73887 |          0.302361 |        0.908902 |     0.109042  |                      0.583384 | mixed or small mechanical change |
| D_short_leg          | exclude_tier_c_shorts                          |     0.388033 |        1.72063 |          0.316473 |        0.951093 |     0.06503   |                      0.594226 | lower borrow drag                |

## 5. Recommended Final Strategy Version

Use `E_target_transform / volatility_scaled_overnight_return` as the candidate final strategy, subject to final report review and no further unlogged tuning.

Recommended row: `E_target_transform / volatility_scaled_overnight_return`; 250M net Sharpe 0.811, net annual return 3.93%, max drawdown -10.19%, worst 12m -10.09%.

## Guardrails

- No 2025 or later data is loaded; the configured cutoff is 2024-12-31.
- All variants are logged in the CSV, including failed experiments.
- No new features are introduced; all ranking adjustments use existing point-in-time score, volatility, ADV20, and borrow-tier fields observable at the decision date.
- Headline returns still use the fixed Section 6.3 commission, slippage, and borrow schedule.
