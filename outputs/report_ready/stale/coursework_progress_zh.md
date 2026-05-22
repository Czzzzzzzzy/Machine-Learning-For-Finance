# C2O Coursework 当前进度记录

记录日期：2026-05-15

本文档专门用于记录当前项目相对于 `C2O_Coursework_Brief.pdf` 的完成进度。它不是最终报告正文，而是后续写 report、补代码审计和准备提交包时的工作台账。

## 1. 总体状态

当前项目已经完成了可复现的主 pipeline：从数据读取、收益构造、年度股票池、eligibility filters、点时 alpha、walk-forward scoring、三档 AUM 回测，到图表和 250M QuantStats tear-sheet 均已有输出。

核心结论是：代码主干已可运行并能产出主要结果；报告材料已有雏形；新增的 strategy improvement experiment harness 已完成并输出统一审计表；但 brief 明确要求的一些审计项仍缺完整输出，尤其是 feature ablation、borrow-tier 细分、AMC/BMO 手工例子，以及 50M/1B 的持仓级 capacity 统计。

## 2. Brief 要求与当前完成情况

| Brief 部分 | 要求概述 | 当前状态 | 证据文件 |
|---|---|---|---|
| Step 1: daily panel | 构造 open-to-close / close-to-open / close-to-close 收益，并校验 corporate-action 调整后一致性 | 已完成 | `outputs/return_reconciliation_summary.csv`, `outputs/equal_weight_return_decomposition.csv` |
| Step 1: 2010-2024 cutoff | 开发阶段不得读取 2025+ 数据，cutoff 需可配置 | 已完成 | `src/c2o_strategy/config.py`, `src/c2o_strategy/data.py`, `README.md` |
| Step 1: AMC/BMO timing | 财报 timing flag 必须按 BMO/AMC 处理，并在报告中手工验证至少一个事件 | 部分完成 | 代码使用 `earnings_calendar.strat_trading_date`，但缺 hand-checkable example export |
| Step 1: short-interest lag | short-interest 特征需遵守发布滞后和 vendor lag | 部分完成 | `all_data` 中已含 lagged short-interest proxies，报告还需更清楚说明和示例图 |
| Step 2: yearly universe | 每年用上一年最后交易日市值冻结 top-1000 universe | 已完成 | `outputs/yearly_universe.parquet`, `outputs/universe_summary.csv` |
| Step 2: capacity-aware eligibility | price、ADV20、volatility、earnings window、participation cap | 已完成 | `outputs/eligibility_summary.csv`, `src/c2o_strategy/features.py` |
| Step 3: borrow cost | 构造 hard-to-borrow proxy，headline 结果必须 net of borrow | 部分完成 | `src/c2o_strategy/features.py`, `outputs/report_ready/borrow_sharpe_degradation.csv` |
| Step 4: alpha | 点时特征、目标、模型、训练方案、IC 统计 | 已完成主结果 | `outputs/feature_weights.csv`, `outputs/ic_daily.csv`, `outputs/ic_yearly.csv`, `outputs/ic_regime.csv` |
| Step 4: feature ablation | 按 feature group 做 marginal contribution 分析 | 未完成 | `outputs/report_ready/feature_ablation_audit.md` 中多数为 `MISSING` |
| Step 5: portfolio | dollar-neutral overnight portfolio，三档 AUM，Section 6.3 成本 | 已完成主结果 | `outputs/performance_summary.csv`, `outputs/daily_returns_*.csv` |
| Step 5: QuantStats | 250M AUM QuantStats HTML，benchmark SP500_TR | 已完成 | `outputs/quantstats_250m.html` |
| Step 5: stress windows | 至少一个 stress-window 分析 | 已完成 | `outputs/stress_windows_250m.csv`, `outputs/report_ready/stress_windows_250m_report.md` |
| Strategy improvement experiments | 在不覆盖 baseline 的前提下，对 basket size、weighting、cost-aware ranking、short-leg treatment、target transformation 做受控实验 | 已完成 | `src/c2o_strategy/experiments.py`, `outputs/strategy_experiment_summary.csv`, `outputs/report_ready/strategy_improvement_audit.md` |
| Deliverables | 15-25 页 PDF report、QuantStats HTML、code repo、innovation declaration | 部分完成 | code 和 outputs 已有；正式 report 与 innovation declaration 尚未完成 |

## 3. 当前 headline 回测结果

来自 `outputs/performance_summary.csv`。

| AUM | Net annualised return | Net vol | Net Sharpe | Max drawdown | Avg gross exposure | Cap binding days |
|---:|---:|---:|---:|---:|---:|---:|
| 50M | 1.38% | 5.67% | 0.270 | -30.70% | 99.69% | 95.12% |
| 250M | 1.66% | 4.71% | 0.374 | -24.58% | 57.89% | 99.97% |
| 1B | -0.18% | 2.17% | -0.073 | -20.18% | 17.25% | 99.97% |

目前最适合作为 headline 的版本是 250M AUM：成本后仍为正 Sharpe，但收益较 modest。1B 版本主要问题是 capacity 约束过强，平均 gross exposure 只能部署约 17.25%。

## 4. 成本分解

来自 `outputs/report_ready/borrow_sharpe_degradation.csv`。

| AUM | Gross Sharpe | Commission drag | Slippage drag | Borrow drag | Net Sharpe |
|---:|---:|---:|---:|---:|---:|
| 50M | 2.231 | 0.443 | 1.330 | 0.188 | 0.270 |
| 250M | 1.724 | 0.309 | 0.929 | 0.112 | 0.374 |
| 1B | 0.801 | 0.201 | 0.602 | 0.071 | -0.073 |

