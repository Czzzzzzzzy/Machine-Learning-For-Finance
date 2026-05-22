# Previous Champion Archive After Phase 2

This archive preserves the previous final champion before promoting the Phase 2
expanding-window challenger.

## Previous Champion

- Target: `volatility_scaled_overnight_return`
- Target definition: `overnight_next / (vol20 / sqrt(252))`
- Training window: 4-year rolling
- Feature set: unchanged from baseline
- Basket: top/bottom 3%, equal weight
- Short treatment: tiered borrow cost only
- 250M net Sharpe: `0.811`

## New Recommended Challenger

- Experiment id: `phase2_g5_05_expanding`
- Target: same volatility-scaled overnight target
- Training window: expanding
- Alpha learning: 50% prior / 50% learned
- Basket, weighting, ranking, borrow treatment, costs, participation cap, and
  execution assumptions are unchanged.

The current task promotes this challenger only after the promotion audit passes.
