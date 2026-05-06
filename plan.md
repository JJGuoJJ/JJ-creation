# plan.md — Personal Investment Bank System (MVP v1)

## 1) Objectives
- Validate **core workflow** in isolation: real data拉取 → 指标计算 → 情绪指数 → Regime → 仓位建议 → 个股建议 → 中文日报输出（可选 LLM 解读）。
- 基于已验证的 core，构建 **FastAPI + React + SQLite** 的可运行 MVP：Dashboard + 日报生成/查看 + 组合设置（输入持股数量自动算权重）。
- 稳定性优先：外部数据失败时 **缓存/跳过/标记**，不崩溃；所有阈值/参数来自 YAML。

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation) ✅必须先完成
**Goal**: `python test_core.py` 一次跑通核心链路；不通过不进入 Phase 2。

**User stories (POC)**
1. 作为用户，我希望脚本能拉取 A 股/美股/指数/加密的真实行情，否则系统无意义。
2. 作为用户，我希望系统能计算 MA/RSI/波动/MDD 等核心技术指标。
3. 作为用户，我希望系统能输出 Global F&G / China Tech F&G / AI Chain Heat 三个分数。
4. 作为用户，我希望系统能给出清晰的市场 Regime 和对应的大类仓位建议。
5. 作为用户，我希望脚本能生成一份可读的中文 markdown 日报（含原因与风险提示）。

**Steps**
- Web search/quick review：确认 akshare 指数/个股日线接口、yfinance 对 ^VIX/^TNX/^IRX 的可用性与限制、Alternative.me F&G schema（仅用于实现细节校验）。
- 编写 `test_core.py`（单文件）：
  - 数据拉取：akshare(A 股持仓/指数/观察池)、yfinance(美股/指数/加密/商品/债券)、Alternative.me(Crypto F&G)
  - 指标：MA/RSI/收益率/回撤/波动/量比
  - 三大指数：Global F&G、China Tech F&G、AI Chain Heat
  - Regime + Allocation engine
  - Recommendation engine（watchlist 排名 + action + reasons）
  - 可选：Emergent LLM 生成“投行口吻解读”段落（失败则降级为规则解释）
  - 生成 `sample_daily_report.md`
- 缓存与容错：本地缓存（/backend/data/cache）+ 失败标记；缺数据则跳过该因子并在报告说明。

**Exit / stop criteria**
- 12 项检查全部通过（含报告落盘）；关键数据源可用性确认并有降级策略；输出分数在 0-100，权重归一。

---

### Phase 2 — V1 App Development (FastAPI + React + SQLite)
**Goal**: 用最少的端到端功能把“每日更新 + Dashboard + 日报查看 + 组合设置”做成可用产品。

**User stories (V1)**
1. 作为用户，我打开 Overview 就能看到今日 Regime、三大情绪指数、建议大类仓位与关键风险点。
2. 作为用户，我能在 Settings 输入每只持仓的**持股数量**，系统自动算市值权重/集中度，并在缺失时用等权演示。
3. 作为用户，我能在 Watchlist 页面看到排序、动作建议（买/持/等/减）、以及每条建议的原因。
4. 作为用户，我能一键手动刷新数据，并看到刷新状态与失败源提示。
5. 作为用户，我能在 Reports 页面查看/下载今日及历史中文日报。

**Backend steps (FastAPI)**
- SQLite + SQLAlchemy：落地表（market_price/indicator/sector_score/portfolio_snapshot/daily_signal/recommendations/reports）。
- 模块化 providers：`base.py` + akshare/yfinance/alternative_fng；统一返回 schema。
- 核心计算模块从 POC 抽取为：indicators/strategy/report（保持与 POC 同逻辑）。
- API（最小闭环）：
  - GET `/api/health`
  - POST `/api/refresh-data`（触发抓取+计算+写库+生成日报）
  - GET `/api/market/overview`
  - GET `/api/watchlist`
  - GET/POST `/api/portfolio`（读+更新 share counts）
  - GET `/api/recommendations/today`
  - GET `/api/reports/list` + GET `/api/reports/{id}`
- Scheduler：APScheduler 每日运行（北京时间收盘后）；失败重试 + 日志。
- 配置：YAML（thresholds/portfolio/watchlist/sectors/strategy_profile/data_sources）+ API 提供读取/更新（先做读取与后端热加载最小版）。

**Frontend steps (React + shadcn/ui + Recharts)**
- 页面：Overview / Portfolio / Watchlist / Fear&Greed(简版曲线) / Reports / Settings。
- 状态：加载/空数据/错误（明确提示来源：akshare/yfinance/alternative.me）。
- 关键组件：F&G gauge、allocation donut、recommendation table、report viewer (markdown render)。

**Phase 2 test gate**
- 完成后调用 testing agent 做 1 轮端到端：启动、刷新、页面渲染、更新持股数量后权重变化、报告生成与查看。

---

### Phase 3 — Hardening + Backtest (Basic) + Strategy Controls
**Goal**: 提升可解释性、稳定性、可回溯；补齐回测与阈值编辑（MVP 级）。

**User stories (Phase 3)**
1. 作为用户，我希望看到每个分数的构成（因子贡献/缺失因子提示）。
2. 作为用户，我希望能在 Settings 调整阈值（YAML）并立即影响建议。
3. 作为用户，我希望有简易回测：按 Regime/信号做再平衡，输出收益/回撤。
4. 作为用户，我希望所有计算结果可追溯到具体日期与原始行情。
5. 作为用户，我希望数据源间歇不可用时系统仍能生成“降级日报”。

**Steps**
- 指数可解释性：每个 F&G/Heat 输出 factor breakdown。
- 阈值编辑：前端表单 → 后端写 YAML（带校验与备份）。
- Backtest API：`/api/backtest/run`（选资产池/周期/规则），输出关键指标与曲线。
- 增强缓存：分层（raw data/processed/report），并加“最后成功时间”。
- 结束后再次调用 testing agent 做 1 轮回归测试。

---

## 3) Next Actions (Immediate)
1. 执行 Phase 1：实现并运行 `test_core.py`，修到 12 项全绿。
2. 将 POC 逻辑抽取为后端模块（保持输出一致），落库 schema。
3. 实现 `/api/refresh-data` + `/api/market/overview` + `/api/reports/*`，前端先做 Overview + Reports 最小闭环。
4. 加 Settings(输入持股数量) → Portfolio 权重联动。
5. Phase 2 完成后跑一次端到端测试并修复。

## 4) Success Criteria
- Phase 1：`python test_core.py` 稳定通过；生成中文 `sample_daily_report.md`；缺失数据有降级说明。
- Phase 2：Dashboard 6 页可用；手动刷新可用；持股数量更新后权重与建议联动；日报可查看/下载；系统不因单一数据源失败而崩溃。
- Phase 3：可解释性面板 + 阈值可编辑 + 基础回测可运行；再次端到端回归通过。
