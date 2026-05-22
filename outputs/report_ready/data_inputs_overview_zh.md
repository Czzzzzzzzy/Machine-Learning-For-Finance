# 原始数据长什么样

当前 `data/` 目录里有 14 个主要输入文件。它们大多是 `parquet` 格式，少数是 `csv`。整体可以分成六类：

1. 股票日频价格数据
2. 基本面、估值、盈利、short interest 等特征数据
3. 财报事件日历
4. 市场 regime 数据
5. 指数和成分股数据
6. 已训练好的 upgrade/downgrade rolling score 数据

当前策略代码直接使用的是：

```text
prices.parquet
all_data.parquet
cheapness_scores.parquet
earnings_calendar.parquet
regime.parquet
sp500_tr.parquet
```

其他文件目前放在数据目录中，但没有被当前 `run.py` pipeline 直接读取，或者它们的内容已经被汇总进 `all_data.parquet`。

## 1. 数据文件总览

| 文件 | 行数 x 列数 | 日期范围 | 当前代码是否直接使用 | 主要用途 |
|---|---:|---|---|---|
| `prices.parquet` | 8,000,368 x 12 | 2000-01-03 到 2024-12-31 | 是 | 股票 OHLCV、adjusted close、市值 |
| `all_data.parquet` | 4,452,783 x 47 | 2000-01-10 到 2024-12-31 | 是 | 综合特征表：基本面、盈利、short interest、行业收益 |
| `cheapness_scores.parquet` | 6,076,756 x 19 | 2000-01-03 到 2024-12-31 | 是 | value/quality/health/momentum 综合分数 |
| `earnings_calendar.parquet` | 60,922 x 7 | 2010-01-05 到 2024-12-20 | 是 | 财报公告日期、BMO/AMC timing、策略交易日 |
| `regime.parquet` | 2,248 x 3 | 2016-01-04 到 2024-12-31 | 是 | 市场 regime 标签 |
| `sp500_tr.parquet` | 6,295 x 7 | 2000-01-03 到 2024-12-31 | 是 | S&P 500 Total Return benchmark |
| `earnings_transfo.parquet` | 4,241,394 x 14 | 2013-01-02 到 2024-12-31 | 否 | 盈利 surprise/revision 特征，当前已在 `all_data` 中出现 |
| `short_interest_transfo.parquet` | 573,825 x 5 | 2002-07-24 到 2024-12-24 | 否 | short interest 衍生特征，当前已在 `all_data` 中出现 |
| `piotrosky.parquet` | 33,036 x 5 | 2000-01-10 到 2024-12-20 | 否 | Piotroski F-score，当前用的是 `all_data.piot_norm` |
| `gics_info.parquet` | 1,612 x 5 | 无日期列 | 否 | 股票行业分类 mapping |
| `sp500_constituents.parquet` | 1,224 x 3 | 1996-01-02 到 2024-12-23 | 否 | S&P 500 成分股加入/移除记录 |
| `sp400_constituents.parquet` | 842 x 3 | 2014-09-30 到 2024-12-23 | 否 | S&P 400 成分股加入/移除记录 |
| `rolling_scores_upgrade.csv` | 150,008 x 7 | 2013-02-28 到 2024-12-31 | 否 | upgrade 预测概率 |
| `rolling_scores_downgrade.csv` | 150,008 x 7 | 2013-02-28 到 2024-12-31 | 否 | downgrade 预测概率 |

## 2. `prices.parquet`

这是最基础的股票日频价格表，也是策略最重要的输入。

### 形状

```text
8,000,368 rows x 12 columns
date: 2000-01-03 -> 2024-12-31
```

### 字段

| 字段 | 含义 |
|---|---|
| `ticker` | 股票代码 |
| `instrument_id` | 股票唯一 ID |
| `date` | 交易日 |
| `open`, `high`, `low`, `close` | 未调整 OHLC 价格 |
| `adjusted_close` | 复权收盘价 |
| `volume` | 成交量 |
| `market_cap` | 市值 |
| `status` | 股票状态标记 |
| `updated` | 数据更新时间 |

