# Volatility-scaled Target Point-in-time Audit

Audit date: 2026-05-15.

Candidate: `E_target_transform / volatility_scaled_overnight_return`.

## Audit Decision

**Pass.** The candidate can be considered for final-strategy promotion from a point-in-time perspective. The volatility-scaled transformation changes the historical training target only; it does not add new contemporaneous features, does not use full-sample volatility, does not use future close/high/low in the feature set, and the cached experiment panels are capped at `2024-12-31`.

## 1. Target Definition

In `src/c2o_strategy/experiments.py::add_target_transform`, the candidate target is defined as:

```python
daily_vol = (eligible["vol20"] / np.sqrt(252.0)).replace(0.0, np.nan)
target = eligible["overnight_next"] / daily_vol
```

So the training label is:

```text
vol_scaled_target = overnight_next / (vol20 / sqrt(252))
```

where `overnight_next = adj_open_(t+1) / adj_close_t - 1` is the realised close-to-next-open return being predicted.

## 2. Volatility Denominator

The denominator is `vol20 / sqrt(252)`, converting the annualised `vol20` field back to a daily volatility scale.

`vol20` is created in `src/c2o_strategy/data.py::build_return_panel` as:

```python
panel["vol20"] = grouped["r_close_close"].transform(
    lambda x: x.rolling(20, min_periods=10).std().shift(1) * np.sqrt(252.0)
)
```

Thus `vol20` is the annualised trailing 20-session standard deviation of close-to-close returns, shifted by one trading day.

## 3. 15:50 ET Observability

`vol20` is observable by 15:50 ET on day `t` because it is shifted by one trading day. It uses close-to-close returns only through `t-1`, not `Close_t`, `High_t`, or `Low_t`. The current-day close is not known at 15:50 ET and is not used in the denominator.

The numerator `overnight_next` is future information, but it is used only as the training label for historical observations. The walk-forward scorer trains each calendar year using dates from the past training window only: `train_end = min(previous_year_end, development_cutoff)`. For the year being scored, realised `overnight_next` is not used to create that day's feature vector or score.

## 4. Trailing-only Check

The denominator is trailing-only by construction:

```text
rolling(20, min_periods=10).std().shift(1)
```

This means at decision date `t`, the volatility estimate is based on previous close-to-close returns ending at `t-1`. It is not a full-sample volatility estimate.

## 5. Future-data and Cutoff Checks

- Future returns: used only as historical labels, not as day-`t` features.
- Future close/high/low: not used in the volatility denominator; `vol20` is shifted by one day.
- Full-sample volatility: not used; volatility is rolling and per instrument.
- 2025+ data: not used. Cached baseline panel max date is `2024-12-31`; cached candidate panel max date is `2024-12-31`; shared experiment panel max date is `2024-12-31`.
- Development cutoff: `2024-12-31`.

Eligible label rows with missing `vol20`: `0.000000` fraction. Eligible label rows with non-positive `vol20`: `0`. The pipeline's eligibility filter requires `vol20` to be present and inside the configured volatility band before a stock can be traded.

## 6. Feature-set Check

The target transformation does **not** change the point-in-time feature set. The shared experiment panel is built once by `prepare_experiment_panel`, using the same calls as the baseline:

```text
prepare_data -> add_point_in_time_features -> apply_eligibility_filters -> add_cross_sectional_ranks
```

The candidate then changes only `experiment_target` inside `add_target_transform(transform="vol_scaled")`. The rank feature columns remain the same as the baseline, and all feature columns continue to come from the point-in-time panel.

## Conclusion

The volatility-scaled target passes the point-in-time audit. It is valid to evaluate it as a final-strategy candidate. Promotion should still depend on robustness, drawdown, cost, capacity, and year-by-year stability rather than Sharpe alone.
