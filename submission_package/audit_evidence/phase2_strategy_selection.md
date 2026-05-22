# Phase 2 Strategy Selection

This memo is the pre-promotion champion-challenger screen. After the promotion audit, `phase2_g5_05_expanding` became the final strategy; the 0.811 strategy should now be read as the previous 4-year rolling champion.

## 1. Previous Champion Summary At Screen Time

- Strategy: `volatility_scaled_overnight_return`.
- 250M full development net Sharpe: `0.811`.
- 250M validation 2019-2022 net Sharpe: `1.107`.
- 250M internal holdout 2023-2024 net Sharpe: `0.003`.
- Full 250M max drawdown: `-10.19%`.

## 2. Top 10 Challengers By Validation 2019-2022 250M Net Sharpe

| experiment_id                               | experiment_group              |   validation_2019_2022_250m_net_sharpe |   internal_holdout_2023_2024_250m_net_sharpe |   full_2010_2024_250m_net_sharpe |   full_250m_average_turnover |   full_250m_total_cost_drag |   full_250m_average_gross_exposure_used |
|:--------------------------------------------|:------------------------------|---------------------------------------:|---------------------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|----------------------------------------:|
| phase2_g5_05_expanding                      | G5_training_window            |                               2.278993 |                                     0.620163 |                         1.445318 |                     1.499426 |                    1.666561 |                                0.749713 |
| phase2_g2_06_score_div_vol_liquidity_floor  | G2_weighting_scheme           |                               1.754876 |                                     0.818036 |                         1.275686 |                     1.408536 |                    1.480952 |                                0.704268 |
| phase2_g2_04_score_divided_by_volatility    | G2_weighting_scheme           |                               1.710867 |                                     0.760509 |                         1.241436 |                     1.408536 |                    1.495739 |                                0.704268 |
| phase2_g6_06_elastic_net_ranked_features    | G6_transparent_alpha_learning |                               1.571677 |                                     0.900135 |                         1.257566 |                     1.482502 |                    1.636099 |                                0.741251 |
| phase2_g2_03_score_weighted                 | G2_weighting_scheme           |                               1.534315 |                                     0.372750 |                         1.088435 |                     1.408536 |                    1.484695 |                                0.704268 |
| phase2_g6_05_ridge_ranked_features          | G6_transparent_alpha_learning |                               1.523141 |                                     1.026967 |                         1.239191 |                     1.469225 |                    1.603733 |                                0.734613 |
| phase2_g2_05_score_times_liquidity          | G2_weighting_scheme           |                               1.499142 |                                     0.194643 |                         1.065721 |                     1.408536 |                    1.398729 |                                0.704268 |
| phase2_g2_07_score_weighted_single_name_cap | G2_weighting_scheme           |                               1.495513 |                                     0.311993 |                         1.040548 |                     1.308052 |                    1.576971 |                                0.654026 |
| phase2_g2_02_volatility_weighted            | G2_weighting_scheme           |                               1.429059 |                                     0.472621 |                         1.055630 |                     1.408536 |                    1.616379 |                                0.704268 |
| phase2_g6_04_learned100                     | G6_transparent_alpha_learning |                               1.299937 |                                     0.301491 |                         0.992155 |                     1.456299 |                    1.606923 |                                0.728150 |

## 3. Top 10 Challengers By Internal Holdout 2023-2024 250M Net Sharpe

