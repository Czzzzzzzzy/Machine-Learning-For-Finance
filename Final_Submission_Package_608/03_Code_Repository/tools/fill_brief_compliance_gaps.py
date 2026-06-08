"""Generate brief-specific compliance evidence for the final C2O package.

This script adds diagnostics requested by the coursework brief without changing
the promoted final strategy outputs.  It reads the frozen final daily returns,
positions, scored panel, and point-in-time source data, then writes report-ready
figures/tables for:

- representative short-interest proxy time series,
- square-root impact examples at the fixed 5% ADV20 cap,
- Lo-style serial-correlation-adjusted Sharpe,
- SI > 10% short contribution, and
- a hard-exclusion sensitivity that removes SI > 10% names from the short leg.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from c2o_strategy.config import StrategyConfig
from c2o_strategy.experiments import basket_size, size_baskets
from c2o_strategy.final_strategy import (
    build_position_frame,
    final_spec,
    performance_row,
    position_columns,
)
from c2o_strategy.metrics import sharpe_ratio
from c2o_strategy.portfolio import COMMISSION_ROUND_TRIP, SLIPPAGE_ROUND_TRIP


REPORT_READY = ROOT / "outputs" / "report_ready"
SCORED_CACHE = ROOT / "outputs" / ".phase2_v1_scored_expanding_prior50_learned50_20241231.parquet"
AUMS = (50_000_000.0, 250_000_000.0, 1_000_000_000.0)


def pct(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x * 100:.{digits}f}%"


def num(x: float, digits: int = 3) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f}"


def aum_label(aum: float) -> str:
    return "1b" if int(aum) == 1_000_000_000 else f"{int(aum / 1_000_000)}m"


def display_aum(aum: float) -> str:
    return "1B" if int(aum) == 1_000_000_000 else f"{int(aum / 1_000_000)}M"


def load_scored_panel() -> pd.DataFrame:
    columns = [
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
        "alpha_score",
        "predicted_alpha_return",
    ]
    if not SCORED_CACHE.exists():
        raise FileNotFoundError(
            f"Missing final scored cache: {SCORED_CACHE}. Run final reproduction first."
        )
    scored = pd.read_parquet(SCORED_CACHE, columns=columns)
    scored["date"] = pd.to_datetime(scored["date"])
    return scored


def lagged_short_interest() -> pd.DataFrame:
    all_data = pd.read_parquet(
        ROOT / "data" / "all_data.parquet",
        columns=["stock_id", "date", "dsi", "dtcn", "ddtcn", "short_interest", "market_cap"],
    )
    all_data["date"] = pd.to_datetime(all_data["date"])
    all_data = all_data.sort_values(["stock_id", "date"], kind="mergesort")
    for column in ["dsi", "dtcn", "ddtcn", "short_interest"]:
        all_data[f"{column}_lag1_decision"] = all_data.groupby("stock_id")[column].shift(1)
    return all_data.rename(columns={"stock_id": "instrument_id"})


def make_short_interest_plot(si: pd.DataFrame) -> None:
    examples = pd.read_csv(ROOT / "outputs" / "short_interest_lag_examples.csv")
    example = examples.iloc[0]
    instrument_id = int(example["instrument_id"])
    ticker = str(example["ticker"])
    series = si.loc[
        si["instrument_id"].eq(instrument_id),
        ["date", "dsi_lag1_decision", "dtcn_lag1_decision", "ddtcn_lag1_decision"],
    ].dropna(subset=["dsi_lag1_decision", "dtcn_lag1_decision"], how="all")
    series = series.loc[series["date"].between("2015-01-01", "2024-12-31")]

    out = REPORT_READY / "short_interest_representative_series.png"
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 7.2), sharex=True)
    plot_specs = [
        ("dsi_lag1_decision", "DSI lagged one decision day"),
        ("dtcn_lag1_decision", "DTCN lagged one decision day"),
        ("ddtcn_lag1_decision", "DDTCN lagged one decision day"),
    ]
    for ax, (column, label) in zip(axes, plot_specs):
        ax.plot(series["date"], series[column], linewidth=1.1, color="#1f4e79")
        ax.axhline(0, color="#6b7280", linewidth=0.8)
        ax.set_ylabel(label)
        ax.grid(True, alpha=0.25)
    axes[0].set_title(
        f"Representative short-interest proxy series: {ticker}, decision-lagged values"
    )
    axes[-1].set_xlabel("Date")
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)

    note = REPORT_READY / "short_interest_representative_series.md"
    note.write_text(
        "\n".join(
            [
                "# Representative Short-Interest Proxy Series",
                "",
                f"Ticker: `{ticker}`; instrument_id: `{instrument_id}`.",
                "",
                "The source `all_data.parquet` short-interest proxies are treated as",
                "already point-in-time transformed by the coursework data package. The",
                "plotted values apply the strategy's additional one-trading-day decision",
                "lag before decision use.",
                "",
                f"Figure: `{out.relative_to(ROOT)}`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def impact_examples(scored: pd.DataFrame, si: pd.DataFrame) -> pd.DataFrame:
    del si
    market_cap = pd.read_parquet(
        ROOT / "data" / "prices.parquet",
        columns=["instrument_id", "date", "market_cap"],
    )
    market_cap["date"] = pd.to_datetime(market_cap["date"])
    market_cap = market_cap.dropna(subset=["market_cap"])
    eligible = scored.loc[
        scored["is_trade_eligible"] & scored["adv20"].gt(0) & scored["vol20"].gt(0),
        ["date", "instrument_id", "ticker", "adv20", "vol20"],
    ].merge(market_cap, on=["instrument_id", "date"], how="left")
    eligible = eligible.dropna(subset=["market_cap"])
    ref_date = eligible["date"].max()
    day = eligible.loc[eligible["date"].eq(ref_date)].copy()
    quantiles = {
        "typical_mid_cap": day["market_cap"].quantile(0.50),
        "typical_large_cap": day["market_cap"].quantile(0.90),
    }
    rows = []
    for label, target_mcap in quantiles.items():
        row = day.loc[(day["market_cap"] - target_mcap).abs().idxmin()]
        sigma_daily = float(row["vol20"]) / np.sqrt(252.0)
        participation = 0.05
        impact = 0.7 * sigma_daily * np.sqrt(participation)
        rows.append(
            {
                "example": label,
                "date": ref_date.date().isoformat(),
                "ticker": row["ticker"],
                "instrument_id": int(row["instrument_id"]),
                "market_cap": float(row["market_cap"]),
                "adv20_dollar": float(row["adv20"]),
                "vol20_annual": float(row["vol20"]),
                "sigma_daily": sigma_daily,
                "participation_cap": participation,
                "sqrt_impact_coefficient": 0.7,
                "impact_at_5pct_adv_bps": impact * 10_000.0,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(REPORT_READY / "impact_at_cap_examples.csv", index=False)

    md = out.copy()
    for col in ["market_cap", "adv20_dollar"]:
        md[col] = md[col].map(lambda x: f"${x / 1_000_000:,.1f}M")
    for col in ["vol20_annual", "sigma_daily", "participation_cap"]:
        md[col] = md[col].map(lambda x: pct(float(x)))
    md["impact_at_5pct_adv_bps"] = md["impact_at_5pct_adv_bps"].map(lambda x: f"{x:.2f}")
    (REPORT_READY / "impact_at_cap_examples.md").write_text(
        "\n".join(
            [
                "# Square-Root Impact Examples At 5% ADV20",
                "",
                "These examples do not alter realised performance. The submitted",
                "backtest keeps the fixed brief cost schedule of 0.5 bps commission per",
                "leg and 1.5 bps auction slippage per leg. The calculation below is a",
                "diagnostic reconciliation using `0.7 * sigma_daily * sqrt(0.05)`.",
                "",
                md.to_markdown(index=False),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out


def lo_adjusted_sharpe(max_lag: int = 5) -> pd.DataFrame:
    rows = []
    for aum in AUMS:
        label = aum_label(aum)
        daily = pd.read_csv(ROOT / "outputs" / f"daily_returns_{label}.csv")
        returns = daily["net_return"].astype(float).dropna()
        raw = sharpe_ratio(returns)
        autocorrs = [float(returns.autocorr(lag=k)) for k in range(1, max_lag + 1)]
        weighted_sum = sum(
            (1.0 - k / (max_lag + 1.0)) * autocorrs[k - 1] for k in range(1, max_lag + 1)
        )
        variance_multiplier = 1.0 + 2.0 * weighted_sum
        adjusted = raw / np.sqrt(variance_multiplier) if variance_multiplier > 0 else np.nan
        rows.append(
            {
                "AUM": aum,
                "AUM_label": display_aum(aum),
                "net_sharpe_raw": raw,
                "lo_max_lag": max_lag,
                "lo_variance_multiplier": variance_multiplier,
                "lo_adjusted_net_sharpe": adjusted,
                "autocorr_lag1": autocorrs[0],
                "autocorr_lag2": autocorrs[1],
                "autocorr_lag3": autocorrs[2],
                "autocorr_lag4": autocorrs[3],
                "autocorr_lag5": autocorrs[4],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(REPORT_READY / "sharpe_lo_corrected.csv", index=False)

    md = out[
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
        md[col] = md[col].map(num)
    md.columns = ["AUM", "Raw net Sharpe", "Lo-adjusted net Sharpe", "Variance multiplier", "Lag-1 autocorr"]
    (REPORT_READY / "sharpe_lo_corrected.md").write_text(
        "\n".join(
            [
                "# Lo-Adjusted Sharpe Diagnostic",
                "",
                f"Uses Newey-West-style autocorrelation weights through lag `{max_lag}`:",
                "`1 + 2 * sum((1 - k/(q+1)) * rho_k)`.",
                "",
                md.to_markdown(index=False),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out


def short_interest_contribution(si: pd.DataFrame) -> pd.DataFrame:
    rows = []
    lag = si[["instrument_id", "date", "dsi_lag1_decision"]]
    for aum in AUMS:
        label = aum_label(aum)
        positions = pd.read_parquet(ROOT / "outputs" / f"positions_{label}.parquet")
        positions["date"] = pd.to_datetime(positions["date"])
        merged = positions.merge(lag, on=["instrument_id", "date"], how="left")
        shorts = merged.loc[merged["side"].eq("SHORT")].copy()
        high = shorts.loc[shorts["dsi_lag1_decision"].gt(0.10)].copy()
        all_gross_pnl = float(merged["gross_pnl"].sum())
        short_gross_pnl = float(shorts["gross_pnl"].sum())
        high_gross_pnl = float(high["gross_pnl"].sum())
        daily_days = len(pd.read_csv(ROOT / "outputs" / f"daily_returns_{label}.csv"))
        rows.append(
            {
                "AUM": aum,
                "AUM_label": display_aum(aum),
                "threshold_dsi": 0.10,
                "short_position_days": int(len(shorts)),
                "high_si_short_position_days": int(len(high)),
                "fraction_short_position_days_high_si": float(len(high) / len(shorts)) if len(shorts) else np.nan,
                "high_si_short_total_gross_pnl": high_gross_pnl,
                "high_si_short_total_gross_return_bps": high_gross_pnl / aum * 10_000.0,
                "high_si_short_average_daily_gross_return_bps": high_gross_pnl / aum / daily_days * 10_000.0,
                "high_si_share_of_all_gross_pnl": high_gross_pnl / all_gross_pnl if all_gross_pnl else np.nan,
                "high_si_share_of_short_gross_pnl": high_gross_pnl / short_gross_pnl if short_gross_pnl else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(REPORT_READY / "short_interest_si_gt_10_contribution.csv", index=False)
    return out


def choose_baskets_excluding_high_si(
    day: pd.DataFrame, aum: float, config: StrategyConfig
) -> tuple[pd.DataFrame, pd.DataFrame]:
    spec = final_spec()
    eligible = day.loc[
        day["is_trade_eligible"] & day["alpha_score"].notna() & day["overnight_next"].notna()
    ].copy()
    if len(eligible) < config.min_basket_size * 2:
        return eligible.iloc[0:0], eligible.iloc[0:0]

    long_count = basket_size(len(eligible), spec.long_fraction, config)
    short_count = basket_size(len(eligible), spec.short_fraction, config)
    if long_count + short_count > len(eligible):
        scale = len(eligible) / float(long_count + short_count)
        long_count = max(config.min_basket_size, int(np.floor(long_count * scale)))
        short_count = max(config.min_basket_size, int(np.floor(short_count * scale)))

    ranked = eligible.sort_values("alpha_score", kind="mergesort")
    longs = ranked.tail(long_count)
    short_pool = ranked.loc[~ranked["instrument_id"].isin(longs["instrument_id"])].copy()
    short_pool = short_pool.loc[~short_pool["dsi_lag1_decision"].gt(0.10)]
    if len(short_pool) < config.min_basket_size:
        return eligible.iloc[0:0], eligible.iloc[0:0]
    shorts = short_pool.sort_values("alpha_score", kind="mergesort").head(min(short_count, len(short_pool)))
    return longs, shorts


def hard_exclusion_backtest(scored: pd.DataFrame, si: pd.DataFrame) -> pd.DataFrame:
    config = StrategyConfig()
    spec = final_spec()
    lag = si[["instrument_id", "date", "dsi_lag1_decision"]]
    panel = scored.merge(lag, on=["instrument_id", "date"], how="left")
    needed = [
        "date",
        "instrument_id",
        "ticker",
        "alpha_score",
        "predicted_alpha_return",
        "overnight_next",
        "adv20",
        "vol20",
        "borrow_tier",
        "borrow_rate_annual",
        "is_trade_eligible",
        "dsi_lag1_decision",
    ]
    work = panel[needed].sort_values("date", kind="mergesort")
    rows = []
    position_frames = []

    for aum in AUMS:
        daily_rows = []
        position_frames.clear()
        for date, day in work.groupby("date", sort=True):
            longs, shorts = choose_baskets_excluding_high_si(day, aum, config)
            if longs.empty or shorts.empty:
                daily_rows.append(
                    {
                        "date": date,
                        "gross_return": 0.0,
                        "commission_cost": 0.0,
                        "slippage_cost": 0.0,
                        "borrow_cost": 0.0,
                        "net_return": 0.0,
                        "turnover": 0.0,
                        "gross_exposure": 0.0,
                        "cap_binding": False,
                        "n_long": 0,
                        "n_short": 0,
                    }
                )
                continue

            long_notional, short_notional, daily_cap_binding = size_baskets(
                longs, shorts, aum, config, spec
            )
            long_weights = long_notional / aum
            short_weights = -short_notional / aum
            gross_exposure = float(long_weights.sum() + np.abs(short_weights).sum())
            gross_return = float(
                np.dot(long_weights, longs["overnight_next"].to_numpy(dtype=float))
                + np.dot(short_weights, shorts["overnight_next"].to_numpy(dtype=float))
            )
            commission_cost = gross_exposure * COMMISSION_ROUND_TRIP
            slippage_cost = gross_exposure * SLIPPAGE_ROUND_TRIP
            borrow_rates = shorts["borrow_rate_annual"].fillna(0.004).to_numpy(dtype=float)
            borrow_cost = float(np.dot(np.abs(short_weights), borrow_rates / 252.0))
            net_return = gross_return - commission_cost - slippage_cost - borrow_cost

            daily_rows.append(
                {
                    "date": date,
                    "gross_return": gross_return,
                    "commission_cost": commission_cost,
                    "slippage_cost": slippage_cost,
                    "borrow_cost": borrow_cost,
                    "net_return": net_return,
                    "turnover": 2.0 * gross_exposure,
                    "gross_exposure": gross_exposure,
                    "cap_binding": daily_cap_binding,
                    "n_long": int(len(longs)),
                    "n_short": int(len(shorts)),
                }
            )

            long_frame = build_position_frame(
                longs,
                "LONG",
                long_notional,
                long_weights,
                aum,
                config,
                date,
                daily_cap_binding,
                target_count=len(longs),
            )
            short_frame = build_position_frame(
                shorts,
                "SHORT",
                -short_notional,
                short_weights,
                aum,
                config,
                date,
                daily_cap_binding,
                target_count=len(shorts),
            )
            position_frames.append(pd.concat([long_frame, short_frame], ignore_index=True))

        daily = pd.DataFrame(daily_rows).sort_values("date")
        perf = performance_row(daily, aum)
        perf["strategy_name"] = "hard_exclude_dsi_gt_10pct_short_leg_sensitivity"
        perf["AUM_label"] = display_aum(aum)
        rows.append(perf)

    out = pd.DataFrame(rows)
    out.to_csv(REPORT_READY / "short_interest_hard_exclusion_sensitivity.csv", index=False)
    return out


def write_borrow_sensitivity_md(contrib: pd.DataFrame, hard: pd.DataFrame) -> None:
    final_perf = pd.read_csv(ROOT / "outputs" / "performance_summary.csv")
    hard_compare = hard.merge(
        final_perf[["AUM", "net_sharpe", "net_annual_return", "max_drawdown", "average_gross_exposure_used"]],
        on="AUM",
        how="left",
        suffixes=("_hard_exclusion", "_final"),
    )
    display = hard_compare[
        [
            "AUM_label",
            "net_sharpe_final",
            "net_sharpe_hard_exclusion",
            "net_annual_return_final",
            "net_annual_return_hard_exclusion",
            "max_drawdown_final",
            "max_drawdown_hard_exclusion",
            "average_gross_exposure_used_final",
            "average_gross_exposure_used_hard_exclusion",
        ]
    ].copy()
    for col in ["net_sharpe_final", "net_sharpe_hard_exclusion"]:
        display[col] = display[col].map(num)
    for col in [
        "net_annual_return_final",
        "net_annual_return_hard_exclusion",
        "max_drawdown_final",
        "max_drawdown_hard_exclusion",
        "average_gross_exposure_used_final",
        "average_gross_exposure_used_hard_exclusion",
    ]:
        display[col] = display[col].map(pct)
    display.columns = [
        "AUM",
        "Final Sharpe",
        "Hard-exclusion Sharpe",
        "Final return",
        "Hard-exclusion return",
        "Final max DD",
        "Hard-exclusion max DD",
        "Final gross exposure",
        "Hard-exclusion gross exposure",
    ]

    contrib_display = contrib[
        [
            "AUM_label",
            "fraction_short_position_days_high_si",
            "high_si_short_total_gross_return_bps",
            "high_si_short_average_daily_gross_return_bps",
            "high_si_share_of_all_gross_pnl",
        ]
    ].copy()
    contrib_display["fraction_short_position_days_high_si"] = contrib_display[
        "fraction_short_position_days_high_si"
    ].map(pct)
    for col in ["high_si_short_total_gross_return_bps", "high_si_short_average_daily_gross_return_bps"]:
        contrib_display[col] = contrib_display[col].map(lambda x: f"{x:.3f}")
    contrib_display["high_si_share_of_all_gross_pnl"] = contrib_display[
        "high_si_share_of_all_gross_pnl"
    ].map(pct)
    contrib_display.columns = [
        "AUM",
        "Short position-days with DSI > 10%",
        "Total gross-return contribution (bps)",
        "Average daily gross-return contribution (bps)",
        "Share of all gross PnL",
    ]

    (REPORT_READY / "short_interest_borrow_sensitivity.md").write_text(
        "\n".join(
            [
                "# Short-Interest Borrow Sensitivity",
                "",
                "The final promoted strategy uses tiered borrow costs only and does not",
                "exclude high-short-interest names from selection. This diagnostic keeps",
                "the same alpha score, top/bottom 3% basket rule, equal weighting, 5%",
                "ADV20 cap, close-to-open execution, commission, slippage, and tiered",
                "borrow charges, then asks what changes if the short leg excludes names",
                "with decision-lagged DSI above 10%.",
                "",
                "## Contribution Of DSI > 10% Shorts",
                "",
                contrib_display.to_markdown(index=False),
                "",
                "## Hard-Exclusion Sensitivity",
                "",
                display.to_markdown(index=False),
                "",
                "This sensitivity is not promoted as a new strategy. It is included to",
                "answer the brief's borrow-honesty question and to show that the final",
                "reported results are not produced by relaxing borrow or execution costs.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_gap_fill_log() -> None:
    (REPORT_READY / "brief_compliance_gap_fill_log.md").write_text(
        "\n".join(
            [
                "# Brief Compliance Gap Fill Log",
                "",
                "Generated additional report-ready evidence without changing final",
                "strategy outputs or assumptions.",
                "",
                "Files added:",
                "",
                "- `short_interest_representative_series.png` and `.md`",
                "- `impact_at_cap_examples.csv` and `.md`",
                "- `sharpe_lo_corrected.csv` and `.md`",
                "- `short_interest_si_gt_10_contribution.csv`",
                "- `short_interest_hard_exclusion_sensitivity.csv`",
                "- `short_interest_borrow_sensitivity.md`",
                "",
                "The realised final portfolio still uses the promoted",
                "`phase2_g5_05_expanding` configuration with unchanged transaction costs,",
                "borrow tiers, 5% ADV20 cap, close-to-open execution, and 2024-12-31",
                "development cutoff.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    REPORT_READY.mkdir(parents=True, exist_ok=True)
    scored = load_scored_panel()
    si = lagged_short_interest()
    make_short_interest_plot(si)
    impact_examples(scored, si)
    lo_adjusted_sharpe()
    contribution = short_interest_contribution(si)
    hard = hard_exclusion_backtest(scored, si)
    write_borrow_sensitivity_md(contribution, hard)
    write_gap_fill_log()
    print("Wrote brief compliance gap-fill evidence to outputs/report_ready")


if __name__ == "__main__":
    main()
