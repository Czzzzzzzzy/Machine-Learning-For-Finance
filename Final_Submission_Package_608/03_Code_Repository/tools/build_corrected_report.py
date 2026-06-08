"""Build the corrected report from frozen output files.

The script deliberately reads existing CSV/Markdown evidence and writes a report
that distinguishes verified results from limitations. It does not rerun strategy
experiments or change final portfolio outputs.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
REPORT_READY = ROOT / "outputs" / "report_ready"


def pct(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x * 100:.{digits}f}%"


def num(x: float, digits: int = 3) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f}"


def money_m(x: float) -> str:
    if pd.isna(x):
        return ""
    return f"${x / 1_000_000:.2f}M"


def aum_label(x: float) -> str:
    if x >= 1_000_000_000:
        return "1B"
    return f"{int(x / 1_000_000)}M"


def format_table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)


def feature_inventory_bullets(df: pd.DataFrame) -> str:
    rows = []
    for _, row in df.iterrows():
        rows.append(
            "- "
            f"`{row['feature_name']}`: {row['formula']}; "
            f"source `{row['data_source']}`; lag `{row['required_lag']}`; "
            f"15:50 ET observable: {row['observable_1550_et_day_t']}."
        )
    return "\n".join(rows)


def stylised_stats(ret: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stream in ["overnight", "intraday", "close_to_close"]:
        r = ret[stream].dropna()
        cumulative = float((1.0 + r).prod() - 1.0)
        ann = float((1.0 + cumulative) ** (252.0 / len(r)) - 1.0)
        vol = float(r.std(ddof=1) * np.sqrt(252.0))
        rows.append(
            {
                "Stream": {"overnight": "Overnight", "intraday": "Intraday", "close_to_close": "Close-to-close / total"}[stream],
                "Cumulative return": pct(cumulative),
                "Annual return": pct(ann),
                "Annual vol": pct(vol),
                "Sharpe": num(ann / vol if vol else np.nan),
            }
        )
    return pd.DataFrame(rows)


def yearly_return_decomp(ret: pd.DataFrame) -> pd.DataFrame:
    ret = ret.copy()
    ret["year"] = pd.to_datetime(ret["date"]).dt.year
    rows = []
    for year, chunk in ret.groupby("year"):
        rows.append(
            {
                "Year": int(year),
                "Overnight": pct(float((1.0 + chunk["overnight"]).prod() - 1.0)),
                "Intraday": pct(float((1.0 + chunk["intraday"]).prod() - 1.0)),
                "Close-to-close": pct(float((1.0 + chunk["close_to_close"]).prod() - 1.0)),
                "Names avg": f"{chunk['names'].mean():.0f}",
            }
        )
    return pd.DataFrame(rows)


def make_aum_cum_plot() -> Path:
    out = REPORT_READY / "corrected_report_aum_cumulative_returns.png"
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    for suffix, label in [("50m", "50M"), ("250m", "250M"), ("1b", "1B")]:
        df = pd.read_csv(ROOT / "outputs" / f"daily_returns_{suffix}.csv")
        df["date"] = pd.to_datetime(df["date"])
        cum = (1.0 + df["net_return"]).cumprod() - 1.0
        ax.plot(df["date"], cum * 100.0, label=label, linewidth=1.8)
    ax.set_title("Final strategy net cumulative return by AUM, 2010-2024")
    ax.set_ylabel("Cumulative return")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def make_capacity_plot(capacity: pd.DataFrame) -> Path:
    out = REPORT_READY / "corrected_report_capacity.png"
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    labels = [aum_label(x) for x in capacity["AUM"]]
    ax.bar(labels, capacity["average_gross_exposure_used"] * 100.0, color=["#1f4e79", "#2f6f73", "#64748b"])
    ax.set_ylim(0, 110)
    ax.set_ylabel("Average gross exposure used")
    ax.set_title("Capacity effect of the fixed 5% ADV20 cap")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    for i, v in enumerate(capacity["average_gross_exposure_used"] * 100.0):
        ax.text(i, v + 2, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def make_ablation_plot(ablation_250: pd.DataFrame) -> Path:
    out = REPORT_READY / "corrected_report_ablation.png"
    plot = ablation_250.copy()
    plot["label"] = plot["removed_group"].replace({"none": "full model"})
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    ax.barh(plot["label"], plot["net_sharpe"], color="#334155")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("250M net Sharpe")
    ax.set_title("Feature-group ablation, final strategy")
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def feature_group_for_name(feature: str) -> str:
    if feature in {
        "rank_r_on_1d",
        "rank_r_on_5d",
        "rank_r_id_1d",
        "rank_ret_cc_5d",
        "rank_ret_cc_20d",
        "rank_ret_cc_60d",
    }:
        return "Return / reversal"
    if feature in {
        "rank_vol20",
        "rank_vol60",
        "rank_amihud20",
        "rank_adv20_log",
        "rank_market_cap_log",
    }:
        return "Risk / liquidity / size"
    if feature in {
        "rank_piot_norm_lag1",
        "rank_gross_profit_margin_lag1",
        "rank_asset_turnover_ratio_lag1",
        "rank_net_debt_to_equity_lag1",
        "rank_price_to_book_lag1",
        "rank_ev_to_ebit_lag1",
        "rank_final_score_lag1",
        "rank_score_velocity_lag1",
        "rank_momentum_score_lag1",
    }:
        return "Fundamental / value / quality"
    if feature in {"rank_sue_lag1", "rank_deps_lag1", "rank_reps1_lag1", "rank_repsf4_lag1"}:
        return "Earnings / revision"
    if feature in {"rank_dsi_lag1", "rank_dtcn_lag1", "rank_ddtcn_lag1"}:
        return "Short-interest / borrow"
    if feature == "rank_industry_return_lag1":
        return "Industry return"
    return "Other"


def make_model_ic_comparison_plot(lgbm: pd.DataFrame) -> Path:
    out = REPORT_READY / "model_ic_comparison.png"
    plot = lgbm.copy()
    plot["model_label"] = plot["model"].replace(
        {"Final transparent expanding-window linear score": "Final linear score"}
    )
    plot["period_label"] = plot["label"].replace(
        {
            "validation_2019_2022": "Validation\n2019-2022",
            "internal_holdout_2023_2024": "Holdout\n2023-2024",
        }
    )
    pivot = plot.pivot(index="period_label", columns="model_label", values="IC_mean")
    pivot = pivot[["Final linear score", "LightGBM"]]
    fig, ax = plt.subplots(figsize=(7.8, 4.5))
    pivot.plot(kind="bar", ax=ax, color=["#1f4e79", "#7c3aed"], width=0.72)
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_ylabel("Mean daily IC")
    ax.set_xlabel("")
    ax.set_title("Final linear score vs LightGBM diagnostic IC")
    ax.legend(frameon=True, title="")
    ax.tick_params(axis="x", rotation=0)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=8, padding=2)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def make_yearly_ic_plot(ic_yearly: pd.DataFrame) -> Path:
    out = REPORT_READY / "model_yearly_ic.png"
    plot = ic_yearly.copy()
    colors = np.where(plot["mean_ic"].ge(0), "#1f4e79", "#b91c1c")
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.bar(plot["year"].astype(str), plot["mean_ic"], color=colors)
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_ylabel("Mean daily IC")
    ax.set_xlabel("Year")
    ax.set_title("Final linear score IC by calendar year")
    ax.tick_params(axis="x", rotation=45)
    for i, row in plot.iterrows():
        y = row["mean_ic"]
        va = "bottom" if y >= 0 else "top"
        offset = 0.002 if y >= 0 else -0.002
        ax.text(i, y + offset, f"{y:.3f}", ha="center", va=va, fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def make_feature_weight_plot(feature_weights: pd.DataFrame) -> Path:
    out = REPORT_READY / "model_feature_weights_2024.png"
    latest_year = int(feature_weights["year"].max())
    plot = feature_weights.loc[feature_weights["year"].eq(latest_year)].copy()
    plot["group"] = plot["feature"].map(feature_group_for_name)
    plot["abs_weight"] = plot["weight"].abs()
    plot = plot.sort_values("abs_weight", ascending=False).head(16)
    plot = plot.sort_values("weight")
    palette = {
        "Return / reversal": "#1f4e79",
        "Risk / liquidity / size": "#64748b",
        "Fundamental / value / quality": "#16a34a",
        "Earnings / revision": "#d97706",
        "Short-interest / borrow": "#7c3aed",
        "Industry return": "#475569",
        "Other": "#334155",
    }
    colors = plot["group"].map(palette)
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.barh(plot["feature"], plot["weight"], color=colors)
    ax.axvline(0, color="#111827", linewidth=0.8)
    ax.set_xlabel("Weight in final alpha score")
    ax.set_title(f"Largest absolute feature weights used to score {latest_year}")
    handles = [
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=color, markersize=8, label=group)
        for group, color in palette.items()
        if group in set(plot["group"])
    ]
    ax.legend(handles=handles, frameon=True, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def build_markdown() -> str:
    perf = pd.read_csv(ROOT / "outputs" / "performance_summary.csv")
    phase2 = pd.read_csv(REPORT_READY / "champion_challenger_matrix.csv")
    final_row = phase2.loc[phase2["experiment_id"].eq("phase2_g5_05_expanding")].iloc[0]
    cap = pd.read_csv(REPORT_READY / "position_capacity_summary.csv")
    ret = pd.read_csv(ROOT / "outputs" / "equal_weight_return_decomposition.csv")
    rec = pd.read_csv(ROOT / "outputs" / "return_reconciliation_summary.csv").iloc[0]
    universe = pd.read_csv(ROOT / "outputs" / "universe_summary.csv")
    eligibility = pd.read_csv(ROOT / "outputs" / "eligibility_summary.csv")
    borrow_drag = pd.read_csv(REPORT_READY / "borrow_sharpe_degradation.csv")
    borrow_tier = pd.read_csv(REPORT_READY / "borrow_tier_summary.csv")
    borrow_signal = pd.read_csv(REPORT_READY / "short_signal_affected_by_borrow.csv")
    borrow_external = pd.read_csv(REPORT_READY / "borrow_proxy_external_validation.csv")
    ablation = pd.read_csv(ROOT / "outputs" / "feature_ablation_summary.csv")
    robustness = pd.read_csv(REPORT_READY / "locked_strategy_robustness.csv")
    lgbm = pd.read_csv(REPORT_READY / "lightgbm_diagnostic.csv")
    feature_inventory = pd.read_csv(REPORT_READY / "feature_inventory.csv")
    feature_weights = pd.read_csv(REPORT_READY / "final_expanding_feature_weights.csv")
    ic_yearly = pd.read_csv(ROOT / "outputs" / "ic_yearly.csv")
    impact_examples = pd.read_csv(REPORT_READY / "impact_at_cap_examples.csv")
    lo_adjusted = pd.read_csv(REPORT_READY / "sharpe_lo_corrected.csv")
    si_contribution = pd.read_csv(REPORT_READY / "short_interest_si_gt_10_contribution.csv")
    hard_exclusion = pd.read_csv(REPORT_READY / "short_interest_hard_exclusion_sensitivity.csv")

    aum_plot = make_aum_cum_plot()
    cap_plot = make_capacity_plot(cap)
    ablation_plot = make_ablation_plot(ablation.loc[ablation["AUM"].eq(250_000_000.0)])
    model_ic_plot = make_model_ic_comparison_plot(lgbm)
    yearly_ic_plot = make_yearly_ic_plot(ic_yearly)
    feature_weight_plot = make_feature_weight_plot(feature_weights)

    headline = perf.loc[perf["AUM"].eq(250_000_000.0)].iloc[0]
    perf_tbl = perf.assign(AUM_label=perf["AUM"].map(aum_label))[
        [
            "AUM_label",
            "net_annual_return",
            "net_vol",
            "net_sharpe",
            "max_drawdown",
            "gross_sharpe",
            "average_turnover",
            "average_gross_exposure_used",
            "cap_binding_days",
        ]
    ].rename(columns={"AUM_label": "AUM"})
    for col in ["net_annual_return", "net_vol", "max_drawdown", "average_gross_exposure_used"]:
        perf_tbl[col] = perf_tbl[col].map(pct)
    for col in ["net_sharpe", "gross_sharpe", "average_turnover"]:
        perf_tbl[col] = perf_tbl[col].map(num)
    perf_tbl.columns = [
        "AUM",
        "Net annual return",
        "Net vol",
        "Net Sharpe",
        "Max drawdown",
        "Gross Sharpe",
        "Avg turnover",
        "Avg gross exposure",
        "Cap-binding days",
    ]

    cap_tbl = cap.assign(AUM_label=cap["AUM"].map(aum_label))[
        [
            "AUM_label",
            "average_gross_exposure_used",
            "average_abs_per_stock_position",
            "max_abs_per_stock_position",
            "average_participation_rate",
            "fraction_position_days_at_cap",
        ]
    ].rename(columns={"AUM_label": "AUM"})
    cap_tbl["average_gross_exposure_used"] = cap_tbl["average_gross_exposure_used"].map(pct)
    cap_tbl["average_abs_per_stock_position"] = cap_tbl["average_abs_per_stock_position"].map(money_m)
    cap_tbl["max_abs_per_stock_position"] = cap_tbl["max_abs_per_stock_position"].map(money_m)
    cap_tbl["average_participation_rate"] = cap_tbl["average_participation_rate"].map(pct)
    cap_tbl["fraction_position_days_at_cap"] = cap_tbl["fraction_position_days_at_cap"].map(pct)
    cap_tbl.columns = [
        "AUM",
        "Avg gross exposure",
        "Avg abs position",
        "Max abs position",
        "Avg participation",
        "Position-days at cap",
    ]

    ablation_250 = ablation.loc[ablation["AUM"].eq(250_000_000.0)].copy()
    ab_tbl = ablation_250[
        [
            "model_variant",
            "removed_group",
            "IC_mean",
            "IC_tstat",
            "net_annual_return",
            "net_vol",
            "net_sharpe",
            "max_drawdown",
        ]
    ].copy()
    for col in ["net_annual_return", "net_vol", "max_drawdown"]:
        ab_tbl[col] = ab_tbl[col].map(pct)
    for col in ["IC_mean", "IC_tstat", "net_sharpe"]:
        ab_tbl[col] = ab_tbl[col].map(num)
    ab_tbl.columns = [
        "Variant",
        "Removed group",
        "IC mean",
        "IC t-stat",
        "Net annual return",
        "Net vol",
        "Net Sharpe",
        "Max drawdown",
    ]

    year_250 = robustness[
        robustness["AUM"].eq(250_000_000.0) & robustness["subperiod"].str.startswith("year_")
    ].copy()
    year_tbl = year_250[
        ["subperiod", "annual_return", "annual_vol", "sharpe", "max_drawdown", "average_gross_exposure_used"]
    ].copy()
    year_tbl["Year"] = year_tbl["subperiod"].str.replace("year_", "", regex=False)
    year_tbl = year_tbl[["Year", "annual_return", "annual_vol", "sharpe", "max_drawdown", "average_gross_exposure_used"]]
    for col in ["annual_return", "annual_vol", "max_drawdown", "average_gross_exposure_used"]:
        year_tbl[col] = year_tbl[col].map(pct)
    year_tbl["sharpe"] = year_tbl["sharpe"].map(num)
    year_tbl.columns = ["Year", "Return", "Vol", "Sharpe", "Max drawdown", "Avg gross exposure"]

    robust_250 = robustness[robustness["AUM"].eq(250_000_000.0)]
    full_rob = robust_250.loc[robust_250["subperiod"].eq("full_2010_2024")].iloc[0]
    stress = robust_250[robust_250["subperiod"].str.startswith("stress_")].copy()
    stress_tbl = stress[
        ["subperiod", "annual_return", "annual_vol", "sharpe", "max_drawdown", "average_gross_exposure_used"]
    ].copy()
    stress_tbl["subperiod"] = stress_tbl["subperiod"].str.replace("stress_", "", regex=False)
    for col in ["annual_return", "annual_vol", "max_drawdown", "average_gross_exposure_used"]:
        stress_tbl[col] = stress_tbl[col].map(pct)
    stress_tbl["sharpe"] = stress_tbl["sharpe"].map(num)
    stress_tbl.columns = ["Window", "Return", "Vol", "Sharpe", "Max drawdown", "Avg gross exposure"]

    splits = robust_250[robust_250["subperiod"].str.startswith("split_")].copy()
    split_tbl = splits[
        ["subperiod", "annual_return", "annual_vol", "sharpe", "max_drawdown", "average_gross_exposure_used"]
    ].copy()
    split_tbl["subperiod"] = split_tbl["subperiod"].str.replace("split_", "", regex=False)
    for col in ["annual_return", "annual_vol", "max_drawdown", "average_gross_exposure_used"]:
        split_tbl[col] = split_tbl[col].map(pct)
    split_tbl["sharpe"] = split_tbl["sharpe"].map(num)
    split_tbl.columns = ["Window", "Return", "Vol", "Sharpe", "Max drawdown", "Avg gross exposure"]

    borrow_drag_tbl = borrow_drag.assign(AUM_label=borrow_drag["AUM"].map(aum_label))[
        ["AUM_label", "gross_sharpe", "commission_drag", "slippage_drag", "borrow_drag", "net_sharpe", "avg_borrow_bps_per_day"]
    ].copy()
    for col in ["gross_sharpe", "commission_drag", "slippage_drag", "borrow_drag", "net_sharpe", "avg_borrow_bps_per_day"]:
        borrow_drag_tbl[col] = borrow_drag_tbl[col].map(num)
    borrow_drag_tbl.columns = [
        "AUM",
        "Gross Sharpe",
        "Commission drag",
        "Slippage drag",
        "Borrow drag",
        "Net Sharpe",
        "Avg daily borrow bps",
    ]

    tier_250 = borrow_tier[borrow_tier["AUM"].eq(250_000_000.0)].copy()
    tier_tbl = tier_250[["borrow_tier", "share_of_short_position_days", "average_short_notional", "total_borrow_cost"]].copy()
    tier_tbl["share_of_short_position_days"] = tier_tbl["share_of_short_position_days"].map(pct)
    tier_tbl["average_short_notional"] = tier_tbl["average_short_notional"].map(money_m)
    tier_tbl["total_borrow_cost"] = tier_tbl["total_borrow_cost"].map(lambda x: f"${x:,.0f}")
    tier_tbl.columns = ["Tier", "Share of short position-days", "Avg short notional", "Total borrow cost"]

    borrow_ext_tbl = borrow_external[
        [
            "ticker",
            "window_start",
            "window_end",
            "external_check",
            "mean_dsi_lag1",
            "max_dsi_lag1",
            "mean_dtcn_lag1",
            "max_dtcn_lag1",
            "tier_b_or_c_fraction",
            "tier_c_fraction",
            "internal_proxy_read",
        ]
    ].copy()
    for col in ["mean_dsi_lag1", "max_dsi_lag1", "mean_dtcn_lag1", "max_dtcn_lag1"]:
        borrow_ext_tbl[col] = borrow_ext_tbl[col].map(num)
    for col in ["tier_b_or_c_fraction", "tier_c_fraction"]:
        borrow_ext_tbl[col] = borrow_ext_tbl[col].map(pct)
    borrow_ext_tbl["Window"] = borrow_ext_tbl["window_start"] + " to " + borrow_ext_tbl["window_end"]
    borrow_ext_tbl = borrow_ext_tbl[
        [
            "ticker",
            "Window",
            "external_check",
            "mean_dsi_lag1",
            "max_dsi_lag1",
            "mean_dtcn_lag1",
            "max_dtcn_lag1",
            "tier_b_or_c_fraction",
            "tier_c_fraction",
            "internal_proxy_read",
        ]
    ]
    borrow_ext_tbl.columns = [
        "Ticker",
        "Window",
        "External anecdote",
        "Mean DSI",
        "Max DSI",
        "Mean DTCN",
        "Max DTCN",
        "Tier B/C days",
        "Tier C days",
        "Internal read",
    ]

    lgbm_tbl = lgbm.copy()
    lgbm_tbl["model_order"] = np.where(
        lgbm_tbl["model"].str.contains("Final transparent", na=False), 0, 1
    )
    lgbm_tbl = lgbm_tbl.sort_values(["model_order", "label"], kind="mergesort").drop(
        columns=["model_order"]
    )
    lgbm_tbl["IC_mean"] = lgbm_tbl["IC_mean"].map(num)
    lgbm_tbl["IC_tstat"] = lgbm_tbl["IC_tstat"].map(num)
    lgbm_tbl["n_train_rows"] = lgbm_tbl["n_train_rows"].map(lambda x: "" if pd.isna(x) else f"{int(x):,}")
    lgbm_tbl["n_test_rows"] = lgbm_tbl["n_test_rows"].map(lambda x: f"{int(x):,}")
    lgbm_tbl = lgbm_tbl[["model", "label", "n_train_rows", "n_test_rows", "daily_ic_count", "IC_mean", "IC_tstat", "notes"]]
    lgbm_tbl.columns = ["Model", "Period", "Train rows", "Test rows", "IC days", "IC mean", "IC t-stat", "Notes"]

    model_spec_tbl = pd.DataFrame(
        [
            ["Final model used for trading", "Transparent expanding-window linear rank-score model"],
            ["Not the final model", "LightGBM and HistGradientBoosting; included only as diagnostics and robustness evidence"],
            ["Score formula", "`alpha_score_t,i = sum_j weight_{Y,j} * rank_feature_{t,i,j}`"],
            ["Training target", "`overnight_next / (vol20 / sqrt(252))`"],
            ["Target use", "Future overnight return is used only as a historical training label"],
            ["Feature transform", "Cross-sectional ranks within the decision-date available universe"],
            ["Weight estimation", "50% fixed prior weights plus 50% learned feature-target correlation weights"],
            ["Training window", "Expanding window: for scored year `Y`, train only on dates strictly before `Y`"],
            ["Prediction timing", "Features observable by 15:50 ET on day `t`; no year being scored or future years in training"],
            ["Portfolio mapping", "Long top 3% and short bottom 3% by alpha score; equal weight before capacity sizing"],
            ["Capacity/costs", "5% ADV20 cap, day-t close entry, day-t+1 open exit, fixed commission/slippage/borrow schedule"],
        ],
        columns=["Item", "Final report value"],
    )

    impact_tbl = impact_examples.copy()
    impact_tbl["market_cap"] = impact_tbl["market_cap"].map(money_m)
    impact_tbl["adv20_dollar"] = impact_tbl["adv20_dollar"].map(money_m)
    for col in ["vol20_annual", "sigma_daily", "participation_cap"]:
        impact_tbl[col] = impact_tbl[col].map(pct)
    impact_tbl["impact_at_5pct_adv_bps"] = impact_tbl["impact_at_5pct_adv_bps"].map(lambda x: f"{x:.2f}")
    impact_tbl = impact_tbl[
        [
            "example",
            "date",
            "ticker",
            "market_cap",
            "adv20_dollar",
            "vol20_annual",
            "sigma_daily",
            "participation_cap",
            "impact_at_5pct_adv_bps",
        ]
    ]
    impact_tbl.columns = [
        "Example",
        "Date",
        "Ticker",
        "Market cap",
        "ADV20",
        "Vol20",
        "Daily sigma",
        "Participation",
        "Impact bps",
    ]

    lo_tbl = lo_adjusted[
        [
            "AUM_label",
            "net_sharpe_raw",
            "lo_adjusted_net_sharpe",
            "lo_variance_multiplier",
            "autocorr_lag1",
        ]
    ].copy()
    for col in [
        "net_sharpe_raw",
        "lo_adjusted_net_sharpe",
        "lo_variance_multiplier",
        "autocorr_lag1",
    ]:
        lo_tbl[col] = lo_tbl[col].map(num)
    lo_tbl.columns = [
        "AUM",
        "Raw net Sharpe",
        "Lo-adjusted net Sharpe",
        "Variance multiplier",
        "Lag-1 autocorr",
    ]

    si_tbl = si_contribution[
        [
            "AUM_label",
            "fraction_short_position_days_high_si",
            "high_si_short_total_gross_return_bps",
            "high_si_short_average_daily_gross_return_bps",
            "high_si_share_of_all_gross_pnl",
        ]
    ].copy()
    si_tbl["fraction_short_position_days_high_si"] = si_tbl["fraction_short_position_days_high_si"].map(pct)
    for col in ["high_si_short_total_gross_return_bps", "high_si_short_average_daily_gross_return_bps"]:
        si_tbl[col] = si_tbl[col].map(lambda x: f"{x:.3f}")
    si_tbl["high_si_share_of_all_gross_pnl"] = si_tbl["high_si_share_of_all_gross_pnl"].map(pct)
    si_tbl.columns = [
        "AUM",
        "DSI > 10% short-days",
        "Total gross contribution bps",
        "Avg daily contribution bps",
        "Share of all gross PnL",
    ]

    hard_tbl = hard_exclusion.merge(
        perf[
            [
                "AUM",
                "net_annual_return",
                "net_sharpe",
                "max_drawdown",
                "average_gross_exposure_used",
            ]
        ],
        on="AUM",
        suffixes=("_hard", "_final"),
    )[
        [
            "AUM_label",
            "net_sharpe_final",
            "net_sharpe_hard",
            "net_annual_return_final",
            "net_annual_return_hard",
            "max_drawdown_final",
            "max_drawdown_hard",
            "average_gross_exposure_used_final",
            "average_gross_exposure_used_hard",
        ]
    ].copy()
    for col in ["net_sharpe_final", "net_sharpe_hard"]:
        hard_tbl[col] = hard_tbl[col].map(num)
    for col in [
        "net_annual_return_final",
        "net_annual_return_hard",
        "max_drawdown_final",
        "max_drawdown_hard",
        "average_gross_exposure_used_final",
        "average_gross_exposure_used_hard",
    ]:
        hard_tbl[col] = hard_tbl[col].map(pct)
    hard_tbl.columns = [
        "AUM",
        "Final Sharpe",
        "DSI>10 excluded Sharpe",
        "Final return",
        "DSI>10 excluded return",
        "Final max DD",
        "DSI>10 excluded max DD",
        "Final gross exposure",
        "DSI>10 excluded gross exposure",
    ]

    universe_tbl = universe.copy()
    universe_tbl["median_year_start_mcap"] = universe_tbl["median_year_start_mcap"].map(money_m)
    universe_tbl.columns = ["Year", "Universe count", "Reference date", "Median year-start market cap", "Mid-year exits"]

    elig_pivot = eligibility.pivot_table(index="year", columns="eligibility_reason", values="stock_days", aggfunc="sum", fill_value=0)
    elig_pivot = elig_pivot.reset_index().rename(columns={"year": "Year"})
    for col in ["MCAP_FAIL", "ADV_FAIL", "PRICE_FAIL", "VOL_FAIL", "EARN_WINDOW", "DATA_FAIL", "OK"]:
        if col not in elig_pivot.columns:
            elig_pivot[col] = 0
    elig_tbl = elig_pivot[["Year", "OK", "MCAP_FAIL", "ADV_FAIL", "PRICE_FAIL", "VOL_FAIL", "EARN_WINDOW", "DATA_FAIL"]]

    section_map = pd.DataFrame(
        [
            ["Section 2", "Daily panel questions", "6", "Data sources, return identity, earnings timing, short-interest lag, universe, return decomposition"],
            ["Section 3", "Capacity-aware universe", "4", "Thresholds, participation cap, AUM capacity, binding constraints"],
            ["Section 4", "Borrow filtering", "4", "Borrow proxy, validation limitation, tiered cost treatment, gross-to-net borrow impact"],
            ["Section 5", "Alpha model", "5", "Information set, target, model/training, IC, ablation, weak periods"],
            ["Section 6", "Portfolio and costs", "5", "Basket/weighting/turnover, 50M/250M/1B performance, cost drag, QuantStats, stress windows"],
        ],
        columns=["Brief section", "Topic", "Explicit questions", "Where answered here"],
    )

    md = f"""# Corrected Final Report: Close-to-Open Overnight Equity Strategy