| experiment_id                              | experiment_group              |   validation_2019_2022_250m_net_sharpe |   internal_holdout_2023_2024_250m_net_sharpe |   full_2010_2024_250m_net_sharpe |   full_250m_average_turnover |   full_250m_total_cost_drag |   full_250m_average_gross_exposure_used |
|:-------------------------------------------|:------------------------------|---------------------------------------:|---------------------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|----------------------------------------:|
| phase2_g4_06_exclude_tier_c_score_vol      | G4_borrow_aware_short_leg     |                               1.260441 |                                     1.050140 |                         1.091470 |                     1.468736 |                    1.467735 |                                0.734368 |
| phase2_g6_05_ridge_ranked_features         | G6_transparent_alpha_learning |                               1.523141 |                                     1.026967 |                         1.239191 |                     1.469225 |                    1.603733 |                                0.734613 |
| phase2_g6_06_elastic_net_ranked_features   | G6_transparent_alpha_learning |                               1.571677 |                                     0.900135 |                         1.257566 |                     1.482502 |                    1.636099 |                                0.741251 |
| phase2_g2_06_score_div_vol_liquidity_floor | G2_weighting_scheme           |                               1.754876 |                                     0.818036 |                         1.275686 |                     1.408536 |                    1.480952 |                                0.704268 |
| phase2_g2_04_score_divided_by_volatility   | G2_weighting_scheme           |                               1.710867 |                                     0.760509 |                         1.241436 |                     1.408536 |                    1.495739 |                                0.704268 |
| phase2_g5_05_expanding                     | G5_training_window            |                               2.278993 |                                     0.620163 |                         1.445318 |                     1.499426 |                    1.666561 |                                0.749713 |
| phase2_g2_02_volatility_weighted           | G2_weighting_scheme           |                               1.429059 |                                     0.472621 |                         1.055630 |                     1.408536 |                    1.616379 |                                0.704268 |
| phase2_g2_03_score_weighted                | G2_weighting_scheme           |                               1.534315 |                                     0.372750 |                         1.088435 |                     1.408536 |                    1.484695 |                                0.704268 |
| phase2_g6_07_robust_ridge_clipped          | G6_transparent_alpha_learning |                               1.098833 |                                     0.339252 |                         0.957206 |                     1.477016 |                    1.602551 |                                0.738508 |
| phase2_g4_02_exclude_tier_c_shorts         | G4_borrow_aware_short_leg     |                               0.656789 |                                     0.312378 |                         0.651475 |                     1.468736 |                    1.574168 |                                0.734368 |

## 4. Rejected Overfit Candidates

### high full-sample Sharpe but weak 2023-2024 holdout

| experiment_id                          |   validation_2019_2022_250m_net_sharpe |   internal_holdout_2023_2024_250m_net_sharpe |   full_2010_2024_250m_net_sharpe |   full_2010_2024_250m_max_drawdown |   full_250m_average_turnover |   full_250m_average_gross_exposure_used |   full_250m_IC_tstat |
|:---------------------------------------|---------------------------------------:|---------------------------------------------:|---------------------------------:|-----------------------------------:|-----------------------------:|----------------------------------------:|---------------------:|
| phase2_g4_07_downweight_b_c_cost_aware |                               1.276140 |                                    -0.117423 |                         0.897135 |                          -0.101003 |                     1.168933 |                                0.584466 |             9.464596 |
| phase2_g4_04_downweight_tier_b_c_50pct |                               1.207306 |                                    -0.205964 |                         0.839055 |                          -0.104476 |                     1.156097 |                                0.578048 |             9.464596 |

### high Sharpe caused mainly by low exposure

| experiment_id                          |   validation_2019_2022_250m_net_sharpe |   internal_holdout_2023_2024_250m_net_sharpe |   full_2010_2024_250m_net_sharpe |   full_2010_2024_250m_max_drawdown |   full_250m_average_turnover |   full_250m_average_gross_exposure_used |   full_250m_IC_tstat |
|:---------------------------------------|---------------------------------------:|---------------------------------------------:|---------------------------------:|-----------------------------------:|-----------------------------:|----------------------------------------:|---------------------:|
| phase2_g4_07_downweight_b_c_cost_aware |                               1.276140 |                                    -0.117423 |                         0.897135 |                          -0.101003 |                     1.168933 |                                0.584466 |             9.464596 |
| phase2_g4_04_downweight_tier_b_c_50pct |                               1.207306 |                                    -0.205964 |                         0.839055 |                          -0.104476 |                     1.156097 |                                0.578048 |             9.464596 |

### large drawdown deterioration

