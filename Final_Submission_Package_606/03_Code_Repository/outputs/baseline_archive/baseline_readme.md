# Baseline Archive

This folder preserves the original baseline outputs before promoting the
volatility-scaled overnight-return target as the final strategy.

The original baseline pipeline output in `outputs/performance_summary.csv`
reported a 250M net Sharpe of approximately `0.374`.

The logged experiment harness baseline in
`outputs/strategy_experiment_summary.csv` reported a 250M net Sharpe of
approximately `0.379`.

The small difference is due to the experiment harness baseline
implementation and logging path. The original baseline output files are
preserved here so the submission can distinguish the initial reproducible
baseline from the final promoted strategy and from the logged experiment
comparison.