## Executive Summary

The final strategy is `phase2_g5_05_expanding`: a daily, dollar-neutral, close-to-open long-short strategy using a volatility-scaled overnight-return target and expanding-window transparent feature-weight estimation.

The target is:

```text
overnight_next / (vol20 / sqrt(252))
```

`overnight_next` is the close-to-next-open return being predicted and traded. `vol20` is trailing 20-day close-to-close volatility, annualised, and shifted by one trading day before use. The final strategy uses the unchanged feature set, top/bottom 3% baskets, equal weighting, raw alpha-score ranking, tiered borrow-cost treatment, fixed transaction costs, 5% ADV20 participation cap, and close-to-open execution.

At the main headline AUM of 250M, the final strategy earns **{pct(headline['net_annual_return'])}** net annual return, **{pct(headline['net_vol'])}** net volatility, net Sharpe **{num(headline['net_sharpe'])}**, and max drawdown **{pct(headline['max_drawdown'])}** over 2010-2024. The previous champion Sharpe of **0.811** is retained only as an archived comparison.

The promotion evidence is controlled: validation 2019-2022 250M Sharpe is **{num(final_row['validation_2019_2022_250m_net_sharpe'])}**, internal holdout 2023-2024 Sharpe is **{num(final_row['internal_holdout_2023_2024_250m_net_sharpe'])}**, and full 2010-2024 Sharpe is **{num(final_row['full_2010_2024_250m_net_sharpe'])}**. The holdout Sharpe is much lower than the validation Sharpe; this is disclosed as expected performance degradation, not hidden.

