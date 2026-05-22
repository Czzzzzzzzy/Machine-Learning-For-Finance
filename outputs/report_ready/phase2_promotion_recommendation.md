# Phase 2 Promotion Recommendation

This is a recommendation for user review only. It does not promote or overwrite
the current champion.

## Exact Challenger Configuration

- Experiment id: `phase2_g5_05_expanding`
- Group: `G5_training_window`
- Name: `expanding window`
- Long fraction: `0.03`
- Short fraction: `0.03`
- Weighting scheme: `equal_weight`
- Ranking scheme: `raw_alpha_score`
- Short treatment: `tiered_borrow_cost_only`
- Training window: `expanding`
- Alpha learning method: `prior50_learned50`

## Why It Beats The Current Champion

- Validation 2019-2022 250M net Sharpe: `2.279` versus champion `1.107`.
- Internal holdout 2023-2024 250M net Sharpe: `0.620` versus champion `0.003`.
- Full 2010-2024 250M net Sharpe: `1.445` versus champion `0.811`.
- Full 250M max drawdown: `-10.19%` versus champion `-10.19%`.

## Assumption Checks

- 2023-2024 internal holdout acceptable: `True`.
- Costs unchanged: `True`.
- Borrow assumptions unchanged: `True`.
- Participation cap unchanged: `True`.
- Execution timing unchanged: `True`.
- Point-in-time audit passes by construction subject to `phase2_recommended_point_in_time_audit.md`.
