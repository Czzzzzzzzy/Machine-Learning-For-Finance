# Phase 2 Recommended Point-In-Time Audit

Recommended challenger: `phase2_g5_05_expanding`.

1. No 2025+ data: `True`; max cached volatility-scaled panel date is `2024-12-31`.
2. Features observable by 15:50 ET on day t: `True`; Phase 2 uses the existing ranked feature set.
3. No use of day-t close/high/low unless shifted appropriately: `True`; close-to-close, volatility, ADV20, and liquidity features are shifted in the existing feature pipeline.
4. Earnings timing still respects AMC/BMO through `strat_trading_date`: `True`; no Phase 2 variant changes earnings filtering.
5. Short-interest features use provided point-in-time proxies plus one-trading-day decision lag: `True`; no Phase 2 variant changes `dsi_lag1`, `dtcn_lag1`, or `ddtcn_lag1`.
6. Target transformation uses future return only as historical training label: `True`.
7. Volatility denominator is trailing and shifted: `True`; `vol20` is trailing close-to-close volatility shifted one trading day.
8. Cross-sectional ranks use only same-day available cross-section: `True`; Phase 2 reuses the existing rank columns.
9. Training weights use only past data under walk-forward protocol: `True`; Phase 2 training windows end before the scored year.
