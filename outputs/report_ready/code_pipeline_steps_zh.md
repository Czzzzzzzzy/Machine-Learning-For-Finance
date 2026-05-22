# C2O 代码流程逐步整理

这份说明按代码实际运行顺序整理当前项目。整条 pipeline 的入口是 `run_c2o.py`，它把 `src/c2o_strategy/run.py::main()` 作为主函数执行。

## 0. 如何运行

项目提供两种等价运行方式：

```bash
make reproduce
```

或：

```bash
python3 run_c2o.py --data-dir data --output-dir outputs
```

默认参数在 `src/c2o_strategy/config.py` 中定义，核心设置包括：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `start_date` | `2010-01-01` | 回测起始日 |
| `cutoff` | `2024-12-31` | 数据读取截止日，默认不读取 2025+ |
| `development_cutoff` | `2024-12-31` | 模型开发截止日 |
| `universe_size` | `1000` | 每年冻结 top-1000 市值股票池 |
| `min_price` | `$5` | 最低股价过滤 |
| `min_adv20` | `$10m` | ADV20 最低流动性过滤 |
| `vol_floor`, `vol_cap` | `5%`, `120%` | 年化波动率过滤区间 |
| `earnings_window_days` | `1` | 财报日前后各 1 个交易日排除 |
| `participation_cap` | `5% ADV20` | 单只股票最大参与率 |
| `basket_fraction` | `3%` | 每日多头/空头各选择 eligible universe 的 3% |
| `aums` | `50M, 250M, 1B` | 三个回测资金规模 |

## 1. 主控流程

文件：`src/c2o_strategy/run.py`

`main()` 是整个项目的调度器。它不直接写策略逻辑，而是按顺序调用各模块：

1. 读取配置并创建输出目录。
2. 调用 `prepare_data()` 准备股票面板。
3. 构造点时点特征和交易资格表。
4. 用 walk-forward 方法生成 alpha score。
5. 计算 IC 诊断。
6. 对 50M、250M、1B 三个 AUM 分别回测。
7. 汇总绩效、压力窗口、图表和 QuantStats tear-sheet。

主函数写出的核心结果包括：

| 输出文件 | 内容 |
|---|---|
| `outputs/yearly_universe.parquet` | 每年冻结的股票池 |
| `outputs/universe_summary.csv` | 年度股票池审计 |
| `outputs/return_reconciliation_summary.csv` | overnight/intraday/close-to-close 收益校验 |
| `outputs/eligibility_summary.csv` | 每年各类过滤原因统计 |
| `outputs/feature_weights.csv` | 每年 walk-forward 学到的特征权重 |
| `outputs/ic_daily.csv` | 每日 Spearman IC |
| `outputs/ic_yearly.csv` | 年度 IC 汇总 |
| `outputs/ic_regime.csv` | 按 regime 的 IC 汇总 |
| `outputs/daily_returns_*.csv` | 不同 AUM 的每日收益、成本、敞口 |
| `outputs/performance_summary.csv` | 三个 AUM 的绩效总表 |
| `outputs/positions_250m.parquet` | 250M AUM 的持仓明细 |
| `outputs/stress_windows_250m.csv` | 250M 压力窗口表现 |
| `outputs/quantstats_250m.html` | 250M QuantStats 报告 |
| `outputs/figures/*.png` | 报告图表 |

## 2. 数据读取和价格调整

文件：`src/c2o_strategy/data.py`

函数：`load_prices(config)`

这一步读取 `data/prices.parquet`，只保留 `cutoff <= 2024-12-31` 的数据，避免使用 held-out 2025/2026 信息。

代码做了三件关键事情：

1. 读取 open、high、low、close、adjusted close、volume、market cap 等字段。
2. 用 `adjusted_close / close` 计算调整因子。
3. 用同一个调整因子调整 open/high/low/close，生成 `adj_open`、`adj_high`、`adj_low`、`adj_close`。

这样做的目的，是保证开盘价、收盘价和收益计算在拆股、分红等 corporate actions 后口径一致。

## 3. 构造收益面板

文件：`src/c2o_strategy/data.py`

函数：`build_return_panel(prices)`

这一阶段构造 coursework 要求的三个收益对象：

| 字段 | 公式 | 含义 |
|---|---|---|
| `r_overnight` | `adj_open_t / adj_close_{t-1} - 1` | 从昨日收盘到今日开盘 |
| `r_intraday` | `adj_close_t / adj_open_t - 1` | 从今日开盘到今日收盘 |
| `r_close_close` | `adj_close_t / adj_close_{t-1} - 1` | 常规 close-to-close return |
| `overnight_next` | `adj_open_{t+1} / adj_close_t - 1` | 策略真正预测和交易的下一晚收益 |

同时代码计算：