| experiment_id                             |   validation_2019_2022_250m_net_sharpe |   internal_holdout_2023_2024_250m_net_sharpe |   full_2010_2024_250m_net_sharpe |   full_2010_2024_250m_max_drawdown |   full_250m_average_turnover |   full_250m_average_gross_exposure_used |   full_250m_IC_tstat |
|:------------------------------------------|---------------------------------------:|---------------------------------------------:|---------------------------------:|-----------------------------------:|-----------------------------:|----------------------------------------:|---------------------:|
| phase2_g6_07_robust_ridge_clipped         |                               1.098833 |                                     0.339252 |                         0.957206 |                          -0.141449 |                     1.477016 |                                0.738508 |            11.414995 |
| phase2_g4_02_exclude_tier_c_shorts        |                               0.656789 |                                     0.312378 |                         0.651475 |                          -0.160913 |                     1.468736 |                                0.734368 |             9.464596 |
| phase2_g4_05_expand_short_basket          |                               0.762163 |                                     0.027435 |                         0.564183 |                          -0.154015 |                     1.824256 |                                0.912128 |             9.464596 |
| phase2_g5_01_2y_rolling                   |                               0.593919 |                                    -0.218872 |                         0.557784 |                          -0.154058 |                     1.400551 |                                0.700276 |             8.181739 |
| phase2_g4_03_exclude_tier_b_c_shorts      |                               0.557802 |                                    -0.049162 |                         0.528064 |                          -0.218470 |                     1.606802 |                                0.803401 |             9.464596 |
| phase2_g3_06_cost_aware_long_short        |                               0.173695 |                                    -2.010789 |                         0.505164 |                          -0.188103 |                     1.996501 |                                0.998250 |             9.464596 |
| phase2_g3_03_alpha_minus_liquidity_impact |                               0.294397 |                                    -2.064465 |                         0.496434 |                          -0.186513 |                     1.996076 |                                0.998038 |             9.464596 |
| phase2_g1_02_top_bottom_5pct_equal        |                               0.554358 |                                    -0.341652 |                         0.475767 |                          -0.184090 |                     1.839325 |                                0.919662 |             9.464596 |

### excessive turnover/cost drag

| experiment_id                             |   validation_2019_2022_250m_net_sharpe |   internal_holdout_2023_2024_250m_net_sharpe |   full_2010_2024_250m_net_sharpe |   full_2010_2024_250m_max_drawdown |   full_250m_average_turnover |   full_250m_average_gross_exposure_used |   full_250m_IC_tstat |
|:------------------------------------------|---------------------------------------:|---------------------------------------------:|---------------------------------:|-----------------------------------:|-----------------------------:|----------------------------------------:|---------------------:|
| phase2_g3_06_cost_aware_long_short        |                               0.173695 |                                    -2.010789 |                         0.505164 |                          -0.188103 |                     1.996501 |                                0.998250 |             9.464596 |
| phase2_g3_03_alpha_minus_liquidity_impact |                               0.294397 |                                    -2.064465 |                         0.496434 |                          -0.186513 |                     1.996076 |                                0.998038 |             9.464596 |
| phase2_g1_05_long_5_short_7_5_equal       |                               0.371124 |                                    -0.508737 |                         0.266537 |                          -0.183873 |                     1.965893 |                                0.982947 |             9.464596 |
| phase2_g1_06_long_5_short_10_equal        |                               0.389245 |                                    -0.611861 |                         0.140083 |                          -0.197462 |                     1.982786 |                                0.991393 |             9.464596 |
| phase2_g1_03_top_bottom_7_5pct_equal      |                               0.162107 |                                    -0.756322 |                         0.093082 |                          -0.224345 |                     1.981037 |                                0.990519 |             9.464596 |
| phase2_g1_07_long_7_5_short_10_equal      |                               0.167460 |                                    -0.878219 |                        -0.055784 |                          -0.238385 |                     1.997890 |                                0.998945 |             9.464596 |
| phase2_g1_04_top_bottom_10pct_equal       |                              -0.079175 |                                    -1.187560 |                        -0.248057 |                          -0.269439 |                     1.998268 |                                0.999134 |             9.464596 |

### unstable IC

_None._

## 5. Recommended Decision

B. A Phase 2 challenger clears the replacement rule and should be reviewed for possible promotion: `phase2_g5_05_expanding`. Do not promote automatically.

All Phase 2 runs use the same fixed commission, auction slippage, tiered borrow, 5% ADV20 participation cap, and close-to-open execution assumptions. The previous champion remains frozen until explicit user approval.
