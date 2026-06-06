"""Limited model-family robustness study for the promoted C2O candidate.

This script is intentionally a side study.  It writes only
`outputs/model_family_robustness_summary.csv` and report-ready memo files.  It
does not overwrite final strategy outputs, positions, daily returns, or the
final report.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from c2o_strategy.alpha import _prior_weights
from c2o_strategy.config import StrategyConfig
from c2o_strategy.experiments import (
    MIN_TRAINING_OBSERVATIONS,
    add_target_transform,
    annualised_return,
    annualised_volatility,
    load_or_prepare_experiment_panel,
    max_drawdown,
    sharpe_ratio,
    worst_rolling_12m_return,
)
from c2o_strategy.phase2 import (
    PERIODS,
    Phase2Spec,
    add_walk_forward_alpha_return_phase2,
    ic_summary,
    load_or_score_phase2_panel,
    phase2_cache_path,
    run_phase2_backtest,
)


TARGET = "volatility_scaled_overnight_return"
TARGET_DEFINITION = "overnight_next / (vol20 / sqrt(252))"
TRAINING_PROTOCOL = "annual expanding walk-forward; train strictly before scored year"
FEATURE_INPUT_TYPE = "same point-in-time cross-sectional ranked features"
RANDOM_SEED = 42
TREE_TRAIN_SAMPLE_CAP = 300_000


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    model_family: str
    estimator: str
    hyperparameters: dict[str, Any]
    notes: str
    use_existing_phase2_method: str | None = None
    train_sample_cap: int | None = None


def model_specs() -> list[ModelSpec]:
    specs = [
        ModelSpec(
            "current_expanding_linear_rank",
            "transparent_linear_rank_score",
            "phase2_prior50_learned50",
            {
                "training_window": "expanding",
                "alpha_learning_method": "prior50_learned50",
                "prior_weight": 0.50,
                "learned_weight": 0.50,
                "learned_transform": "corr(feature,target)/0.02 clipped to [-1,1]",
                "normalisation": "L1",
            },
            "Current final candidate; cached Phase 2 expanding score.",
            use_existing_phase2_method="prior50_learned50",
        ),
        ModelSpec(
            "ridge_ranked_features",
            "regularised_linear",
            "phase2_ridge_ranked_features",
            {
                "training_window": "expanding",
                "alpha_learning_method": "ridge_ranked_features",
                "penalty": 5.0,
                "normalisation": "L1",
            },
            "Ridge on ranked features using the existing deterministic Phase 2 implementation.",
            use_existing_phase2_method="ridge_ranked_features",
        ),
    ]

    try:
        import sklearn  # noqa: F401

        specs.extend(
            [
                ModelSpec(
                    "elastic_net_ranked_features",
                    "regularised_linear",
                    "phase2_elastic_net_ranked_features",
                    {
                        "training_window": "expanding",
                        "alpha_learning_method": "elastic_net_ranked_features",
                        "alpha": 0.0005,
                        "l1_ratio": 0.5,
                        "max_iter": 1000,
                        "random_state": RANDOM_SEED,
                    },
                    "Elastic net on ranked features; dependency already available.",
                    use_existing_phase2_method="elastic_net_ranked_features",
                ),
                ModelSpec(
                    "random_forest_ranked_features",
                    "tree_ensemble",
                    "sklearn_random_forest",
                    {
                        "n_estimators": 80,
                        "max_depth": 6,
                        "min_samples_leaf": 200,
                        "max_features": "sqrt",
                        "random_state": RANDOM_SEED,
                        "n_jobs": -1,
                        "train_sample_cap": TREE_TRAIN_SAMPLE_CAP,
                    },
                    "Random Forest with fixed conservative parameters and deterministic annual training sample cap.",
                    train_sample_cap=TREE_TRAIN_SAMPLE_CAP,
                ),
                ModelSpec(
                    "extra_trees_ranked_features",
                    "tree_ensemble",
                    "sklearn_extra_trees",
                    {
                        "n_estimators": 120,
                        "max_depth": 6,
                        "min_samples_leaf": 200,
                        "max_features": "sqrt",
                        "random_state": RANDOM_SEED,
                        "n_jobs": -1,
                        "train_sample_cap": TREE_TRAIN_SAMPLE_CAP,
                    },
                    "Extra Trees with fixed conservative parameters and deterministic annual training sample cap.",
                    train_sample_cap=TREE_TRAIN_SAMPLE_CAP,
                ),
                ModelSpec(
                    "hist_gradient_boosting_ranked_features",
                    "boosting",
                    "sklearn_hist_gradient_boosting",
                    {
                        "max_iter": 100,
                        "learning_rate": 0.05,
                        "max_leaf_nodes": 31,
                        "min_samples_leaf": 200,
                        "l2_regularization": 0.1,
                        "random_state": RANDOM_SEED,
                        "train_sample_cap": TREE_TRAIN_SAMPLE_CAP,
                    },
                    "HistGradientBoosting with fixed conservative parameters and deterministic annual training sample cap.",
                    train_sample_cap=TREE_TRAIN_SAMPLE_CAP,
                ),
            ]
        )
    except Exception:
        pass

    try:
        import lightgbm  # noqa: F401

        specs.append(
            ModelSpec(
                "lightgbm_ranked_features",
                "boosting",
                "lightgbm",
                {
                    "n_estimators": 200,
                    "learning_rate": 0.03,
                    "num_leaves": 31,
                    "max_depth": 6,
                    "min_child_samples": 200,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "reg_lambda": 1.0,
                    "random_state": RANDOM_SEED,
                    "n_jobs": -1,
                    "verbosity": -1,
                    "train_sample_cap": TREE_TRAIN_SAMPLE_CAP,
                },
                "LightGBM tested because it is already installed; no hyperparameter tuning.",
                train_sample_cap=TREE_TRAIN_SAMPLE_CAP,
            )
        )
    except Exception:
        pass

    return specs


def scored_cache_path(config: StrategyConfig, model_id: str) -> Path:
    return config.output_dir / f".model_family_robustness_scored_{model_id}_{config.cutoff_ts:%Y%m%d}.parquet"


def phase2_spec_for_model(spec: ModelSpec) -> Phase2Spec:
    return Phase2Spec(
        experiment_id=f"model_family_{spec.model_id}",
        experiment_group="model_family_robustness",
        experiment_name=spec.model_id,
        training_window="expanding",
        alpha_learning_method=spec.use_existing_phase2_method or "prior50_learned50",
        notes=spec.notes,
    )


def base_output_columns(panel: pd.DataFrame, rank_columns: list[str]) -> list[str]:
    cols = [
        "date",
        "year",
        "instrument_id",
        "ticker",
        "is_trade_eligible",
        "overnight_next",
        "adv20",
        "vol20",
        "borrow_tier",
        "borrow_rate_annual",
        *rank_columns,
        "alpha_score",
        "predicted_alpha_return",
    ]
    return [col for col in cols if col in panel.columns]


def estimator_for(spec: ModelSpec):
    if spec.estimator == "sklearn_random_forest":
        from sklearn.ensemble import RandomForestRegressor

        params = {k: v for k, v in spec.hyperparameters.items() if k != "train_sample_cap"}
        return RandomForestRegressor(**params)
    if spec.estimator == "sklearn_extra_trees":
        from sklearn.ensemble import ExtraTreesRegressor

        params = {k: v for k, v in spec.hyperparameters.items() if k != "train_sample_cap"}
        return ExtraTreesRegressor(**params)
    if spec.estimator == "sklearn_hist_gradient_boosting":
        from sklearn.ensemble import HistGradientBoostingRegressor

        params = {k: v for k, v in spec.hyperparameters.items() if k != "train_sample_cap"}
        return HistGradientBoostingRegressor(**params)
    if spec.estimator == "lightgbm":
        from lightgbm import LGBMRegressor

        params = {k: v for k, v in spec.hyperparameters.items() if k != "train_sample_cap"}
        return LGBMRegressor(**params)
    raise ValueError(f"Unsupported estimator: {spec.estimator}")


def deterministic_sample(sample: pd.DataFrame, cap: int | None, year: int) -> pd.DataFrame:
    if cap is None or len(sample) <= cap:
        return sample
    return sample.sample(n=cap, random_state=RANDOM_SEED + year)


def score_ml_model(
    panel: pd.DataFrame,
    rank_columns: list[str],
    config: StrategyConfig,
    spec: ModelSpec,
) -> pd.DataFrame:
    path = scored_cache_path(config, spec.model_id)
    if path.exists():
        print(f"Loading cached model-family scored panel {spec.model_id} from {path}", flush=True)
        out = pd.read_parquet(path)
        out["date"] = pd.to_datetime(out["date"])
        return out

    scored = add_target_transform(panel, "vol_scaled")
    scored["alpha_score"] = np.nan
    prior = _prior_weights(rank_columns)
    years = sorted(scored["year"].dropna().unique())
    for year_value in years:
        year = int(year_value)
        year_start = pd.Timestamp(year=year, month=1, day=1)
        train_end = min(year_start - pd.Timedelta(days=1), config.development_cutoff_ts)
        train_start = config.start_ts
        train_mask = (
            scored["date"].between(train_start, train_end)
            & scored["is_trade_eligible"]
            & scored["experiment_target"].notna()
        )
        train = scored.loc[train_mask, ["date", *rank_columns, "experiment_target"]]
        year_mask = scored["year"].eq(year)
        if len(train) < MIN_TRAINING_OBSERVATIONS:
            matrix = scored.loc[year_mask, rank_columns].fillna(0.0).to_numpy(dtype=float)
            scored.loc[year_mask, "alpha_score"] = matrix @ prior.reindex(rank_columns).to_numpy()
            continue

        train = deterministic_sample(train, spec.train_sample_cap, year)
        x_train = np.nan_to_num(
            train[rank_columns].to_numpy(dtype=np.float32),
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )
        y_train = train["experiment_target"].to_numpy(dtype=np.float32)
        model = estimator_for(spec)
        print(
            f"  scoring {spec.model_id} for {year}: train_rows={len(train):,}",
            flush=True,
        )
        model.fit(x_train, y_train)

        year_indices = scored.index[year_mask]
        x_year = np.nan_to_num(
            scored.loc[year_indices, rank_columns].to_numpy(dtype=np.float32),
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )
        scored.loc[year_indices, "alpha_score"] = model.predict(x_year).astype(float)

    scored = add_walk_forward_alpha_return_phase2(scored, config, "expanding")
    out = scored.drop(columns=["experiment_target"], errors="ignore")
    if out["date"].max() > config.cutoff_ts:
        raise ValueError(f"{spec.model_id} scored panel includes data after cutoff")
    out = out[base_output_columns(out, rank_columns)]
    out.to_parquet(path, index=False)
    print(f"Cached model-family scored panel {spec.model_id} to {path}", flush=True)
    return out


def load_or_score_model(
    panel: pd.DataFrame,
    rank_columns: list[str],
    config: StrategyConfig,
    spec: ModelSpec,
) -> pd.DataFrame:
    if spec.use_existing_phase2_method is not None:
        phase_spec = phase2_spec_for_model(spec)
        scored = load_or_score_phase2_panel(panel, rank_columns, config, phase_spec)
        return scored[base_output_columns(scored, rank_columns)].copy()
    return score_ml_model(panel, rank_columns, config, spec)


def summarise_model_period(
    daily: pd.DataFrame,
    scored: pd.DataFrame,
    spec: ModelSpec,
    aum: float,
    period_name: str,
    start: str,
    end: str,
) -> dict[str, Any]:
    chunk = daily.loc[pd.to_datetime(daily["date"]).between(start, end)].copy()
    gross = chunk["gross_return"]
    after_commission = gross - chunk["commission_cost"]
    after_slippage = after_commission - chunk["slippage_cost"]
    net = chunk["net_return"]
    gross_sharpe = sharpe_ratio(gross)
    after_commission_sharpe = sharpe_ratio(after_commission)
    after_slippage_sharpe = sharpe_ratio(after_slippage)
    net_sharpe = sharpe_ratio(net)
    scored_period = scored.loc[pd.to_datetime(scored["date"]).between(start, end)]
    ic_mean, ic_tstat = ic_summary(scored_period)

    return {
        "model_id": spec.model_id,
        "model_family": spec.model_family,
        "target": TARGET,
        "training_protocol": TRAINING_PROTOCOL,
        "feature_input_type": FEATURE_INPUT_TYPE,
        "hyperparameters": json.dumps(spec.hyperparameters, sort_keys=True),
        "AUM": aum,
        "period": period_name,
        "start_date": start,
        "end_date": end,
        "net_annual_return": annualised_return(net),
        "net_vol": annualised_volatility(net),
        "net_sharpe": net_sharpe,
        "max_drawdown": max_drawdown(net),
        "gross_sharpe": gross_sharpe,
        "commission_drag": gross_sharpe - after_commission_sharpe,
        "slippage_drag": after_commission_sharpe - after_slippage_sharpe,
        "borrow_drag": after_slippage_sharpe - net_sharpe,
        "average_turnover": float(chunk["turnover"].mean()) if not chunk.empty else np.nan,
        "average_gross_exposure_used": float(chunk["gross_exposure"].mean()) if not chunk.empty else np.nan,
        "cap_binding_days": int(chunk["cap_binding"].sum()) if not chunk.empty else 0,
        "fraction_cap_binding_days": float(chunk["cap_binding"].mean()) if not chunk.empty else np.nan,
        "IC_mean": ic_mean,
        "IC_tstat": ic_tstat,
        "worst_12m_return": worst_rolling_12m_return(chunk) if not chunk.empty else np.nan,
        "notes": spec.notes,
    }


def run_summary(config: StrategyConfig) -> pd.DataFrame:
    panel, rank_columns = load_or_prepare_experiment_panel(config)
    specs = model_specs()
    rows: list[dict[str, Any]] = []
    backtest_spec = Phase2Spec(
        experiment_id="model_family_backtest_spec",
        experiment_group="model_family_robustness",
        experiment_name="top_bottom_3pct_equal_raw_tiered",
        training_window="expanding",
        alpha_learning_method="model_family_score",
        notes="Common top/bottom 3%, equal weight, raw score ranking, tiered borrow-cost backtest.",
    )

    for spec in specs:
        print(f"Scoring model family: {spec.model_id}", flush=True)
        scored = load_or_score_model(panel, rank_columns, config, spec)
        if scored["date"].max() > config.cutoff_ts:
            raise ValueError(f"{spec.model_id} includes dates after cutoff")
        for aum in config.aums:
            print(f"  backtesting {spec.model_id} at AUM={aum:,.0f}", flush=True)
            daily = run_phase2_backtest(scored, aum, config, backtest_spec)
            for period_name, start, end in PERIODS:
                rows.append(summarise_model_period(daily, scored, spec, aum, period_name, start, end))

    out = pd.DataFrame(rows)
    required = [
        "model_id",
        "model_family",
        "target",
        "training_protocol",
        "feature_input_type",
        "hyperparameters",
        "AUM",
        "period",
        "start_date",
        "end_date",
        "net_annual_return",
        "net_vol",
        "net_sharpe",
        "max_drawdown",
        "gross_sharpe",
        "commission_drag",
        "slippage_drag",
        "borrow_drag",
        "average_turnover",
        "average_gross_exposure_used",
        "cap_binding_days",
        "fraction_cap_binding_days",
        "IC_mean",
        "IC_tstat",
        "worst_12m_return",
        "notes",
    ]
    out = out[required]
    out.to_csv(config.output_dir / "model_family_robustness_summary.csv", index=False)
    return out


def fmt(x: float, digits: int = 3) -> str:
    if pd.isna(x):
        return "NA"
    return f"{x:.{digits}f}"


def pct(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return "NA"
    return f"{x * 100:.{digits}f}%"


def model_period_table(summary: pd.DataFrame, aum: float = 250_000_000.0) -> pd.DataFrame:
    keep_periods = ["validation_2019_2022", "internal_holdout_2023_2024", "full_2010_2024"]
    data = summary.loc[summary["AUM"].eq(aum) & summary["period"].isin(keep_periods)].copy()
    pivot = data.pivot_table(index=["model_id", "model_family"], columns="period", values="net_sharpe", aggfunc="first")
    pivot = pivot.reset_index()
    for period in keep_periods:
        if period not in pivot.columns:
            pivot[period] = np.nan
    aux = data.pivot_table(index="model_id", columns="period", values=["max_drawdown", "average_turnover", "average_gross_exposure_used", "IC_mean", "IC_tstat"], aggfunc="first")
    rows = []
    for _, row in pivot.iterrows():
        model_id = row["model_id"]
        rows.append(
            {
                "model_id": model_id,
                "family": row["model_family"],
                "validation_sharpe": row["validation_2019_2022"],
                "holdout_sharpe": row["internal_holdout_2023_2024"],
                "full_sharpe": row["full_2010_2024"],
                "full_max_drawdown": aux.loc[model_id, ("max_drawdown", "full_2010_2024")] if model_id in aux.index else np.nan,
                "full_turnover": aux.loc[model_id, ("average_turnover", "full_2010_2024")] if model_id in aux.index else np.nan,
                "full_gross_exposure": aux.loc[model_id, ("average_gross_exposure_used", "full_2010_2024")] if model_id in aux.index else np.nan,
                "full_IC_mean": aux.loc[model_id, ("IC_mean", "full_2010_2024")] if model_id in aux.index else np.nan,
                "full_IC_tstat": aux.loc[model_id, ("IC_tstat", "full_2010_2024")] if model_id in aux.index else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("validation_sharpe", ascending=False)


def aum_robustness_table(summary: pd.DataFrame) -> pd.DataFrame:
    data = summary.loc[summary["period"].eq("full_2010_2024")].copy()
    pivot = data.pivot_table(index="model_id", columns="AUM", values="net_sharpe", aggfunc="first")
    pivot = pivot.rename(columns={50_000_000.0: "50M", 250_000_000.0: "250M", 1_000_000_000.0: "1B"})
    return pivot.reset_index()


def write_memo(summary: pd.DataFrame, config: StrategyConfig) -> None:
    report_dir = config.output_dir / "report_ready"
    report_dir.mkdir(parents=True, exist_ok=True)
    table = model_period_table(summary)
    current = table.loc[table["model_id"].eq("current_expanding_linear_rank")].iloc[0]
    nonlinear = table.loc[table["family"].isin(["tree_ensemble", "boosting"])].copy()
    beats_validation = nonlinear.loc[nonlinear["validation_sharpe"].gt(current["validation_sharpe"])]
    beats_both = beats_validation.loc[beats_validation["holdout_sharpe"].gt(current["holdout_sharpe"])]
    overfit = beats_validation.loc[beats_validation["holdout_sharpe"].le(current["holdout_sharpe"])]
    best = table.iloc[0]
    promote_candidate = (
        best["model_id"] != "current_expanding_linear_rank"
        and best["validation_sharpe"] > current["validation_sharpe"]
        and best["holdout_sharpe"] >= current["holdout_sharpe"]
    )

    display = table.copy()
    for col in ["validation_sharpe", "holdout_sharpe", "full_sharpe", "full_turnover", "full_gross_exposure", "full_IC_mean", "full_IC_tstat"]:
        display[col] = display[col].map(lambda x: fmt(float(x)))
    display["full_max_drawdown"] = display["full_max_drawdown"].map(lambda x: pct(float(x)))

    aum = aum_robustness_table(summary)
    for col in ["50M", "250M", "1B"]:
        if col in aum.columns:
            aum[col] = aum[col].map(lambda x: fmt(float(x)))

    recommendation = (
        "A. keep expanding linear ranking model"
        if not promote_candidate
        else (
            "D. keep nonlinear models only as robustness evidence until a dedicated "
            f"promotion audit is passed; audit candidate `{best['model_id']}`"
        )
    )

    lines = [
        "# Model Family Robustness Memo",
        "",
        "## 1. Why Alternative Models Were Tested",
        "",
        "This is a limited model-family robustness study around the current final candidate, "
        "`phase2_g5_05_expanding`. The aim is to check whether regularised linear or "
        "nonlinear models improve the validation/holdout tradeoff under the same point-in-time "
        "features, volatility-scaled target, cost schedule, borrow assumptions, 5% ADV20 cap, "
        "and close-to-open execution. The study does not promote a replacement and does not "
        "overwrite final outputs.",
        "",
        "Nonlinear models use a deterministic annual training sample cap of "
        f"`{TREE_TRAIN_SAMPLE_CAP:,}` rows to keep this a limited robustness study rather than "
        "a heavy tuning exercise. The training sample is always drawn only from dates strictly "
        "before the scored year.",
        "",
        "## 2. 250M Validation/Holdout Summary",
        "",
        display[
            [
                "model_id",
                "family",
                "validation_sharpe",
                "holdout_sharpe",
                "full_sharpe",
                "full_max_drawdown",
                "full_turnover",
                "full_gross_exposure",
                "full_IC_mean",
                "full_IC_tstat",
            ]
        ].to_markdown(index=False),
        "",
        "## 3. Do Nonlinear Models Beat The Current Expanding Linear Model?",
        "",
    ]
    if beats_both.empty:
        lines.append(
            "No nonlinear model clears the simple validation-plus-holdout screen against the "
            "current expanding linear ranking model. Some nonlinear models may show isolated "
            "improvements, but the evidence is not strong enough to justify replacing the "
            "transparent final candidate."
        )
    else:
        lines.append(
            "At least one nonlinear model improves both validation and internal holdout Sharpe "
            "versus the current model. This is only a promotion-audit trigger, not an automatic "
            "replacement."
        )
        lines.append("")
        lines.append(beats_both.to_markdown(index=False))

    lines.extend(
        [
            "",
            "## 4. Overfit Candidates",
            "",
        ]
    )
    if overfit.empty:
        lines.append("No nonlinear model has the classic pattern of beating validation while failing holdout.")
    else:
        lines.append(
            "The following nonlinear models beat validation but do not beat the 2023-2024 holdout, "
            "so they are treated as overfit or unstable candidates:"
        )
        lines.append("")
        lines.append(overfit.to_markdown(index=False))

    current_turnover = float(current["full_turnover"])
    high_turnover = table.loc[table["full_turnover"].gt(current_turnover * 1.10)].copy()
    low_exposure = table.loc[
        table["full_gross_exposure"].lt(float(current["full_gross_exposure"]) * 0.90)
    ].copy()

    lines.extend(
        [
            "",
            "## 5. Turnover, Cost Drag, And Exposure Flags",
            "",
        ]
    )
    if high_turnover.empty:
        lines.append("No tested model materially increases full-period 250M turnover by more than 10% versus the current model.")
    else:
        lines.append("Models with more than 10% higher turnover are flagged:")
        lines.append("")
        lines.append(high_turnover[["model_id", "full_turnover", "full_sharpe"]].to_markdown(index=False))
    lines.append("")
    if low_exposure.empty:
        lines.append("No tested model appears to improve Sharpe mainly through materially lower gross exposure.")
    else:
        lines.append("Models with materially lower full-period 250M gross exposure are flagged:")
        lines.append("")
        lines.append(low_exposure[["model_id", "full_gross_exposure", "full_sharpe"]].to_markdown(index=False))

    lines.extend(
        [
            "",
            "## 6. AUM Robustness",
            "",
            aum.to_markdown(index=False),
            "",
            "A credible replacement should remain sensible at 50M, 250M, and 1B. The 1B case remains "
            "a capacity boundary case for all models because the fixed 5% ADV20 cap limits deployable "
            "gross exposure.",
            "",
            "## 7. Explainability Comparison",
            "",
            "- Transparent linear ranking model: strongest auditability; coefficients are deterministic, "
            "point-in-time, and economically interpretable through feature groups.",
            "- Regularised linear models: still reasonably explainable, but less aligned with the prior-plus-learned "
            "economic design and can be more sensitive to target scaling.",
            "- Tree models: can capture interactions, but explanations are weaker and annual fitted structures "
            "are harder to audit than a coefficient vector.",
            "- Boosting models: can improve IC diagnostics, but carry higher overfit risk and lower transparency; "
            "in this study they are robustness evidence only unless validation and holdout both justify promotion.",
            "",
            "## 8. Final Recommendation",
            "",
            f"Recommendation: **{recommendation}**.",
            "",
        ]
    )
    if not promote_candidate:
        lines.append(
            "More complex models were considered, but they did not improve the validation-holdout "
            "tradeoff enough to displace the current expanding linear ranking model. The current model "
            "remains preferable because it combines competitive performance with interpretability, "
            "auditability, deterministic point-in-time training, and stable cost/capacity accounting."
        )
    else:
        lines.append(
            f"The strongest challenger is `{best['model_id']}`. It should enter a separate promotion "
            "audit before any final strategy output is overwritten."
        )

    (report_dir / "model_family_robustness_memo.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if promote_candidate:
        best_model = str(best["model_id"])
        best_rows = summary.loc[summary["model_id"].eq(best_model)]
        best_250 = best_rows.loc[best_rows["AUM"].eq(250_000_000.0)]
        full = best_250.loc[best_250["period"].eq("full_2010_2024")].iloc[0]
        validation = best_250.loc[best_250["period"].eq("validation_2019_2022")].iloc[0]
        holdout = best_250.loc[best_250["period"].eq("internal_holdout_2023_2024")].iloc[0]
        text = f"""# Model Promotion Recommendation

