# plan.md — Personal Investment Bank System (MVP v1) — Updated

## 1) Objectives
- ✅ 已验证 **核心工作流**：真实数据拉取 → 指标计算 → 情绪指数 → Regime → 仓位建议 → 个股建议 → 中文日报输出（含可选 LLM 深度解读）。
- ✅ 已交付 **可运行 MVP**（FastAPI + React + SQLite）：Dashboard（7页）+ 日报生成/查看/下载 + 组合设置（输入持股数量自动算权重）。
- ✅ 稳定性优先能力已落地：
  - 数据源失败时 **缓存/跳过/标记**，系统不崩溃
  - 针对 akshare 限流加入 **磁盘缓存 + Sina 回退**
- ⏳ 当前状态：进入 **端到端测试与加固阶段**（testing_agent_v3 进行中），准备收敛为“可长期每日稳定运行”的 v1。

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation) ✅已完成
**Goal**: `python test_core.py` 一次跑通核心链路；不通过不进入 Phase 2。

**User stories (POC)**
1. ✅ 拉取 A 股/美股/指数/加密真实行情。
2. ✅ 计算 MA/RSI/波动/MDD 等核心技术指标。
3. ✅ 输出 Global F&G / China Tech F&G / AI Chain Heat 三个分数。
4. ✅ 输出市场 Regime 与大类仓位建议。
5. ✅ 生成中文 markdown 日报（含原因与风险提示）。

**Delivered / Evidence**
- ✅ `test_core.py` 12/12 checks 全绿：akshare、yfinance、Alternative.me Crypto F&G、技术指标、Global/China F&G、AI 热度、Regime、Allocation、Recommendation、LLM、中文日报。
- ✅ 生成 `sample_daily_report.md`（可读、可执行、中文）。

**Exit / stop criteria**
- ✅ 12 项检查全部通过；输出分数 0-100；关键数据源失败有降级说明。

---

### Phase 2 — V1 App Development (FastAPI + React + SQLite) ✅已完成
**Goal**: 用最少的端到端功能把“每日更新 + Dashboard + 日报查看 + 组合设置”做成可用产品。

**User stories (V1)**
1. ✅ Overview：一屏看到今日 Regime、三大情绪指数、建议大类仓位与关键风险点。
2. ✅ Portfolio/Settings：录入持股数量 → 自动按市值估算权重/集中度；无输入时等权演示。
3. ✅ Watchlist：排序、动作建议（回调加仓/小仓位/持有/等待/减仓止盈/回避追涨）+ 原因解释 + 技术指标。
4. ✅ 一键手动刷新数据：展示刷新状态与缺失数据源提示。
5. ✅ Reports：查看/下载今日与历史中文日报（Markdown 渲染）。

**Backend delivered (FastAPI)**
- ✅ SQLite + SQLAlchemy 表结构落地：
  - `market_price`（预留扩展）
  - `market_indicator`（预留扩展）
  - `sector_score`
  - `portfolio_snapshot`
  - `daily_signal`
  - `recommendations`
  - `daily_report`
- ✅ 日更 pipeline：抓取 → 计算 → 策略 → 报告 → 写库
  - `/api/refresh-data` 触发执行
  - APScheduler 默认 **北京时间 16:30** 自动执行
- ✅ 数据源与容错能力增强：
  - akshare：磁盘缓存（TTL）+ **Sina fallback**（解决 EastMoney 接口断连/限流）
  - yfinance：磁盘缓存（TTL）
  - Alternative.me：直接请求，失败降级
- ✅ 配置：YAML 管理（portfolio/watchlist/sectors/thresholds/data_sources/strategy_profile），并提供 Settings API 更新阈值、风险偏好。

**Frontend delivered (React + shadcn/ui + Recharts)**
- ✅ 7 页面完整实现：
  1) Overview 总览
  2) Portfolio 持仓
  3) Sectors 赛道
  4) Watchlist 观察池
  5) Sentiment 情绪（历史曲线 + 因子贡献）
  6) Reports 报告（列表 + Markdown 阅读器 + 下载）
  7) Settings 设置（风险偏好 + 阈值编辑）
- ✅ 设计语言落地：遵循 `design_guidelines.md`（Bloomberg-like 信息密度、IBM Plex 字体、深色默认、专业数据可视化）。