### 样例

| ticker | instrument_id | date | open | high | low | close | adjusted_close | volume | market_cap | status |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| XEL | 2 | 2000-01-03 | 19.625 | 19.6250 | 18.9375 | 19.0000 | 6.5292 | 2,738,600 | 1.27e9 | 1 |
| ED | 3 | 2000-01-03 | 34.375 | 34.4375 | 33.7500 | 33.7500 | 10.3796 | 581,900 | 7.33e9 | 1 |
| BBY | 4 | 2000-01-03 | 57.750 | 57.8751 | 54.0000 | 57.5001 | 13.8958 | 19,512,431 | 1.18e10 | 1 |

### 在代码里的作用

`data.py::load_prices()` 读取它，并用：

```text
adjustment factor = adjusted_close / close
```

把 open/high/low/close 都复权。然后 `build_return_panel()` 用复权价格计算：

```text
r_overnight
r_intraday
r_close_close
overnight_next
adv20
vol20
vol60
amihud20
```

## 3. `all_data.parquet`

这是一个综合特征表，把很多非价格信息按 stock-date 展开成日频面板。

### 形状

```text
4,452,783 rows x 47 columns
date: 2000-01-10 -> 2024-12-31
```

### 主要字段

| 字段组 | 字段例子 | 含义 |
|---|---|---|
| ID/date | `stock_id`, `date` | 股票 ID 和日期 |
| Piotroski | `piot_norm` | 标准化 Piotroski 分数 |
| Short interest | `dsi`, `dtcn`, `ddtcn`, `short_interest` | short interest、days-to-cover、变化指标 |
| 基本面质量 | `asset_turnover_ratio`, `gross_profit_margin`, `net_debt_to_equity` | 资产效率、毛利率、杠杆 |
| 估值 | `ev_to_ebit`, `price_to_book` | 企业价值/EBIT、市净率 |
| 盈利 surprise/revision | `epsp`, `epsf`, `reps1`, `repsf4`, `sue`, `deps` | 盈利预测、修正、surprise |
| GICS | `gics_sector`, `gics_group`, `gics_industry`, `gics_subindustry` | 行业分类 |
| 价格/成交 | `open`, `high`, `low`, `close`, `volume`, `market_cap` | 辅助价格字段 |
| 行业收益 | `industry_return` | 行业层面的收益 |

### 样例

| stock_id | date | piot_norm | dsi | dtcn | short_interest | asset_turnover_ratio | ev_to_ebit | gross_profit_margin | price_to_book | gics_sector |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 31 | 2000-01-10 | 0.0 | NaN | NaN | NaN | 0.0453 | 14.8199 | NaN | 1.7805 | 40 |
| 66 | 2000-01-10 | 0.0 | NaN | NaN | NaN | 0.9527 | 16.9661 | 18.3803 | 2.8008 | 20 |
| 775 | 2000-01-10 | 0.0 | NaN | NaN | NaN | 0.4458 | NaN | 91.8919 | NaN | 35 |

### 在代码里的作用

`data.py::merge_auxiliary_features()` 读取它，然后把 `stock_id` 改名为 `instrument_id`，再按：

```text
instrument_id + date
```

合并到主价格面板。

之后 `features.py::add_point_in_time_features()` 会把这些辅助特征全部滞后一日，生成 `_lag1` 特征，避免使用当天收盘后信息。

## 4. `cheapness_scores.parquet`

这是每日 value/quality/health/momentum 打分表。

### 形状

```text
6,076,756 rows x 19 columns
date: 2000-01-03 -> 2024-12-31
```

### 字段

