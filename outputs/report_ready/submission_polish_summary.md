# Submission Polish Summary

## 1. Strategy Experiments Added

Phase 2 added a controlled champion-challenger study with 40 specifications across six groups: basket size, weighting, cost-aware ranking, borrow-aware short leg, training window, and transparent alpha-learning alternatives. Each experiment was evaluated at 50M, 250M, and 1B across design 2010-2018, validation 2019-2022, internal holdout 2023-2024, and full 2010-2024. `outputs/phase2_experiment_summary.csv` has `480` rows.

## 2. Whether Any Challenger Beat The Previous Champion

Yes. `phase2_g5_05_expanding` beat the previous 4-year rolling champion under the controlled screen. At 250M, validation Sharpe improved from `1.107` to `2.279`, internal holdout Sharpe improved from `0.003` to `0.620`, and full-period Sharpe improved from `0.811` to `1.445`.

## 3. Recommended Strategy Decision

Decision: promote `phase2_g5_05_expanding` as the new final strategy after passing the promotion audit. The final strategy is the volatility-scaled overnight-return target with expanding-window transparent feature-weight estimation.

## 4. Stale Files Cleaned

Stale old-final references were updated or moved out of report-ready paths. The audit trail is in `outputs/report_ready/stale_file_audit.md`. Baseline and previous champion archives were preserved.

## 5. Robustness Evidence Added

Robustness diagnostics were regenerated for the promoted final strategy in `outputs/report_ready/locked_strategy_robustness.csv` and `.md`. The evidence includes yearly metrics, pre/post split, stress windows, rolling losses, top-day PnL concentration, lag-1 autocorrelation, gross exposure, and cap-binding frequency.

## 6. Tests Added

High-risk tests cover cutoff protection, cost constants, 5% ADV20 cap, final position completeness, no 2025+ output dates, dollar neutrality, borrow-tier mapping, earnings timing examples, and short-interest lag wording. Latest result: `13 passed`.

## 7. Report Wording Improved

The report now states that the final strategy uses a volatility-scaled target with expanding-window weight estimation. It explains that the improvement is not from lower costs, borrow relaxation, new data, or execution changes, and it discloses that 2023-2024 holdout Sharpe is lower than validation Sharpe.

## 8. External Borrow Validation

External borrow validation was not possible from public data already present in the repository. The limitation remains documented in `outputs/report_ready/borrow_external_validation_limitations.md`.

## 9. Remaining Limitations

- No independent prime-broker or securities-lending borrow-fee validation.
- No raw FINRA settlement/publication-date reconstruction for short interest.
- 1B remains capacity constrained under the 5% ADV20 cap.
- 2025-2026 remains held out for marker evaluation.

## 10. Final Test Result

`PYTHON=/opt/anaconda3/bin/python3 make reproduce` passed. `PYTHON=/opt/anaconda3/bin/python3 make test` passed with `13 passed`.

## 11. Final Strategy Outputs

Final strategy outputs were overwritten only after the promotion audit passed and the user approved moving to promotion. The old 0.811 champion is preserved in `outputs/previous_champion_archive_after_phase2/` and `outputs/current_champion_archive/`.
