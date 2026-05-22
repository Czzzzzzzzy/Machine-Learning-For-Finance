# 1B Capacity Note

The 1B AUM result is a capacity boundary case, not the main headline. The most credible headline AUM remains 250M, where the promoted expanding-window final strategy has 250M net Sharpe `1.445`, net annual return `7.31%`, and average gross exposure used `74.97%`.

At 1B, the promoted strategy improves versus the previous champion, with net Sharpe `1.293` versus previous champion `0.266`. Even so, average gross exposure used is only `25.35%`, compared with `99.92%` at 50M and `74.97%` at 250M.

Low gross exposure at 1B means the strategy cannot always deploy target risk under the fixed 5% ADV20 participation cap. The positions file shows cap binding on `3773` trading days, and the capacity summary shows `75.40%` of 1B position-days at the cap.

This is evidence of backtest honesty, not a bug. The implementation reduces deployed gross exposure when the selected names cannot absorb target notional under the brief's cap. The report should therefore avoid overstating 1B scalability.
