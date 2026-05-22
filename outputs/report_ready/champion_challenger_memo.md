# Champion-Challenger Memo

This memo records the pre-promotion Phase 2 screen. The 0.811 strategy was the champion at screening time and is now the previous 4-year rolling champion after promotion.

## Previous Champion At Screen Time

- Full 2010-2024 250M net Sharpe: `0.811`; validation 2019-2022 250M net Sharpe: `1.107`; holdout 2023-2024 250M net Sharpe: `0.003`.
- Full 250M max drawdown: `-10.19%`; average gross exposure used: `70.43%`.

## Top Challengers By Validation Sharpe

| experiment_id                               | experiment_group              |   validation_2019_2022_250m_net_sharpe |   internal_holdout_2023_2024_250m_net_sharpe |   full_2010_2024_250m_net_sharpe |   full_250m_average_turnover |   full_250m_average_gross_exposure_used | passes_phase2_replacement_rule   |
|:--------------------------------------------|:------------------------------|---------------------------------------:|---------------------------------------------:|---------------------------------:|-----------------------------:|----------------------------------------:|:---------------------------------|
| phase2_g5_05_expanding                      | G5_training_window            |                               2.278993 |                                     0.620163 |                         1.445318 |                     1.499426 |                                0.749713 | True                             |
| phase2_g2_06_score_div_vol_liquidity_floor  | G2_weighting_scheme           |                               1.754876 |                                     0.818036 |                         1.275686 |                     1.408536 |                                0.704268 | True                             |
| phase2_g2_04_score_divided_by_volatility    | G2_weighting_scheme           |                               1.710867 |                                     0.760509 |                         1.241436 |                     1.408536 |                                0.704268 | True                             |
| phase2_g6_06_elastic_net_ranked_features    | G6_transparent_alpha_learning |                               1.571677 |                                     0.900135 |                         1.257566 |                     1.482502 |                                0.741251 | True                             |
| phase2_g2_03_score_weighted                 | G2_weighting_scheme           |                               1.534315 |                                     0.372750 |                         1.088435 |                     1.408536 |                                0.704268 | True                             |
| phase2_g6_05_ridge_ranked_features          | G6_transparent_alpha_learning |                               1.523141 |                                     1.026967 |                         1.239191 |                     1.469225 |                                0.734613 | True                             |
| phase2_g2_05_score_times_liquidity          | G2_weighting_scheme           |                               1.499142 |                                     0.194643 |                         1.065721 |                     1.408536 |                                0.704268 | True                             |
| phase2_g2_07_score_weighted_single_name_cap | G2_weighting_scheme           |                               1.495513 |                                     0.311993 |                         1.040548 |                     1.308052 |                                0.654026 | True                             |
| phase2_g2_02_volatility_weighted            | G2_weighting_scheme           |                               1.429059 |                                     0.472621 |                         1.055630 |                     1.408536 |                                0.704268 | True                             |
| phase2_g6_04_learned100                     | G6_transparent_alpha_learning |                               1.299937 |                                     0.301491 |                         0.992155 |                     1.456299 |                                0.728150 | True                             |
| phase2_g4_07_downweight_b_c_cost_aware      | G4_borrow_aware_short_leg     |                               1.276140 |                                    -0.117423 |                         0.897135 |                     1.168933 |                                0.584466 | False                            |
| phase2_g6_02_prior25_learned75              | G6_transparent_alpha_learning |                               1.264655 |                                     0.257871 |                         0.956754 |                     1.439764 |                                0.719882 | True                             |

## Mechanical Screen Result

At least one challenger passes the mechanical Phase 2 replacement screen and should be reviewed by the user before any promotion.

The screen checks validation improvement first, then holdout non-failure, drawdown, exposure, turnover/cost, AUM robustness, and IC stability. It is a guardrail, not an automatic promotion.