| 字段 | 含义 |
|---|---|
| `instrument_id`, `date`, `ticker` | 股票 ID、日期、ticker |
| `gics_sector`, `gics_group`, `gics_industry`, `gics_subindustry` | 行业分类 |
| `adjusted_close`, `market_cap` | 价格和市值 |
| `valuation_score` | 估值得分 |
| `quality_score` | 质量得分 |
| `health_score` | 财务健康得分 |
| `momentum_score` | 动量得分 |
| `final_score`, `final_score_clean` | 综合分数 |
| `score_velocity`, `score_acceleration` | 分数变化速度和加速度 |
| `regime_break`, `value_trap` | 风险/状态标记 |

### 样例

| instrument_id | date | ticker | adjusted_close | market_cap | valuation_score | quality_score | health_score | momentum_score | final_score | value_trap |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 2013-12-12 | HLT | 41.6951 | 2.12e10 | NaN | NaN | NaN | NaN | NaN | False |
| 1 | 2013-12-13 | HLT | 42.8587 | 2.18e10 | NaN | NaN | NaN | NaN | NaN | False |
| 1 | 2013-12-16 | HLT | 41.7339 | 2.12e10 | NaN | NaN | NaN | NaN | NaN | False |

### 在代码里的作用

当前策略使用其中的：

```text
final_score
score_velocity
momentum_score
```

等字段，滞后一日后进入 alpha 模型。

## 5. `earnings_calendar.parquet`

这是财报事件表，不是每日面板，而是一行一个财报事件。

### 形状

```text
60,922 rows x 7 columns
reporting_date: 2010-01-05 -> 2024-12-20
strat_trading_date: 2010-01-05 -> 2024-12-19
```

### 字段

| 字段 | 含义 |
|---|---|
| `stock_id` | 股票 ID |
| `reporting_date` | 财报公告日期 |
| `strat_trading_date` | 策略应使用的交易日，已经考虑 BMO/AMC timing |
| `reporting_time` | 具体公告时间 |
| `before_after_market` | before/after market |
| `period` | 财报季度 |
| `period_end_date` | 财报期结束日 |

### 样例

| stock_id | reporting_date | strat_trading_date | reporting_time | before_after_market | period | period_end_date |
|---:|---|---|---|---|---|---|
| 1 | 2014-02-27 | 2014-02-26 | 13:30:00 | before | FY2013Q4 | 2013-12-31 |
| 1 | 2014-05-09 | 2014-05-08 | 12:30:00 | before | FY2014Q1 | 2014-03-31 |
| 1 | 2014-08-01 | 2014-07-31 | 12:30:00 | before | FY2014Q2 | 2014-06-30 |

### 在代码里的作用

`build_earnings_window_flags()` 使用 `strat_trading_date`，并把前后各 1 个交易日标记为：

```text
earnings_window = True
```

这些日期上的股票会被 `apply_eligibility_filters()` 排除。

## 6. `short_interest_transfo.parquet`

这是 short interest 转换后的事件/低频表。

### 形状

```text
573,825 rows x 5 columns
date: 2002-07-24 -> 2024-12-24
```

### 字段

| 字段 | 含义 |
|---|---|
| `stock_id` | 股票 ID |
| `date` | short interest 有效日期 |
| `dsi` | short interest intensity proxy |
| `dtcn` | days-to-cover proxy |
| `ddtcn` | days-to-cover / short interest stress 的变化 proxy |

### 样例

| stock_id | date | dsi | dtcn | ddtcn |
|---:|---|---:|---:|---:|
| 1 | 2015-01-27 | 0.0041 | 1.6695 | -0.2457 |
| 1 | 2015-02-10 | 0.0040 | 1.1345 | -0.3624 |
| 1 | 2015-02-25 | 0.0042 | 0.8891 | -2.2617 |

### 在代码里的作用

当前 pipeline 没有直接读取这个文件，因为 `all_data.parquet` 已经包含 `dsi`、`dtcn`、`ddtcn`。策略用这些字段生成 borrow tier。

## 7. `earnings_transfo.parquet`

这是盈利相关的日频转换特征表。

### 形状

