# 个人投行系统 · Personal Investment Bank System (MVP v1)

让你拥有接近美国投行专业人员的市场监控、风险判断和仓位决策能力。

## 技术栈

- **Backend**: Python 3.11 · FastAPI · SQLAlchemy + SQLite · APScheduler
- **Frontend**: React 19 · shadcn/ui · Tailwind · Recharts · ReactMarkdown
- **Data Sources**: akshare（A股，含 Sina fallback）· yfinance（全球）· Alternative.me（Crypto F&G）
- **AI**: Emergent Universal LLM Key（GPT-4o-mini，深度策略解读）

## 核心能力

1. **数据采集模块化**：A股个股/指数（akshare），美股/ETF/加密（yfinance），Crypto F&G。失败时自动磁盘缓存或跳过，并在报告中标记缺失。
2. **核心指标**：MA(5/10/20/60/120/200)、RSI、20/60/120日收益、最大回撤、20日波动率、量比。
3. **三大情绪指数**：
   - Global Fear & Greed（VIX 25% + Nasdaq200MA 20% + SOXX 15% + UST10Y 10% + DXY 10% + BTC/CryptoFNG 10% + S&P500 10%）
   - China Tech F&G（科创/创业板/深成趋势 25% + 两市成交额分位 20% + CSI300 200MA 20% + 估值偏离 15%）
   - AI Chain Heat（按赛道：动量 35% + 量能 25% + 广度 20% + 风险罚分 20%）
4. **市场阶段识别**：Extreme Fear / Fear / Neutral / Greed / Extreme Greed / Bubble Risk
5. **仓位建议引擎**：每个 Regime 给出权益、AI 科技、封装/HBM/液冷、黄金能源、比特币、现金的区间。
6. **个股推荐**：综合分 = 25% 赛道热度 + 20% 动量 + 15% 回调性价比 + 15% 相对强度 + 10% 风险控制 + 10% 新闻催化 + 5% 适配度。输出动作：回调加仓/小仓位布局/持有/等待/减仓止盈/回避追涨。
7. **中文日报**：含市场阶段、F&G 分数、仓位建议、赛道排名、Top 10 观察池、风险信号、明日操作计划。
8. **持仓诊断**：录入持股数量后自动按市值估算权重 + 当前 vs 目标偏离 + 加仓/减仓建议。

## 启动

后端默认端口 **8001**，前端 **3000**，Supervisor 自动管理。

```bash
# 健康检查
curl http://localhost:8001/api/health

# 手动刷新数据（需 60-280 秒）
curl -X POST http://localhost:8001/api/refresh-data?use_llm=true
```

## 自动调度

每日 **北京时间 16:30**（A 股收盘后）自动运行 daily pipeline。

## 目录结构

```
backend/
├── server.py                    # FastAPI 入口
├── main_pipeline.py             # 日更主流程
├── core/                        # config / logger / utils
├── data_providers/              # akshare / yfinance / alternative_fng
├── indicators/                  # technical / fear_greed / sector_heat / portfolio_metrics
├── strategy/                    # regime_detector / allocation_engine / recommendation_engine / llm_interpretation
├── report/                      # daily_report (Jinja2 模板风格)
├── scheduler/                   # APScheduler jobs
├── storage/                     # SQLAlchemy models + repository
├── config_files/                # YAML 配置（portfolio/watchlist/sectors/thresholds...）
└── data/
    ├── pib.sqlite               # 主数据库
    └── cache/                   # 行情数据磁盘缓存

frontend/src/
├── App.js                       # 路由入口
├── components/                  # Sidebar / Header / MarketPhaseCard / FearGreedGauge / AllocationDonut / SectorHeatList / ActionBadge
├── pages/                       # Overview / Portfolio / Sectors / Watchlist / Sentiment / Reports / Settings
└── lib/api.js                   # API client (axios)

config_files/portfolio.yaml      # 当前 29 只持仓
config_files/watchlist.yaml      # 36 只观察池
```

## API 端点

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 + 数据日期 |
| `/api/refresh-data` | POST | 触发完整 pipeline |
| `/api/market/overview` | GET | 今日 Regime + 三大情绪 + 仓位建议 |
| `/api/sectors` | GET | 赛道热度排名 |
| `/api/watchlist` | GET | 观察池排序（filter: sector/market/action） |
| `/api/recommendations/today` | GET | Top 推荐 |
| `/api/portfolio` | GET | 持仓快照 |
| `/api/portfolio/diagnose` | GET | 持仓诊断（buckets/add/trim） |
| `/api/portfolio/update` | POST | 批量更新持股数量 |
| `/api/reports/list` | GET | 历史报告列表 |
| `/api/reports/{date}` | GET | 单份报告（含 markdown） |
| `/api/reports/{date}/download` | GET | 下载 Markdown |
| `/api/indicators/fear-greed` | GET | F&G 历史曲线 |
| `/api/settings/risk-profile` | GET/POST | 风险偏好 |
| `/api/settings/thresholds` | GET/POST | 阈值编辑 |
| `/api/backtest/run` | POST | 简易回测（symbol + days） |

## 阈值与策略可在 UI 编辑

- 风险偏好：保守 / 平衡 / 中高（默认）/ 进取
- F&G 阶段阈值：可调
- 风险信号触发条件：可调

## 第二版规划

- 新闻情绪深度分析（Alpha Vantage News Sentiment）
- SEC 财报/A股年报解析
- 投行报告自动摘要
- 复杂回测（多因子 + Regime 切换）
- Telegram / Email 告警
- 多账户管理
- LLM 智能问答（基于本地数据库）