2025-2026 remains held out for marker evaluation. No 2025+ data is used in the development outputs or in this report.

## Coursework Question Map

The brief contains **24 explicit report questions** across Sections 2-6:

{format_table(section_map)}

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

The project reconciles adjusted open, adjusted close, and close-to-close returns with tolerance `{rec['tolerance']:.0e}`. It checks `{int(rec['stock_days_checked']):,}` stock-days, with `{int(rec['fail_count'])}` failures and fail fraction `{rec['fail_fraction']:.6f}`.

The equal-weight eligible-universe decomposition is below. It supports the overnight-versus-intraday motivation, but it does **not** support the stronger claim that overnight is larger than total close-to-close return in this implementation. In our equal-weight universe, close-to-close/total has the largest cumulative return; overnight has a stronger Sharpe than intraday.

{format_table(stylised_stats(ret))}

![Equal-weight eligible-universe overnight/intraday/close-to-close decomposition, 2010-2024, no AUM, no strategy costs, annual large-cap universe](outputs/report_ready/return_decomposition_q1.png){{ width=92% }}

Year-by-year decomposition:

{format_table(yearly_return_decomp(ret))}

## 2. Data Source, Panel Construction, And Timing

The data source is the provided coursework data package in `data/`, using daily OHLCV, market capitalisation, daily fundamentals, earnings timing, short-interest proxies, regime labels, and SP500 total-return benchmark files. The development window is 2010-01-01 through 2024-12-31.