```text
4,241,394 rows x 14 columns
date: 2013-01-02 -> 2024-12-31
```

### 主要字段

| 字段 | 含义 |
|---|---|
| `epsp`, `epsf` | EPS 相关预测/因子 |
| `reps1`, `repsf4` | 盈利修正相关特征 |
| `sue` | standardized unexpected earnings |
| `inesp`, `inesn` | earnings surprise/sign 类指标 |
| `reps41`, `repsfs`, `repsfl` | 其他 revision 变体 |
| `nspc5`, `deps` | 预测变化/差异类指标 |

### 样例

| stock_id | date | epsp | epsf | reps1 | repsf4 | sue | inesp | inesn | deps |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2014-02-27 | 0.0072 | 0.0055 | NaN | NaN | NaN | NaN | NaN | -0.0387 |
| 1 | 2014-02-28 | NaN | 0.0053 | NaN | NaN | NaN | 0.0 | 0.0 | -0.0074 |
| 1 | 2014-03-03 | NaN | 0.0056 | NaN | NaN | NaN | 0.0 | 0.0 | -0.0044 |

### 在代码里的作用

当前 pipeline 没有直接读取它，因为相关字段已经在 `all_data.parquet` 中。

## 8. `piotrosky.parquet`

这是 Piotroski F-score 的低频基本面表。

### 形状

```text
33,036 rows x 5 columns
reporting_date: 2000-01-10 -> 2024-12-20
```

### 字段

| 字段 | 含义 |
|---|---|
| `stock_id` | 股票 ID |
| `reporting_date` | 报告日期 |
| `piot` | 原始 Piotroski 分数 |
| `piot_feat_nb` | 可用特征数量 |
| `piot_norm` | 标准化 Piotroski 分数 |

### 在代码里的作用

当前 pipeline 没有直接读取它，因为 `all_data.parquet` 里已经有 `piot_norm`。

## 9. `gics_info.parquet`

这是股票行业分类 mapping 表。

### 形状

```text
1,612 rows x 5 columns
```

### 字段

| 字段 | 含义 |
|---|---|
| `instrument_id` | 股票 ID |
| `sector` | GICS sector |
| `industry_group` | GICS industry group |
| `industry` | GICS industry |
| `subindustry` | GICS subindustry |

### 样例

| instrument_id | sector | industry_group | industry | subindustry |
|---:|---:|---:|---:|---:|
| 1 | 25 | 2530 | 253010 | 25301020 |
| 2 | 55 | 5510 | 551010 | 55101010 |
| 3 | 55 | 5510 | 551030 | 55103010 |

## 10. `regime.parquet`

这是市场 regime 标签表。

### 形状

```text
2,248 rows x 3 columns
date: 2016-01-04 -> 2024-12-31
```

### 字段

| 字段 | 含义 |
|---|---|
| `date` | 交易日 |
| `regime` | 市场 regime 标签 |

### 样例

| date | regime |
|---|---|
| 2016-01-04 | Underweight |
| 2016-01-05 | Underweight |
| 2016-01-06 | Underweight |

### 在代码里的作用

它不直接进入 alpha score，而是用于 `summarise_ic_by_regime()`，分析不同 regime 下模型 IC 是否稳定。

## 11. `sp500_tr.parquet`

这是 S&P 500 Total Return benchmark。

### 形状

```text
6,295 rows x 7 columns
date: 2000-01-03 -> 2024-12-31
```

### 字段

| 字段 | 含义 |
|---|---|
| `date` | 日期 |
| `open`, `high`, `low`, `close` | 指数点位 |
| `adjusted_close` | 复权/总收益指数点位 |
| `volume` | 成交量，指数层面通常为 0 |

### 在代码里的作用

`reporting.py::generate_tearsheet()` 用它作为 benchmark，生成：

```text
outputs/quantstats_250m.html
```

## 12. `sp500_constituents.parquet` 和 `sp400_constituents.parquet`

这是指数成分股加入和移除记录。

