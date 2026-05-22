# C2O Data Inspection

Scanned `14` file(s) under `data`. Apple resource-fork files beginning with `._` are ignored.

## all_data.parquet

- Path: `data/all_data.parquet`
- Size: `242.0MB`
- Shape: `4,452,783 rows x 47 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2000-01-10 | 2024-12-31 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `stock_id` | `int64` |
| 2 | `date` | `timestamp[ns]` |
| 3 | `piot_norm` | `double` |
| 4 | `dsi` | `double` |
| 5 | `dtcn` | `double` |
| 6 | `ddtcn` | `double` |
| 7 | `short_interest` | `double` |
| 8 | `asset_turnover_ratio` | `double` |
| 9 | `current_liabilities` | `double` |
| 10 | `ev_to_ebit` | `double` |
| 11 | `gross_profit_margin` | `double` |
| 12 | `interest_expenses_net` | `double` |
| 13 | `long_term_debt` | `double` |
| 14 | `net_cash_flow_oper` | `double` |
| 15 | `net_debt_to_equity` | `double` |
| 16 | `net_income_before_extr` | `double` |
| 17 | `price_to_book` | `double` |
| 18 | `total_assets` | `double` |
| 19 | `total_curr_assets` | `double` |
| 20 | `epsp` | `double` |
| 21 | `epsf` | `double` |
| 22 | `reps1` | `double` |
| 23 | `repsf4` | `double` |
| 24 | `sue` | `double` |
| 25 | `inesp` | `double` |
| 26 | `inesn` | `double` |
| 27 | `reps41` | `double` |
| 28 | `repsfs` | `double` |
| 29 | `repsfl` | `double` |
| 30 | `nspc5` | `double` |
| 31 | `deps` | `double` |
| 32 | `value_mean_eps` | `double` |
| 33 | `value_smart_eps` | `double` |
| 34 | `value_split_adj_mean_eps` | `double` |
| 35 | `value_split_adj_smart_eps` | `double` |
| 36 | `gics_sector` | `int64` |
| 37 | `gics_group` | `int64` |
| 38 | `gics_industry` | `int64` |
| 39 | `gics_subindustry` | `int64` |
| 40 | `open` | `double` |
| 41 | `high` | `double` |
| 42 | `low` | `double` |
| 43 | `close` | `double` |
| 44 | `close_split_adj` | `double` |
| 45 | `volume` | `double` |
| 46 | `market_cap` | `double` |
| 47 | `industry_return` | `double` |

### Sample

|   stock_id | date                |   piot_norm |   dsi |   dtcn |   ddtcn |   short_interest |   asset_turnover_ratio |   current_liabilities |   ev_to_ebit |
|-----------:|:--------------------|------------:|------:|-------:|--------:|-----------------:|-----------------------:|----------------------:|-------------:|
|         31 | 2000-01-10 00:00:00 |           0 |   nan |    nan |     nan |              nan |               0.045338 |           nan         |      14.8199 |
|         66 | 2000-01-10 00:00:00 |           0 |   nan |    nan |     nan |              nan |               0.952662 |             2.593e+09 |      16.9661 |
|        775 | 2000-01-10 00:00:00 |           0 |   nan |    nan |     nan |              nan |               0.445783 |        514000         |     nan      |

_Sample truncated: 37 additional columns hidden. Use --max-cols to show more._

## cheapness_scores.parquet

- Path: `data/cheapness_scores.parquet`
- Size: `312.8MB`
- Shape: `6,076,756 rows x 19 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2000-01-03 | 2024-12-31 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `instrument_id` | `int64` |
| 2 | `date` | `timestamp[ns]` |
| 3 | `ticker` | `string` |
| 4 | `gics_sector` | `double` |
| 5 | `gics_group` | `double` |
| 6 | `gics_industry` | `double` |
| 7 | `gics_subindustry` | `double` |
| 8 | `adjusted_close` | `double` |
| 9 | `market_cap` | `double` |
| 10 | `valuation_score` | `double` |
| 11 | `quality_score` | `double` |
| 12 | `health_score` | `double` |
| 13 | `momentum_score` | `double` |
| 14 | `final_score` | `double` |
| 15 | `final_score_clean` | `double` |
| 16 | `score_velocity` | `double` |
| 17 | `score_acceleration` | `double` |
| 18 | `regime_break` | `int64` |
| 19 | `value_trap` | `bool` |

### Sample