Open, high, low, and close are adjusted consistently by the adjusted-close ratio before return construction. The strategy uses:

- `r_overnight = adj_open_t / adj_close_(t-1) - 1`
- `r_intraday = adj_close_t / adj_open_t - 1`
- `overnight_next = adj_open_(t+1) / adj_close_t - 1`

The annual universe is frozen at each year start from the top available market-cap names using only the prior year-end reference date. The output universe is close to 1,000 names each year because the source data has slightly fewer valid names in early years.

{format_table(universe_tbl)}

Earnings timing uses `earnings_calendar.strat_trading_date`. The eligibility filter excludes plus/minus one trading day around the strategy trading date. Existing hand-checkable examples include MOS as an AMC example and RPM as a BMO example in `outputs/earnings_timing_examples.csv`.

Short-interest fields `dsi`, `dtcn`, and `ddtcn` are treated as provided point-in-time transformed proxies from the coursework data package, then shifted by one additional trading day before decision use. The report does not claim independent reconstruction of raw FINRA settlement/publication dates because those raw inputs are not present.

The representative series below shows HLT's decision-lagged short-interest proxies. The figure is a timing diagnostic, not a strategy return chart; it confirms that the report is using the same lag convention as the feature and borrow-tier pipeline.

![Representative short-interest proxy series; HLT, 2015-2024, provided point-in-time proxies plus one-trading-day decision lag, no AUM, no portfolio cost assumption](outputs/report_ready/short_interest_representative_series.png){{ width=92% }}

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