主要 Sharpe degradation 来自 auction slippage，其次是 commission，borrow drag 相对较小但仍需要完整报告 borrow-tier 分布和 proxy validation。

## 5. 已有报告素材

| 文件 | 用途 |
|---|---|
| `outputs/report_ready/data_inputs_overview_zh.md` | 中文数据文件总览 |
| `outputs/report_ready/code_pipeline_steps_zh.md` | 中文代码流程说明 |
| `outputs/report_ready/report_snippets.md` | 报告可用表格和英文段落草稿 |
| `outputs/report_ready/feature_inventory.md` | 特征清单、公式、滞后说明 |
| `outputs/report_ready/capacity_analysis.md` | capacity 分析草稿 |
| `outputs/report_ready/stress_windows_250m_report.md` | stress-window 报告段落 |
| `outputs/report_ready/feature_ablation_audit.md` | ablation 审计表，目前多项缺失 |
| `outputs/report_ready/strategy_improvement_audit.md` | strategy improvement 实验审计与推荐版本 |

## 6. 新增 Strategy Improvement 实验进度

已新增独立 harness：`src/c2o_strategy/experiments.py`，入口为 `run_strategy_experiments.py`，并在 `Makefile` 中加入 `experiments` target。该 harness 不覆盖当前 top/bottom 3% 250M baseline，而是使用同一份点时数据、同一开发截止日 `2024-12-31`、同一成本表、同一 walk-forward 训练协议，对 A-E 五组实验统一输出。

主输出为 `outputs/strategy_experiment_summary.csv`，共 72 条实验结果：24 个实验配置 × 3 档 AUM。列包含 net/gross performance、三类成本 drag、turnover、capacity、持仓数量、IC、worst 12m return 和 notes。报告审计输出为 `outputs/report_ready/strategy_improvement_audit.md`。

当前 250M 结果显示，baseline `top_bottom_3pct` net Sharpe 为 0.379；表现最强的候选版本是 `E_target_transform / volatility_scaled_overnight_return`，250M net Sharpe 为 0.811，net annual return 为 3.93%，max drawdown 为 -10.19%。需要在正式报告中说明：这是开发样本内的受控比较，不应继续围绕同一指标反复调参而不记录失败实验。

## 7. 当前缺口清单

1. Feature ablation 需要补跑。
   - 按 feature group 移除：return/reversal、risk/liquidity/size、fundamental/value/quality、earnings/revision、short-interest/borrow-stress、industry-return。
   - 输出建议：`outputs/feature_ablation_summary.csv` 和更新 `outputs/report_ready/feature_ablation_audit.md`。

2. Borrow-tier 明细需要补充。
   - 当前 `positions_250m.parquet` 未包含 `borrow_tier` 和 `borrow_rate_annual`。
   - 需要输出 short positions 的 Tier A/B/C 占比、raw short signal affected fraction，以及 hard-exclusion sensitivity。

3. AMC/BMO 手工验证例子需要导出。
   - brief 要求报告中 cite 至少一个 stock-event by hand。
   - 建议导出 `outputs/earnings_timing_examples.csv`，包含 `ticker`, `instrument_id`, `reporting_date`, `before_after_market`, `strat_trading_date`, `excluded_decision_date`, `rule_applied`。

4. 50M 和 1B 的 positions 需要导出。
   - 当前只保存 `positions_250m.parquet`。
   - brief Section 7 会问每档 AUM 的 average/peak per-stock dollar position，50M 和 1B 现在缺持仓级证据。

5. Equal-weight stylised fact 需要解释或复核。
   - 当前 2010-2024 cumulative roughly：overnight +298%，intraday +95%，close-to-close +647%。
   - overnight 优于 intraday，但不像 brief 所说“几乎全部 long-run return 都在 overnight”。报告里不能硬说复现完全一致，需要解释 universe/equal-weight 口径差异，或重新检查 index-level benchmark decomposition。

6. 测试环境已补齐。
   - 已使用项目依赖环境运行 `PYTHONPATH=src python -m pytest -q`。
   - 当前测试结果：4 passed。

7. 最终提交文档还未完成。
   - 需要正式 PDF report。
   - 需要 one-page innovation declaration。
   - 图表 caption 需要明确写 AUM、basket size、participation cap、cost schedule。

## 8. 建议下一步优先级

1. 先改 `run.py` / `portfolio.py`，保存三档 AUM 的 positions，并把 borrow tier 写进持仓。
2. 加 ablation loop，生成 feature-group ablation summary。
3. 导出 AMC/BMO timing examples 和 borrow-tier summary。
4. 把 strategy improvement audit 的推荐版本写进正式 report，但避免再做未记录的 metric chasing。
5. 补跑 `make reproduce`，确认所有 outputs 一次性生成。
6. 用 `report_ready` 文件整理正式 report。
7. 单独写 innovation declaration，强调 human choices：容量约束处理、borrow proxy、walk-forward transparent alpha、成本诚实分解等。

## 9. 当前项目一句话总结

当前代码已经形成一条可复现、点时意识较强、成本后表现诚实的 C2O overnight strategy pipeline；strategy improvement 实验已补齐并给出候选改进版本，剩余主要短板是 brief 要求的 feature ablation、borrow-tier、AMC/BMO 示例和持仓级 capacity 证据。