|   instrument_id | date                | ticker   |   gics_sector |   gics_group |   gics_industry |   gics_subindustry |   adjusted_close |   market_cap |   valuation_score |
|----------------:|:--------------------|:---------|--------------:|-------------:|----------------:|-------------------:|-----------------:|-------------:|------------------:|
|               1 | 2013-12-12 00:00:00 | HLT      |           nan |          nan |             nan |                nan |          41.6951 |  2.11661e+10 |               nan |
|               1 | 2013-12-13 00:00:00 | HLT      |           nan |          nan |             nan |                nan |          42.8587 |  2.17568e+10 |               nan |
|               1 | 2013-12-16 00:00:00 | HLT      |           nan |          nan |             nan |                nan |          41.7339 |  2.11858e+10 |               nan |

_Sample truncated: 9 additional columns hidden. Use --max-cols to show more._

## earnings_calendar.parquet

- Path: `data/earnings_calendar.parquet`
- Size: `374.7KB`
- Shape: `60,922 rows x 7 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `reporting_date` | 2010-01-05 | 2024-12-20 |
| `strat_trading_date` | 2010-01-05 | 2024-12-19 |
| `period_end_date` | 2009-11-28 | 2024-11-30 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `stock_id` | `int64` |
| 2 | `reporting_date` | `timestamp[ns]` |
| 3 | `strat_trading_date` | `timestamp[ns]` |
| 4 | `reporting_time` | `duration[ns]` |
| 5 | `before_after_market` | `string` |
| 6 | `period` | `string` |
| 7 | `period_end_date` | `timestamp[ns]` |

### Sample

|   stock_id | reporting_date      | strat_trading_date   | reporting_time   | before_after_market   | period   | period_end_date     |
|-----------:|:--------------------|:---------------------|:-----------------|:----------------------|:---------|:--------------------|
|          1 | 2014-02-27 00:00:00 | 2014-02-26 00:00:00  | 0 days 13:30:00  | before                | FY2013Q4 | 2013-12-31 00:00:00 |
|          1 | 2014-05-09 00:00:00 | 2014-05-08 00:00:00  | 0 days 12:30:00  | before                | FY2014Q1 | 2014-03-31 00:00:00 |
|          1 | 2014-08-01 00:00:00 | 2014-07-31 00:00:00  | 0 days 12:30:00  | before                | FY2014Q2 | 2014-06-30 00:00:00 |

## earnings_transfo.parquet

- Path: `data/earnings_transfo.parquet`
- Size: `97.8MB`
- Shape: `4,241,394 rows x 14 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2013-01-02 | 2024-12-31 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `stock_id` | `int64` |
| 2 | `date` | `timestamp[ns]` |
| 3 | `epsp` | `double` |
| 4 | `epsf` | `double` |
| 5 | `reps1` | `double` |
| 6 | `repsf4` | `double` |
| 7 | `sue` | `double` |
| 8 | `inesp` | `double` |
| 9 | `inesn` | `double` |
| 10 | `reps41` | `double` |
| 11 | `repsfs` | `double` |
| 12 | `repsfl` | `double` |
| 13 | `nspc5` | `double` |
| 14 | `deps` | `double` |

### Sample

|   stock_id | date                |         epsp |       epsf |   reps1 |   repsf4 |   sue |   inesp |   inesn |   reps41 |
|-----------:|:--------------------|-------------:|-----------:|--------:|---------:|------:|--------:|--------:|---------:|
|          1 | 2014-02-27 00:00:00 |   0.00715174 | 0.00546456 |     nan |      nan |   nan |     nan |     nan |      nan |
|          1 | 2014-02-28 00:00:00 | nan          | 0.00533809 |     nan |      nan |   nan |       0 |       0 |      nan |
|          1 | 2014-03-03 00:00:00 | nan          | 0.0055777  |     nan |      nan |   nan |       0 |       0 |      nan |

_Sample truncated: 4 additional columns hidden. Use --max-cols to show more._

## gics_info.parquet

- Path: `data/gics_info.parquet`
- Size: `18.4KB`
- Shape: `1,612 rows x 5 columns`

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `instrument_id` | `int64` |
| 2 | `sector` | `int64` |
| 3 | `industry_group` | `int64` |
| 4 | `industry` | `int64` |
| 5 | `subindustry` | `int64` |

### Sample

|   instrument_id |   sector |   industry_group |   industry |   subindustry |
|----------------:|---------:|-----------------:|-----------:|--------------:|
|               1 |       25 |             2530 |     253010 |    2.5301e+07 |
|               2 |       55 |             5510 |     551010 |    5.5101e+07 |
|               3 |       55 |             5510 |     551030 |    5.5103e+07 |

