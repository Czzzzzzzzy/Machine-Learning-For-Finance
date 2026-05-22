# C2O Coursework Innovation Declaration

This submission’s added value is not a single high-Sharpe backtest, but the sequence of design and audit choices used to reach the final strategy.

First, we made a deliberate target-engineering choice. The project did not simply predict raw overnight returns. We tested logged target alternatives and promoted the volatility-scaled overnight return target only after a point-in-time audit. The final target, `overnight_next / (vol20 / sqrt(252))`, ranks stocks by risk-adjusted overnight opportunity rather than raw overnight magnitude. The volatility input is trailing 20-day close-to-close volatility shifted by one trading day, so the improvement is not based on future information or a changed feature set.

Second, we treated capacity as part of implementation rather than an after-the-fact caveat. The final strategy is evaluated at 50M, 250M, and 1B AUM with a 5% ADV20 participation cap. Full positions files are preserved, including final weights, dollar positions, ADV20 dollars, participation rates, cap dollars, and cap-binding flags. This makes the 1B degradation visible and auditable instead of hidden behind summary performance.

Third, we reported costs and borrow honestly. The final performance includes commission, auction slippage, and tiered borrow costs. We report gross-to-net Sharpe degradation rather than presenting inflated gross results. Borrow treatment is disclosed as a tiered-cost method, not an externally validated locate model or a hard-exclusion rule.

Fourth, we made reproducibility and auditability explicit. The original baseline outputs were archived before final regeneration. The final strategy configuration was frozen, report-ready audit files were generated, and `make reproduce` and `make test` were verified. The final report uses numbers from the frozen output files and identifies evidence gaps rather than filling them with unsupported estimates.

LLM tools were used for coding assistance, checking, and drafting. The key design decisions were made through human judgement about economic plausibility, point-in-time validity, robustness, and whether the resulting strategy could be defended to a sceptical marker.
