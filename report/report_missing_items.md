# Report Missing Items

The final report was regenerated from promoted final outputs in `outputs/`, `outputs/report_ready/`, and the preserved archives. The submitted metrics for performance, capacity, cost degradation, borrow tiers, feature ablation, earnings timing, short-interest lag examples, and reproducibility are present.

| Item | Missing from frozen outputs | Report treatment |
|---|---|---|
| External borrow validation | No independent external borrow-fee or locate-rate source is present for validating the proxy thresholds. | The report defines the deterministic proxy, reports tier shares and costs, and labels external validation as unavailable. |
| Raw short-interest publication-date audit | Frozen outputs contain lag examples from the processed `all_data` panel, but not raw FINRA settlement and publication dates. | The report states that the strategy uses provided point-in-time proxies and adds a one-trading-day decision lag; it does not claim raw FINRA reconstruction. |
| Separate square-root impact estimate at the 5% ADV20 cap | Final outputs report fixed auction slippage drag and realized participation, but do not export a separate impact-at-cap estimate. | The report uses the fixed brief cost schedule and realized participation/cap-binding evidence; it does not introduce a new impact model. |
| 2025-2026 live validation | 2025-2026 remains outside the development cutoff. | The report treats those years as held out for marker evaluation. |