## piotrosky.parquet

- Path: `data/piotrosky.parquet`
- Size: `148.9KB`
- Shape: `33,036 rows x 5 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `reporting_date` | 2000-01-10 | 2024-12-20 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `stock_id` | `int64` |
| 2 | `reporting_date` | `timestamp[ns]` |
| 3 | `piot` | `int64` |
| 4 | `piot_feat_nb` | `int64` |
| 5 | `piot_norm` | `double` |

### Sample

|   stock_id | reporting_date      |   piot |   piot_feat_nb |   piot_norm |
|-----------:|:--------------------|-------:|---------------:|------------:|
|          1 | 2010-02-14 00:00:00 |      0 |              1 |           0 |
|          1 | 2011-02-14 00:00:00 |      1 |              1 |           1 |
|          1 | 2012-02-14 00:00:00 |      2 |              2 |           1 |

## prices.parquet

- Path: `data/prices.parquet`
- Size: `238.2MB`
- Shape: `8,000,368 rows x 12 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2000-01-03 | 2024-12-31 |
| `updated` | 2025-01-08 | 2026-04-13 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `ticker` | `string` |
| 2 | `instrument_id` | `int64` |
| 3 | `date` | `timestamp[ns]` |
| 4 | `open` | `double` |
| 5 | `high` | `double` |
| 6 | `low` | `double` |
| 7 | `close` | `double` |
| 8 | `adjusted_close` | `double` |
| 9 | `volume` | `double` |
| 10 | `market_cap` | `double` |
| 11 | `status` | `string` |
| 12 | `updated` | `timestamp[ns]` |

### Sample

| ticker   |   instrument_id | date                |   open |    high |     low |   close |   adjusted_close |           volume |   market_cap |
|:---------|----------------:|:--------------------|-------:|--------:|--------:|--------:|-----------------:|-----------------:|-------------:|
| XEL      |               2 | 2000-01-03 00:00:00 | 19.625 | 19.625  | 18.9375 | 19      |           6.5292 |      2.7386e+06  |  1.27121e+09 |
| ED       |               3 | 2000-01-03 00:00:00 | 34.375 | 34.4375 | 33.75   | 33.75   |          10.3796 | 581900           |  7.33193e+09 |
| BBY      |               4 | 2000-01-03 00:00:00 | 57.75  | 57.8751 | 54      | 57.5001 |          13.8958 |      1.95124e+07 |  1.1803e+10  |

_Sample truncated: 2 additional columns hidden. Use --max-cols to show more._

## regime.parquet

- Path: `data/regime.parquet`
- Size: `34.0KB`
- Shape: `2,248 rows x 3 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2016-01-04 | 2024-12-31 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `Unnamed: 0` | `int64` |
| 2 | `date` | `timestamp[ns]` |
| 3 | `regime` | `string` |

### Sample

|   Unnamed: 0 | date                | regime      |
|-------------:|:--------------------|:------------|
|            0 | 2016-01-04 00:00:00 | Underweight |
|            1 | 2016-01-05 00:00:00 | Underweight |
|            2 | 2016-01-06 00:00:00 | Underweight |

## rolling_scores_downgrade.csv

- Path: `data/rolling_scores_downgrade.csv`
- Size: `8.7MB`
- Shape: `150,008 rows x 7 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2013-02-28 | 2024-12-31 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `ticker` | `object` |
| 2 | `date` | `object` |
| 3 | `target` | `object` |
| 4 | `prob` | `float64` |
| 5 | `y_true` | `int64` |
| 6 | `models` | `object` |
| 7 | `window` | `int64` |

### Sample

| ticker   | date       | target           |      prob |   y_true | models   |   window |
|:---------|:-----------|:-----------------|----------:|---------:|:---------|---------:|
| ROP      | 2013-02-28 | downgrade_any_1m | 0.083025  |        0 | RF+GB    |        5 |
| AIZ      | 2013-02-28 | downgrade_any_1m | 0.0818616 |        0 | RF+GB    |        5 |
| FRT      | 2013-02-28 | downgrade_any_1m | 0.12319   |        0 | RF+GB    |        5 |

## rolling_scores_upgrade.csv