### 字段

| 字段 | 含义 |
|---|---|
| `ticker` | 股票代码 |
| `add_date` | 加入指数日期 |
| `remove_date` | 移除指数日期，没有移除则为 missing |

### 样例

`sp500_constituents.parquet`：

| ticker | add_date | remove_date |
|---|---|---|
| A | 2000-06-05 | NaT |
| AABA | 1999-12-08 | 2017-06-19 |
| AAL | 1996-01-02 | 1997-01-15 |

`sp400_constituents.parquet`：

| ticker | add_date | remove_date |
|---|---|---|
| AA | 2021-12-20 | NaT |
| AAL | 2024-09-23 | NaT |
| AAON | 2024-05-03 | NaT |

### 在代码里的作用

当前策略没有用指数成分股定义 universe。当前 universe 是每年用 `prices.parquet` 里的市值排序选 top-1000。

## 13. `rolling_scores_upgrade.csv` 和 `rolling_scores_downgrade.csv`

这是外部已经训练好的 upgrade/downgrade 预测分数。

### 形状

```text
rolling_scores_upgrade.csv:   150,008 rows x 7 columns
rolling_scores_downgrade.csv: 150,008 rows x 7 columns
date: 2013-02-28 -> 2024-12-31
```

### 字段

| 字段 | 含义 |
|---|---|
| `ticker` | 股票代码 |
| `date` | 日期 |
| `target` | 预测目标，例如 `upgrade_any_1m` |
| `prob` | 模型预测概率 |
| `y_true` | 真实标签 |
| `models` | 模型组合，例如 `GB+RF` |
| `window` | rolling window 参数 |

### 样例

`rolling_scores_upgrade.csv`：

| ticker | date | target | prob | y_true | models | window |
|---|---|---|---:|---:|---|---:|
| ROP | 2013-02-28 | upgrade_any_1m | 0.1395 | 0 | GB+RF | 5 |
| AIZ | 2013-02-28 | upgrade_any_1m | 0.1463 | 0 | GB+RF | 5 |
| FRT | 2013-02-28 | upgrade_any_1m | 0.1604 | 0 | GB+RF | 5 |

当前 pipeline 没有把这两个 CSV 纳入 alpha 特征。

## 14. 主代码实际怎么把这些数据拼起来

当前策略不是把所有文件都直接用上，而是围绕 `prices.parquet` 建一张主面板：

```text
prices.parquet
-> 复权 OHLC
-> overnight / intraday / close-to-close / next overnight returns
-> yearly top-1000 universe
```

然后按 `instrument_id + date` 合并：

```text
all_data.parquet
cheapness_scores.parquet
regime.parquet
earnings_calendar-derived flags
```

最终形成一个很大的 daily stock panel，每一行大致代表：

```text
某只股票 i 在某个交易日 t 的价格、收益、基本面、short interest、行业、财报窗口、交易资格、特征和未来一晚收益
```

这个 panel 才是后面 alpha 模型和回测真正使用的数据形态。

## 15. 一个直观理解

可以把这些数据想象成三层：

### 第一层：价格和收益

来自 `prices.parquet`。回答的问题是：

```text
这只股票今天开盘、收盘、成交量、市值是多少？
昨天收盘到今天开盘涨跌多少？
今天收盘到明天开盘涨跌多少？
```

### 第二层：股票特征

来自 `all_data.parquet` 和 `cheapness_scores.parquet`。回答的问题是：

```text
这只股票贵不贵？
质量好不好？
盈利有没有 surprise？
short interest 高不高？
行业最近表现怎么样？
```

### 第三层：事件和审计

来自 `earnings_calendar.parquet`、`regime.parquet`、`sp500_tr.parquet`。回答的问题是：

```text
今天是否接近财报？
当前市场 regime 是什么？
策略相对于 S&P 500 TR 表现如何？
```

这三层合在一起，构成策略每天 15:50 ET 做多/做空决策的信息集。

