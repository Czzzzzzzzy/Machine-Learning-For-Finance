# Borrow External Validation Limitations

No direct prime-broker borrow-fee, locate-rate, or securities-lending data is
used in this submission.

The borrow proxy is internally deterministic and based on lagged
short-interest stress variables already present in the point-in-time panel:
`dsi_lag1`, `dtcn_lag1`, and `ddtcn_lag1`. This is a limitation because the
proxy cannot be independently validated against actual contemporaneous borrow
fees from the frozen repository files.

The strategy mitigates this limitation by charging explicit and conservative
Tier A/B/C borrow costs to short notional:

- Tier A: 40 bps per annum
- Tier B: 200 bps per annum
- Tier C: 800 bps per annum

Borrow is charged daily as annual rate divided by 252. Future work could
validate the proxy against licensed or otherwise reproducible securities-lending
or vendor borrow data.
