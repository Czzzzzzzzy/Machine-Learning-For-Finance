"""Write final promoted expanding-window linear-model weights.

The legacy `outputs/feature_weights.csv` belongs to the earlier rolling-window
pipeline.  The promoted final strategy is Phase 2 `phase2_g5_05_expanding`, so
its report should use weights recomputed with the Phase 2 expanding-window
weight estimator.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from c2o_strategy.config import StrategyConfig
from c2o_strategy.experiments import load_or_prepare_experiment_panel
from c2o_strategy.phase2 import DEFAULT_ALPHA_METHOD, load_or_train_phase2_weight_schedule


def main() -> None:
    config = StrategyConfig()
    out_dir = config.output_dir / "report_ready"
    out_dir.mkdir(parents=True, exist_ok=True)

    panel, rank_columns = load_or_prepare_experiment_panel(config)
    weights_frame, _ = load_or_train_phase2_weight_schedule(
        panel,
        rank_columns,
        config,
        "expanding",
        DEFAULT_ALPHA_METHOD,
        use_model_cache=True,
    )
    weights_frame = weights_frame.drop(
        columns=["cache_version", "feature_count", "feature_set"],
        errors="ignore",
    )
    weights_frame.to_csv(out_dir / "final_expanding_feature_weights.csv", index=False)
    print(f"Wrote {out_dir / 'final_expanding_feature_weights.csv'}")


if __name__ == "__main__":
    main()
