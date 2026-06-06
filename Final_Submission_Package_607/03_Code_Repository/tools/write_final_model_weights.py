"""Write final promoted expanding-window linear-model weights.

The legacy `outputs/feature_weights.csv` belongs to the earlier rolling-window
pipeline.  The promoted final strategy is Phase 2 `phase2_g5_05_expanding`, so
its report should use weights recomputed with the Phase 2 expanding-window
weight estimator.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from c2o_strategy.alpha import _prior_weights
from c2o_strategy.config import StrategyConfig
from c2o_strategy.experiments import MIN_TRAINING_OBSERVATIONS, add_target_transform, load_or_prepare_experiment_panel
from c2o_strategy.phase2 import DEFAULT_ALPHA_METHOD, TARGET, TARGET_DEFINITION, learn_phase2_weights, training_start_for_window


def main() -> None:
    config = StrategyConfig()
    out_dir = config.output_dir / "report_ready"
    out_dir.mkdir(parents=True, exist_ok=True)

    panel, rank_columns = load_or_prepare_experiment_panel(config)
    scored = add_target_transform(panel, "vol_scaled")
    prior = _prior_weights(rank_columns)

    rows = []
    for year in sorted(scored["year"].dropna().unique()):
        year = int(year)
        year_start = pd.Timestamp(year=year, month=1, day=1)
        train_end = min(year_start - pd.Timedelta(days=1), config.development_cutoff_ts)
        train_start = training_start_for_window(train_end, config, "expanding")
        train = scored.loc[scored["date"].between(train_start, train_end)]
        sample_count = int((train["is_trade_eligible"] & train["experiment_target"].notna()).sum())
        weights = learn_phase2_weights(
            train,
            rank_columns,
            prior,
            DEFAULT_ALPHA_METHOD,
            "expanding",
            train_end,
        )
        source = (
            "prior_fallback"
            if sample_count < MIN_TRAINING_OBSERVATIONS
            else "phase2_expanding_prior50_learned50"
        )
        for feature, weight in weights.items():
            rows.append(
                {
                    "year": year,
                    "feature": feature,
                    "weight": float(weight),
                    "source": source,
                    "train_start": str(train_start.date()),
                    "train_end": str(train_end.date()),
                    "training_window": "expanding",
                    "alpha_learning_method": DEFAULT_ALPHA_METHOD,
                    "target": TARGET,
                    "target_definition": TARGET_DEFINITION,
                    "training_rows": sample_count,
                }
            )

    weights_frame = pd.DataFrame(rows)
    weights_frame.to_csv(out_dir / "final_expanding_feature_weights.csv", index=False)
    print(f"Wrote {out_dir / 'final_expanding_feature_weights.csv'}")


if __name__ == "__main__":
    main()