This file is an audit trigger only. It does not promote or overwrite final outputs.

- Exact model: `{best_model}`
- Hyperparameters: `{full['hyperparameters']}`
- Validation 2019-2022 250M Sharpe: `{validation['net_sharpe']:.6f}`
- Internal holdout 2023-2024 250M Sharpe: `{holdout['net_sharpe']:.6f}`
- Full 2010-2024 250M Sharpe: `{full['net_sharpe']:.6f}`
- Full max drawdown: `{full['max_drawdown']:.6f}`
- Full average turnover: `{full['average_turnover']:.6f}`
- Full average gross exposure: `{full['average_gross_exposure_used']:.6f}`
- AUM robustness: see `model_family_robustness_memo.md`.
- Explainability limitation: nonlinear/regularised model is less directly interpretable than the current transparent prior-plus-learned score.
- Point-in-time audit status: annual expanding walk-forward uses only dates before each scored year; no 2025+ data.
- Replacement recommendation: do not replace automatically; run a dedicated promotion audit first.
"""
        (report_dir / "model_promotion_recommendation.md").write_text(text, encoding="utf-8")


def main() -> None:
    config = StrategyConfig()
    summary = run_summary(config)
    write_memo(summary, config)
    print(f"Wrote {config.output_dir / 'model_family_robustness_summary.csv'}")
    print(f"Wrote {config.output_dir / 'report_ready' / 'model_family_robustness_memo.md'}")


if __name__ == "__main__":
    main()