```text
(1 + r_overnight) * (1 + r_intraday) - 1 - r_close_close
```

得到 `return_identity_residual`，用于检查 overnight + intraday 是否能复原 close-to-close return。这个审计结果输出到 `outputs/return_reconciliation_summary.csv`。

这一阶段还生成后续过滤和特征需要的字段：

| 字段 | 含义 |
|---|---|
| `price_lag1` | 昨日调整收盘价 |
| `market_cap_lag1` | 昨日市值 |
| `dollar_volume_lag1` | 昨日成交金额 |
| `adv20` | 滞后一日的 20 日平均成交金额 |
| `vol20` | 滞后一日的 20 日年化波动率 |
| `vol60` | 滞后一日的 60 日年化波动率 |
| `amihud20` | 滞后一日的 20 日 Amihud 流动性 proxy |

## 4. 年度冻结股票池

文件：`src/c2o_strategy/data.py`

函数：`build_yearly_universe(prices, config)`

每个年份 Y，代码使用 Y 年 1 月 1 日之前最后一个交易日的市值排序，选择满足至少 252 天价格历史的 top-1000 股票。

这一步的原则是：

1. 年初确定股票池。
2. 年内不使用未来市值信息动态调整。
3. 避免 survivorship/look-ahead bias。

随后 `attach_universe(panel, universe)` 会把年度股票池合并回 daily panel，生成 `in_universe` 标记。

审计输出：

```text
outputs/yearly_universe.parquet
outputs/universe_summary.csv
```

## 5. 合并辅助数据和财报窗口

文件：`src/c2o_strategy/data.py`

函数：`merge_auxiliary_features(panel, config)`

这一阶段把几个外部日频数据文件合并进股票面板：

| 数据文件 | 用途 |
|---|---|
| `all_data.parquet` | 基本面、short interest、earnings surprise、industry return 等 |
| `cheapness_scores.parquet` | value/quality/health/momentum 综合分数 |
| `regime.parquet` | 市场 regime 标签 |

函数：`build_earnings_window_flags(config, trading_dates)`

这一步读取 `earnings_calendar.parquet`，使用其中的 `strat_trading_date` 来标记财报窗口。当前设置是财报日前后各 1 个交易日都不交易，最后得到 `earnings_window=True/False`。

## 6. 构造点时点特征

文件：`src/c2o_strategy/features.py`

函数：`add_point_in_time_features(panel)`

这一阶段把原始字段变成 alpha 模型可用的特征。核心原则是：每天 15:50 ET 做决策，因此不能使用当天收盘后才知道的信息。

主要特征包括：

| 特征组 | 代码字段 | 解释 |
|---|---|---|
| Overnight reversal | `r_on_1d`, `r_on_5d` | 最近 overnight return 及其短期均值 |
| Intraday/close-to-close reversal | `r_id_1d`, `ret_cc_5d`, `ret_cc_20d` | 使用滞后后的日内和收盘收益 |
| Momentum | `ret_cc_60d` | 中期 close-to-close 动量 |
| Risk/liquidity | `vol20`, `vol60`, `amihud20`, `adv20_log` | 波动率、流动性和成交金额 |
| Size | `market_cap_log` | 滞后一日市值 |
| Fundamentals | `piot_norm_lag1`, `gross_profit_margin_lag1`, `asset_turnover_ratio_lag1` 等 | 质量、估值、资产效率 |
| Earnings/revisions | `sue_lag1`, `deps_lag1`, `reps1_lag1`, `repsf4_lag1` | 盈利惊喜和修正 |
| Cheapness scores | `final_score_lag1`, `score_velocity_lag1`, `momentum_score_lag1` | 综合基本面/动量打分 |
| Short-interest stress | `dsi_lag1`, `dtcn_lag1`, `ddtcn_lag1` | 借券压力 proxy |
| Industry | `industry_return_lag1` | 行业收益滞后一日 |

所有辅助数据列都会通过 `grouped[column].shift(1)` 生成 `_lag1`，保证不使用当日收盘后信息。

## 7. 借券等级 proxy

文件：`src/c2o_strategy/features.py`

函数：`assign_borrow_tier(panel)`

代码用 lagged short-interest stress 变量给空头借券成本分层：

| Tier | 条件 | 年化借券成本 |
|---|---|---:|
| A | 默认，无明显 hard-to-borrow 信号 | 40 bps |
| B | `dsi_lag1 >= 0.08` 或 `dtcn_lag1 >= 5.0` 或 `ddtcn_lag1 >= 1.0` | 200 bps |
| C | `dsi_lag1 >= 0.15` 或 `dtcn_lag1 >= 10.0` 或 `dsi_lag1 >= 0.10 且 ddtcn_lag1 >= 1.5` | 800 bps |

映射结果保存在：

```text
borrow_tier
borrow_rate_annual
```