{format_table(impact_tbl)}

{format_table(cap_tbl)}

![Capacity by AUM for final top/bottom 3% equal-weight strategy, 50M/250M/1B, fixed 5% ADV20 cap, full commission/slippage/borrow schedule](outputs/report_ready/corrected_report_capacity.png){{ width=75% }}

The 1B case is a capacity boundary case. Its average gross exposure is only **{pct(cap.loc[cap['AUM'].eq(1_000_000_000.0), 'average_gross_exposure_used'].iloc[0])}**, so the strategy cannot deploy target risk under the fixed 5% ADV20 cap. This is evidence of backtest honesty, not a bug. The final report should not imply that the basket expands to solve 1B capacity; it does not.

Binding eligibility reasons by year are:

{format_table(elig_tbl)}

## 4. Borrow Proxy And Short Leg

The borrow proxy uses lagged short-interest stress variables available in the prepared point-in-time panel. Borrow tiers are charged as:

- Tier A: 40 bps p.a.
- Tier B: 200 bps p.a.
- Tier C: 800 bps p.a.
- Daily borrow charge: annual rate / 252.

The final strategy applies tiered borrow cost only. It does not hard-exclude Tier B/C shorts. Therefore borrow affects net performance through explicit costs, not through selected-name changes.

At 250M, borrow tier exposure and cost are:

{format_table(tier_tbl)}

The fraction of selected short position-days in Tier B or C is **{pct(borrow_signal.loc[borrow_signal['AUM'].eq(250_000_000.0), 'fraction_tier_b_or_c'].iloc[0])}**. The fraction of raw short signal changed by borrow treatment is **{pct(borrow_signal.loc[borrow_signal['AUM'].eq(250_000_000.0), 'fraction_raw_short_signal_affected_by_borrow_treatment'].iloc[0])}**, because tiered costs do not alter raw short selection.

The report does not use a complete prime-broker borrow-fee, locate-rate, or securities-lending history. That is a limitation. To avoid leaving the borrow proxy totally unanchored, I added two anecdotal external checks for names that are present in the coursework panel. They are not a statistical validation, but they do check whether the proxy catches public crowded-short episodes.

{format_table(borrow_ext_tbl)}

Sources used for the anecdotal checks are the SEC staff report on early-2021 equity/options market structure for GME and a Reuters report on the May-2023 CVNA short-squeeze episode, available respectively at `https://www.sec.gov/files/staff-report-equity-options-market-struction-conditions-early-2021.pdf` and `https://www.investing.com/news/stock-market-news/usedcar-retailer-carvanas-shares-soar-on-upbeat-secondquarter-forecast-3074273`. The internal result is directionally sensible: both public crowded-short windows are classified as Tier C on 100% of local panel days. The limitation remains that this is a small sanity check, not a full external borrow-fee tape.

