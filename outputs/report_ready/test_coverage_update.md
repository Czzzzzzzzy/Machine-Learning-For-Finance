# Test Coverage Update

`PYTHON=/opt/anaconda3/bin/python3 make test` passed on 2026-05-22.

Result: `13 passed`.

High-risk rule tests cover:

- default cutoff and final cached panel max date, including the promoted Phase 2 expanding-window cache;
- fixed commission/slippage round-trip cost assumptions;
- locked 5% ADV20 participation cap;
- three-AUM positions file completeness and required position-level cost/capacity columns;
- no 2025+ dates in final daily return outputs;
- sample-date dollar neutrality after capacity sizing;
- borrow tier annual-rate mapping and short-only borrow costs;
- earnings timing examples with AMC and BMO cases;
- short-interest lag audit wording for provided point-in-time proxies plus one-trading-day decision lag.

No strategy logic was changed for these tests.
