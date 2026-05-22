# Final Check

- [x] Final report PDF exists and renders.
- [x] QuantStats HTML exists and is the generated 250M report.
- [x] Final 250M metrics match outputs: net annual return `7.31%`, net volatility `4.97%`, net Sharpe `1.445`, max drawdown `-10.19%`.
- [x] Old `0.811` Sharpe is labelled only as previous champion.
- [x] Promoted `1.445` Sharpe is labelled as final.
- [x] Cost, borrow, 5% ADV20 cap, and close-to-open execution assumptions are unchanged.
- [x] Final daily return outputs end no later than 2024-12-31.
- [x] 50M, 250M, and 1B position files are present.
- [x] 2025-2026 remains held out for marker evaluation.
- [x] `PYTHON=/opt/anaconda3/bin/python3 make reproduce` passed.
- [x] `PYTHON=/opt/anaconda3/bin/python3 make test` passed with `13 passed`.