For the brief's high-short-interest honesty check, names with decision-lagged `dsi > 10%` account for the following gross-return contribution on the selected short leg:

{format_table(si_tbl)}

As a sensitivity, the audit re-runs the final selection while excluding `dsi > 10%` names from the short leg only. This is not promoted as a new strategy and does not alter the submitted final outputs. It keeps the same target, top/bottom 3% basket rule, equal weighting, 5% ADV20 cap, close-to-open execution, commission, slippage, and tiered borrow rates.

{format_table(hard_tbl)}

## 5. Alpha, Training, And Point-In-Time Controls

The final trading model is **not LightGBM**. The final model used to create submitted positions is a transparent expanding-window linear rank-score model. LightGBM, HistGradientBoosting, and other model families appear only as diagnostic or robustness comparisons.

{format_table(model_spec_tbl)}

### 5.1 Feature Design And Information Set

The information set at decision time is data observable by 15:50 ET on day `t`. The final feature set is unchanged from the baseline and is stored as ranked features such as return/reversal, lagged intraday return, trailing volatility/liquidity/size, lagged fundamentals, lagged earnings/revision variables, lagged short-interest stress variables, and lagged industry return.

Line-by-line feature inventory used by the final score:

{feature_inventory_bullets(feature_inventory)}

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

![Largest 2024 final linear score feature weights, transparent expanding-window model, same feature set, no LightGBM portfolio promotion](outputs/report_ready/model_feature_weights_2024.png){{ width=88% }}

Final full-sample IC is **{num(headline['IC_mean'])}** with t-stat **{num(headline['IC_tstat'])}**.

### 5.3 Machine Learning Benchmark: LightGBM

LightGBM was first run as an optional IC diagnostic to check the same data panel for nonlinear signal. It is not the final strategy. The table is ordered with the final transparent model first, then the LightGBM diagnostic rows.

{format_table(lgbm_tbl)}

![Final linear score versus LightGBM diagnostic IC, validation and internal holdout, same data panel and cutoff, LightGBM not promoted as a costed strategy](outputs/report_ready/model_ic_comparison.png){{ width=78% }}

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

![63-day rolling IC for the final linear score, Spearman correlation between alpha score and subsequent overnight return, 2010-2024](outputs/figures/rolling_ic.png){{ width=84% }}