后续回测中只对 short book 收取 daily borrow cost。

## 8. 交易资格过滤

文件：`src/c2o_strategy/features.py`

函数：`apply_eligibility_filters(panel, config)`

这一步为每个 stock-date 生成一个 `eligibility_reason`：

| 原因 | 含义 |
|---|---|
| `OK` | 可以交易 |
| `MCAP_FAIL` | 不在年度冻结股票池 |
| `DATA_FAIL` | 缺少必要价格、收益、ADV 或波动率数据 |
| `ADV_FAIL` | `adv20 < $10m` |
| `PRICE_FAIL` | `price_lag1 < $5` |
| `VOL_FAIL` | `vol20` 不在 5%-120% 区间 |
| `EARN_WINDOW` | 处于财报排除窗口 |

最终交易只使用：

```text
is_trade_eligible == True
```

审计输出：

```text
outputs/eligibility_summary.csv
```

## 9. 横截面 rank 标准化

文件：`src/c2o_strategy/features.py`

函数：`add_cross_sectional_ranks(panel)`

代码将每个原始特征在每天的股票横截面里转成 percentile rank，并减去 0.5，使特征大致落在 `[-0.5, 0.5]`。

例如：

```text
rank_ret_cc_20d = cross-sectional percentile rank of ret_cc_20d - 0.5
```

这样做有两个好处：

1. 不同量纲的特征可以直接线性加权。
2. 模型预测的是横截面排序，而不是原始收益水平。

## 10. Alpha 模型训练和打分

文件：`src/c2o_strategy/alpha.py`

函数：`score_panel(panel, rank_columns, config)`

这是策略的核心模型。它每年重新估计一次特征权重，然后给当年每个 stock-date 生成 `alpha_score`。

步骤如下：

1. `add_target_rank()` 把真实的 `overnight_next` 转成每天横截面的 `target_rank`。
2. `_prior_weights()` 读取 `FEATURE_PRIORS` 中预设的经济先验权重。
3. `_learn_weights()` 用过去训练窗口里每个特征和 `target_rank` 的相关性学习权重。
4. 学到的权重会和先验权重做 50/50 混合。
5. 每一年只使用该年份之前的数据训练，默认训练窗口为过去 4 年。
6. 如果进入 development cutoff 之后的年份，则冻结最后一个开发期权重，避免 held-out 泄露。

最终打分公式可以概括为：

```text
alpha_score_{i,t} = sum_j rank_feature_{i,t,j} * weight_{year,j}
```

权重审计输出：

```text
outputs/feature_weights.csv
```

## 11. IC 诊断

文件：`src/c2o_strategy/alpha.py`

函数：

```text
compute_information_coefficients(panel)
summarise_ic(ic_daily)
summarise_ic_by_regime(panel)
```

代码每天计算：

```text
SpearmanCorr(alpha_score_t, overnight_next_t)
```

也就是模型排序和真实下一晚收益排序之间的 rank correlation。

输出：

| 输出文件 | 内容 |
|---|---|
| `outputs/ic_daily.csv` | 每日 IC |
| `outputs/ic_yearly.csv` | 每年 mean IC、IC t-stat、样本天数 |
| `outputs/ic_regime.csv` | 不同 regime 下的 IC |

## 12. 组合构建

文件：`src/c2o_strategy/portfolio.py`

函数：`run_backtest(panel, aum, config)`

每天组合构建分三步：

### 12.1 选 long/short 篮子

函数：`_choose_baskets(day, config)`

逻辑：

1. 只保留 `is_trade_eligible == True` 且有 `alpha_score` 和 `overnight_next` 的股票。
2. 按 `alpha_score` 从低到高排序。
3. 取最高的 3% 做多。
4. 取最低的 3% 做空。
5. 最少每边 15 只股票。

### 12.2 按容量约束分配仓位

函数：`_size_baskets(longs, shorts, aum, config)`

目标是：

```text
long book = 0.5 * AUM
short book = 0.5 * AUM
```

但是每只股票最大仓位受限制：

```text
max_position_i = 5% * ADV20_i
```

如果某只股票达到了 participation cap，代码会把剩余资金重新分配给其他股票。如果整个 basket 无法吸收目标资金，就降低实际 gross exposure。

具体分配函数是：

```text
capped_equal_allocation(caps, target_notional)
```

### 12.3 计算每日收益和成本

多头收益：

```text
sum(long_weight_i * overnight_next_i)
```

空头收益：

```text
sum(short_weight_i * overnight_next_i)
```

注意 short weight 是负数，所以如果被做空股票下跌，贡献为正。

成本包括：

| 成本 | 当前代码 |
|---|---:|
| Commission round trip | `gross_exposure * 0.0001` |
| Auction slippage round trip | `gross_exposure * 0.0003` |
| Borrow cost | `abs(short_weight) * borrow_rate_annual / 252` |