- Path: `data/rolling_scores_upgrade.csv`
- Size: `8.5MB`
- Shape: `150,008 rows x 7 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2013-02-28 | 2024-12-31 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `ticker` | `object` |
| 2 | `date` | `object` |
| 3 | `target` | `object` |
| 4 | `prob` | `float64` |
| 5 | `y_true` | `int64` |
| 6 | `models` | `object` |
| 7 | `window` | `int64` |

### Sample

| ticker   | date       | target         |     prob |   y_true | models   |   window |
|:---------|:-----------|:---------------|---------:|---------:|:---------|---------:|
| ROP      | 2013-02-28 | upgrade_any_1m | 0.139527 |        0 | GB+RF    |        5 |
| AIZ      | 2013-02-28 | upgrade_any_1m | 0.146318 |        0 | GB+RF    |        5 |
| FRT      | 2013-02-28 | upgrade_any_1m | 0.160414 |        0 | GB+RF    |        5 |

## short_interest_transfo.parquet

- Path: `data/short_interest_transfo.parquet`
- Size: `14.1MB`
- Shape: `573,825 rows x 5 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2002-07-24 | 2024-12-24 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `stock_id` | `int64` |
| 2 | `date` | `timestamp[ns]` |
| 3 | `dsi` | `double` |
| 4 | `dtcn` | `double` |
| 5 | `ddtcn` | `double` |

### Sample

|   stock_id | date                |        dsi |     dtcn |     ddtcn |
|-----------:|:--------------------|-----------:|---------:|----------:|
|          1 | 2015-01-27 00:00:00 | 0.00407394 | 1.66949  | -0.245679 |
|          1 | 2015-02-10 00:00:00 | 0.00402514 | 1.13453  | -0.362399 |
|          1 | 2015-02-25 00:00:00 | 0.004166   | 0.889116 | -2.26174  |

## sp400_constituents.parquet

- Path: `data/sp400_constituents.parquet`
- Size: `12.1KB`
- Shape: `842 rows x 3 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `add_date` | 2014-09-30 | 2024-12-23 |
| `remove_date` | 2014-09-30 | 2024-12-23 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `ticker` | `string` |
| 2 | `add_date` | `timestamp[ns]` |
| 3 | `remove_date` | `timestamp[ns]` |

### Sample

| ticker   | add_date            | remove_date   |
|:---------|:--------------------|:--------------|
| AA       | 2021-12-20 00:00:00 | NaT           |
| AAL      | 2024-09-23 00:00:00 | NaT           |
| AAON     | 2024-05-03 00:00:00 | NaT           |

## sp500_constituents.parquet

- Path: `data/sp500_constituents.parquet`
- Size: `21.0KB`
- Shape: `1,224 rows x 3 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `add_date` | 1996-01-02 | 2024-12-23 |
| `remove_date` | 1996-01-22 | 2024-12-23 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `ticker` | `string` |
| 2 | `add_date` | `timestamp[ns]` |
| 3 | `remove_date` | `timestamp[ns]` |

### Sample

| ticker   | add_date            | remove_date         |
|:---------|:--------------------|:--------------------|
| A        | 2000-06-05 00:00:00 | NaT                 |
| AABA     | 1999-12-08 00:00:00 | 2017-06-19 00:00:00 |
| AAL      | 1996-01-02 00:00:00 | 1997-01-15 00:00:00 |

## sp500_tr.parquet

- Path: `data/sp500_tr.parquet`
- Size: `270.0KB`
- Shape: `6,295 rows x 7 columns`

### Date Ranges

| column | min | max |
|---|---:|---:|
| `date` | 2000-01-03 | 2024-12-31 |

### Columns

| # | column | dtype |
|---:|---|---|
| 1 | `date` | `timestamp[ns]` |
| 2 | `open` | `double` |
| 3 | `high` | `double` |
| 4 | `low` | `double` |
| 5 | `close` | `double` |
| 6 | `adjusted_close` | `double` |
| 7 | `volume` | `int64` |

### Sample

| date                |    open |    high |     low |   close |   adjusted_close |   volume |
|:--------------------|--------:|--------:|--------:|--------:|-----------------:|---------:|
| 2000-01-03 00:00:00 | 2002.11 | 2002.11 | 2002.11 | 2002.11 |          2002.11 |        0 |
| 2000-01-04 00:00:00 | 1925.41 | 1925.41 | 1925.41 | 1925.41 |          1925.41 |        0 |
| 2000-01-05 00:00:00 | 1929.28 | 1929.28 | 1929.28 | 1929.28 |          1929.28 |        0 |