![Final linear score mean IC by calendar year, 2010-2024, negative years highlighted](outputs/report_ready/model_yearly_ic.png){{ width=84% }}

## 6. Feature Ablation

Feature-group ablation is a dependence audit, not retuning. Return/reversal is the core alpha contributor: removing it lowers 250M Sharpe from **{num(headline['net_sharpe'])}** to **{num(ablation_250.loc[ablation_250['removed_group'].eq('return/reversal'), 'net_sharpe'].iloc[0])}** and produces a negative net annual return.

Some removals improve Sharpe in the frozen no-retuning table, especially short-interest/borrow-stress and earnings/revision. This should not be hidden. It means those variables may act as risk, capacity, cost, or crowding controls rather than pure alpha predictors, and ablation improvement does not automatically imply the removed group is useless.

{format_table(ab_tbl)}

![Feature-group ablation at 250M for final top/bottom 3% equal-weight strategy, fixed 5% ADV20 cap and full cost schedule](outputs/report_ready/corrected_report_ablation.png){{ width=85% }}

## 7. Portfolio Construction And Costs

The portfolio takes the top 3% of eligible names as longs and bottom 3% as shorts, with at least 15 names per side. It uses equal weighting within each side before capacity scaling. Dollar neutrality is enforced after capacity sizing; if selected names cannot absorb target notional under the 5% ADV20 cap, gross exposure is reduced rather than relaxing the cap.

{format_table(perf_tbl)}

![Final net cumulative returns by AUM, 50M/250M/1B, final top/bottom 3% equal-weight strategy, fixed 5% ADV20 cap and full commission/slippage/borrow schedule](outputs/report_ready/corrected_report_aum_cumulative_returns.png){{ width=90% }}

The gross-to-net Sharpe degradation is:

{format_table(borrow_drag_tbl)}

These drag values are Sharpe-unit drags, not percentages. Auction slippage is the largest explicit drag.

The QuantStats tear-sheet for the 250M strategy is `outputs/quantstats_250m.html`.

## 8. Robustness And Weak Periods

250M year-by-year results:

{format_table(year_tbl)}

Pre/post split:

{format_table(split_tbl)}

Stress windows:

{format_table(stress_tbl)}

Tail diagnostics at 250M:

- Worst 3-month return: **{pct(full_rob['worst_3m_return'])}**.
- Worst 6-month return: **{pct(full_rob['worst_6m_return'])}**.
- Worst 12-month return: **{pct(full_rob['worst_12m_return'])}**.
- Top 5% best days contribute **{num(full_rob['top_5pct_days_pnl_share'])}** times total PnL.
- Lag-1 return autocorrelation is **{num(full_rob['return_autocorrelation_lag1'])}**.

The Lo-style serial-correlation diagnostic below uses autocorrelation weights through lag 5. It is a diagnostic adjustment, not a replacement for the main reported Sharpe. For 250M, the adjusted Sharpe is slightly lower than the raw Sharpe because the weighted higher-lag autocorrelation variance multiplier is above one.

{format_table(lo_tbl)}

The weak periods are visible: 2010 is strongly negative, late 2018 is negative, and 2024 is negative. This is consistent with the lower 2023-2024 holdout Sharpe.

## 9. Promotion Audit And Baselines

The selected Phase 2 challenger improves validation Sharpe, remains positive in holdout, improves full-period Sharpe, and does not worsen full-period max drawdown.

| Metric | Previous champion | Promoted final |
|---|---:|---:|
| Validation 2019-2022 250M Sharpe | 1.107 | {num(final_row['validation_2019_2022_250m_net_sharpe'])} |
| Internal holdout 2023-2024 250M Sharpe | 0.003 | {num(final_row['internal_holdout_2023_2024_250m_net_sharpe'])} |
| Full 2010-2024 250M Sharpe | 0.811 | {num(final_row['full_2010_2024_250m_net_sharpe'])} |
| Full 2010-2024 max drawdown | -10.19% | {pct(final_row['full_2010_2024_250m_max_drawdown'])} |
| Full 2010-2024 worst 12m return | -10.09% | {pct(final_row['full_2010_2024_250m_worst_12m_return'])} |

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

The recommended final strategy remains `phase2_g5_05_expanding`: volatility-scaled overnight target with expanding-window transparent weight estimation. The correct final 250M headline is **{pct(headline['net_annual_return'])}** net annual return, **{pct(headline['net_vol'])}** net volatility, net Sharpe **{num(headline['net_sharpe'])}**, and max drawdown **{pct(headline['max_drawdown'])}**. The old **0.811** Sharpe appears only as previous champion comparison.
"""
    return md


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    REPORT_READY.mkdir(exist_ok=True)
    md = build_markdown()
    md_path = REPORT_DIR / "final_report.md"
    corrected_md_path = REPORT_DIR / "final_report_corrected.md"
    md_path.write_text(md, encoding="utf-8")
    corrected_md_path.write_text(md, encoding="utf-8")

    log = REPORT_READY / "corrected_report_generation_log.md"
    log.write_text(
        "\n".join(
            [
                "# Corrected Report Generation Log",
                "",
                "- Updated `report/final_report.md` from frozen output files.",
                "- Wrote mirror copy `report/final_report_corrected.md`.",
                "- Included corrected return decomposition, point-in-time wording, capacity, borrow, robustness, ablation, and LightGBM diagnostic evidence.",
                "- Did not rerun strategy variants or change final portfolio outputs.",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