净收益：

```text
net_return = gross_return - commission_cost - slippage_cost - borrow_cost
```

输出：

```text
outputs/daily_returns_50m.csv
outputs/daily_returns_250m.csv
outputs/daily_returns_1000m.csv
outputs/positions_250m.parquet
```

## 13. 绩效汇总

文件：`src/c2o_strategy/metrics.py`

函数：`summarise_backtest(daily, aum)`

这一阶段根据 daily returns 计算：

| 指标 | 含义 |
|---|---|
| `net_annualised_return` | 净年化收益 |
| `net_annualised_volatility` | 净年化波动率 |
| `net_sharpe` | 净 Sharpe |
| `max_drawdown` | 最大回撤 |
| `daily_turnover` | 平均日 turnover |
| `average_gross_exposure` | 平均实际 gross exposure |
| `fraction_days_full_gross_exposure` | 满 gross exposure 的天数比例 |
| `fraction_days_cap_binding` | participation cap 触发比例 |
| `gross_sharpe` | 成本前 Sharpe |
| `commission_sharpe_drag` | commission 对 Sharpe 的拖累 |
| `slippage_sharpe_drag` | slippage 对 Sharpe 的拖累 |
| `borrow_sharpe_drag` | borrow 对 Sharpe 的拖累 |

输出：

```text
outputs/performance_summary.csv
```

## 14. 压力窗口分析

文件：`src/c2o_strategy/metrics.py`

函数：`stress_window_summary(daily)`

当前代码对 250M AUM 策略分析三个压力窗口：

| 窗口 | 日期 |
|---|---|
| `late_2018` | 2018-10-01 到 2018-12-31 |
| `covid_q1_2020` | 2020-01-01 到 2020-03-31 |
| `drawdown_2022` | 2022-01-01 到 2022-12-31 |

每个窗口输出：

```text
net_return
net_sharpe
max_drawdown
avg_gross_exposure
```

输出文件：

```text
outputs/stress_windows_250m.csv
```

## 15. 图表和 QuantStats 报告

文件：`src/c2o_strategy/reporting.py`

主要函数：

| 函数 | 输出 |
|---|---|
| `compute_equal_weight_decomposition()` | 等权 universe 的 overnight/intraday/close-to-close 分解 |
| `plot_equal_weight_decomposition()` | `outputs/figures/equal_weight_return_decomposition.png` |
| `plot_strategy_cumulative()` | `outputs/figures/strategy_cumulative.png` |
| `plot_ic()` | `outputs/figures/rolling_ic.png` |
| `generate_tearsheet()` | `outputs/quantstats_250m.html` |
| `write_summary_markdown()` | `outputs/run_summary.md` |

其中 `generate_tearsheet()` 使用 `quantstats` 将 250M AUM 策略和 `SP500_TR` benchmark 对比。如果 `quantstats` 不可用，代码会生成一个 fallback HTML，但当前输出里已经有 `quantstats_250m.html`。

## 16. 整体逻辑一句话

代码整体做的是：

```text
读取并调整价格
-> 构造 overnight/intraday/close-to-close 收益
-> 年初冻结 top-1000 股票池
-> 合并基本面、short interest、regime 和财报信息
-> 构造只使用 15:50 ET 前可观察信息的特征
-> 过滤不可交易股票
-> 每日横截面 rank 标准化
-> 用过去数据 walk-forward 学习特征权重
-> 每天按 alpha_score 做多最高 3%、做空最低 3%
-> 在 5% ADV20 participation cap 下分配仓位
-> 扣除 commission、auction slippage、borrow cost
-> 输出 IC、绩效、压力窗口、持仓、图表和 QuantStats 报告
```

## 17. 报告里可以这样描述代码结构

本项目采用模块化 pipeline 设计，由 `run.py` 统一调度。`data.py` 负责原始价格数据读取、corporate-action 调整、收益构造、年度股票池冻结、辅助数据合并和财报窗口标记；`features.py` 负责构造 15:50 ET 前可观察的点时点特征、借券等级 proxy、交易资格过滤和横截面 rank 标准化；`alpha.py` 实现 walk-forward 透明线性 alpha 模型，并输出每日 IC、年度 IC 和 regime IC；`portfolio.py` 将 alpha ranking 转换为 daily long-short overnight portfolio，在 5% ADV20 participation cap 下进行容量约束仓位分配，并逐日扣除 commission、auction slippage 和 borrow cost；`metrics.py` 汇总年化收益、波动率、Sharpe、最大回撤和 gross-to-net Sharpe degradation；`reporting.py` 生成图表、equal-weight return decomposition 和 250M AUM QuantStats tear-sheet。整个 pipeline 可以通过 `make reproduce` 单命令复现。

