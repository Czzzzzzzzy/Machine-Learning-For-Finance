# Ablation Interpretation Update

The feature ablation should be read as a dependence audit for the promoted expanding-window final strategy, not as a new tuning exercise.

At 250M, the return/reversal group is the clearest core alpha contributor: removing it lowers net Sharpe from `1.445` to `-1.114` and worsens max drawdown from `-10.19%` to `-46.66%`.

The other groups are mixed. Removing risk/liquidity/size lowers 250M net Sharpe to `1.144`, while removing short-interest/borrow-stress raises it to `1.508` and removing earnings/revision raises it to `1.477` in this no-retuning ablation. This should be disclosed rather than hidden.

The interpretation is narrower than "every feature group improves Sharpe." Some variables can act as risk, capacity, crowding, turnover, or borrow-cost controls rather than pure alpha predictors. Ablation improvement does not prove a removed group is useless; it says that, under the frozen promoted model and basket rule, that group did not add incremental net Sharpe after costs.