**Known fixes applied during Phase 2**
- ✅ 修复 watchlist.yaml YAML 语法错误（键值冒号后缺空格）。
- ✅ 修复日报生成变量名遮蔽导致 KeyError。
- ✅ akshare 限流/断连：增加磁盘缓存 + Sina 回退，pipeline 可完成。

**Current output snapshot**
- ✅ watchlist 覆盖：约 **21 CN** + **13 US** + **2 Crypto**，每条含指标与建议。
- ✅ pipeline 端到端跑通：生成含 LLM 策略师解读的日报；当日示例 Regime=Extreme Greed。

**Phase 2 test gate**
- ⏳ testing_agent_v3 端到端测试进行中（目标覆盖：启动、刷新、页面渲染、更新持股数量后联动、报告生成/下载）。

---

### Phase 3 — Hardening + Backtest (Basic) + Strategy Controls (Next)
**Goal**: 在已完成 MVP 的基础上，提升稳定性、可解释性、可回溯性；补齐回测与策略控制（MVP 级）。

**User stories (Phase 3)**
1. 作为用户，我希望看到每个分数的构成（因子贡献/缺失因子提示）并可在 UI 直接查看。
2. 作为用户，我希望在 Settings 调整阈值后能立即影响建议，并支持“保存前预览影响”。
3. 作为用户，我希望有简易回测：按 Regime/信号做再平衡，输出收益/回撤。
4. 作为用户，我希望所有计算结果可追溯到具体日期与原始行情、缺失因子。
5. 作为用户，我希望数据源间歇不可用时系统仍可生成“降级日报”，并记录降级原因。

**Revised Steps (based on实际实现现状)**
- A) 端到端测试收敛（Phase 2 收尾）
  - 使用 testing_agent_v3 覆盖所有核心页面与关键交互
  - 修复：
    - 页面空状态与提示（明确“请先刷新数据”）
    - API 超时/重试策略（特别是 akshare/sina）
    - 刷新时 UI loading、避免重复触发 refresh
- B) 可解释性增强
  - 在 Sentiment 页展示：
    - Global/China F&G factor breakdown（已在 payload 中）
    - 缺失因子列表（missing factors）
  - 在 Overview/Watchlist 行展开：显示评分拆解（sector/momentum/pullback/RS/risk）
- C) 回测（基础版）
  - 完善 `/api/backtest/run`：支持选择资产池（指数/ETF）与时间窗，输出曲线与指标
- D) 数据可靠性
  - 将 akshare A股个股数据抓取默认切换为：优先东财，失败自动 sina
  - 增加“最后成功抓取时间/数据新鲜度”展示
  - 缓存分层：raw/processed/report，并提供一键清缓存（开发用）
- E) 报告增强
  - 报告中明确标注：缺失数据源、缺失因子、是否使用 LLM
  - 增加“关键变化”与“触发条件”段落（便于执行）

---

## 3) Next Actions (Immediate)
1. ⏳ 完成 testing_agent_v3 端到端测试并修复问题（Phase 2 收尾）。
2. 优化 pipeline 耗时：
   - 利用磁盘缓存减少重复抓取
   - 对 A 股个股抓取做批次/间隔控制
3. 强化可解释性 UI：Sentiment 因子贡献图 + Watchlist 评分拆解。
4. 增强 Portfolio：保存持股数量后自动提示“需要刷新重算”，并支持“仅重算组合”轻量刷新（可选）。
5. 准备 Phase 3：补齐回测与策略阈值即时生效机制。

## 4) Success Criteria
- Phase 1：✅ `python test_core.py` 稳定通过；生成中文 `sample_daily_report.md`；缺失数据有降级说明。
- Phase 2：✅ Dashboard 7 页可用；手动刷新可用；持股数量更新后权重与建议联动；日报可查看/下载；系统不因单一数据源失败而崩溃；16:30 北京时间自动调度。
- Phase 3：
  - 可解释性：F&G/Heat/推荐评分均可在 UI 查看拆解；缺失因子与降级原因可追溯
  - 回测：基础 backtest 可运行并输出曲线与关键指标
  - 稳定性：数据源波动时仍可生成降级日报；pipeline 单次运行成功率显著提升（目标 >95%）
