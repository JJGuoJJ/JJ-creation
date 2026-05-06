"""Daily report generator (Markdown)."""
from typing import Dict, Any
from datetime import datetime
from backend.core.utils import now_bj


def generate_daily_report(payload: Dict[str, Any]) -> str:
    today = payload.get("date", now_bj().strftime("%Y-%m-%d"))
    g = payload["global_fng"]
    c = payload["china_tech_fng"]
    regime_d = payload["regime"]
    a = payload["allocation"]
    sectors = payload.get("sector_heat", {})
    recs = payload.get("recommendations", [])
    portfolio = payload.get("portfolio", {})
    llm_text = payload.get("llm_interpretation", "") or "本人策略台：按规则引擎生成。"
    missing_sources = payload.get("missing_sources", [])

    lines = []
    lines.append(f"# 个人投行系统日报 · {today}")
    lines.append(f"")
    lines.append(f"> **市场阶段**：**{regime_d['regime_cn']} ({regime_d['regime']})**  ·  综合分：**{regime_d['combined_score']}**  ·  **动作**：{regime_d['action']}")

    if missing_sources:
        lines.append(f"\n> ⚠️ 部分数据源不可用：{', '.join(missing_sources)}\u3002已跳过并标记。")

    lines.append("\n## 一、今日市场状态")
    lines.append(f"- 🌍 **全球恐惧贪婪指数**：**{g['score']} / 100**")
    lines.append(f"- 🇨🇳 **中国科技恐惧贪婪指数**：**{c['score']} / 100**")
    lines.append(f"- ⚡ **AI 产业链峰值热度**：**{regime_d['ai_peak_heat']:.1f} / 100**")
    if payload.get("crypto_fng"):
        cf = payload["crypto_fng"]
        lines.append(f"- ₿ **Crypto Fear & Greed**：**{cf.get('current', '-')} ({cf.get('classification', '-')})**")
    lines.append(f"\n**策略师解读**：\n> {llm_text}")

    lines.append("\n## 二、今日仓位建议")
    lines.append("| 类别 | 建议区间 |")
    lines.append("|:---|:---|")
    lines.append(f"| 总权益 | **{a.get('equity',[55,65])[0]}% – {a.get('equity',[55,65])[1]}%** |")
    lines.append(f"| AI 科技 | {a.get('ai_tech',[35,50])[0]}% – {a.get('ai_tech',[35,50])[1]}% |")
    lines.append(f"| 先进封装 / HBM / 电力液冷 | {a.get('packaging_hbm_cool',[20,30])[0]}% – {a.get('packaging_hbm_cool',[20,30])[1]}% |")
    lines.append(f"| 黄金 / 能源 / 军工 | {a.get('gold_energy',[15,25])[0]}% – {a.get('gold_energy',[15,25])[1]}% |")
    lines.append(f"| 比特币 | {a.get('btc',[2,7])[0]}% – {a.get('btc',[2,7])[1]}% |")
    lines.append(f"| 现金 | {a.get('cash',[15,25])[0]}% – {a.get('cash',[15,25])[1]}% |")

    lines.append("\n## 三、赛道热度排名")
    lines.append("| 赛道 | 热度分 | 20日均涨幅 | 平均RSI | 量比 | 风险罚分 | 动作 |")
    lines.append("|:---|---:|---:|---:|---:|---:|:---|")
    sl = sorted([(k, v) for k, v in sectors.items() if v.get("heat") is not None], key=lambda x: -x[1]["heat"])
    for sec, s in sl:
        lines.append(f"| {sec} | **{s['heat']}** | {s['r20_avg']:+.2f}% | {s['rsi_avg']:.1f} | {s['vol_ratio']:.2f}x | {s['risk_penalty']} | {s.get('action','-')} |")

    lines.append("\n## 四、高价值观察池 Top 10")
    lines.append("| # | 代码 | 名称 | 赛道 | 怼合分 | 动作 | 理由 |")
    lines.append("|:---|:---|:---|:---|---:|:---|:---|")
    for i, rec in enumerate(recs[:10], 1):
        lines.append(f"| {i} | `{rec['symbol']}` | {rec['name']} | {rec['sector']} | {rec['score']} | **{rec['action_cn']}** | {rec['reason']} |")

    if portfolio.get("rows"):
        lines.append("\n## 五、持仓诊断")
        b = portfolio.get("current_buckets", {})
        bands = portfolio.get("target_bands", {})
        lines.append(f"- 当前总市值（CNY估算）：**{portfolio.get('total_value_cny', 0):,.2f}**")
        lines.append(f"- 当前仓位分布：权益 {b.get('equity',0)}% / AI科技 {b.get('ai_tech',0)}% / 封装HBM液冷 {b.get('packaging_hbm_cool',0)}% / 黄金能源 {b.get('gold_energy',0)}% / BTC {b.get('btc',0)}% / 现金 {b.get('cash',0)}%")
        if portfolio.get("add_list"):
            lines.append("\n**建议加仓**\uff1a")
            for r in portfolio["add_list"][:5]:
                lines.append(f"- `{r['symbol']}` {r['name']} ({r['sector']})\u2014 {r['reason']}")
        if portfolio.get("trim_list"):
            lines.append("\n**建议减仓**\uff1a")
            for r in portfolio["trim_list"][:5]:
                lines.append(f"- `{r['symbol']}` {r['name']} ({r['sector']})\u2014 {r['reason']}")

    lines.append("\n## 六、今日风险信号")
    flags = []
    for sec, s in sl:
        if s.get("risk_penalty", 0) >= 25:
            flags.append(f"- 🔴 **{sec}** 赛\u9053\u8fc7\u70ed\uff08\u98ce\u9669\u7f5a\u5206 {s['risk_penalty']}\uff09\uff0c\u4e0d\u5efa\u8bae\u8ffd\u6da8")
        elif s.get("heat", 0) > 75:
            flags.append(f"- 🟡 **{sec}** 赛\u9053\u70ed\u5ea6\u504f\u9ad8 ({s['heat']})")
    if g["score"] > 85:
        flags.append(f"- 🔴 全球情绪接\u8fd1\u6781\u5ea6\u8d2a\u5a6a ({g['score']})")
    if c["score"] > 85:
        flags.append(f"- 🔴 A\u80a1\u79d1\u6280\u60c5\u7eea\u63a5\u8fd1\u6781\u5ea6\u8d2a\u5a6a ({c['score']})")
    if g["score"] < 25:
        flags.append(f"- 🟢 全球\u60c5\u7eea\u6781\u5ea6\u6050\u614c ({g['score']})\uff0c\u53ef\u5206\u6279\u4f4e\u5438")
    if c["score"] < 25:
        flags.append(f"- 🟢 A\u80a1\u79d1\u6280\u60c5\u7eea\u6781\u5ea6\u6050\u614c ({c['score']})")
    if not flags:
        flags.append("- 暂无重大风险信号")
    lines.extend(flags)

    lines.append("\n## 七、明日操作计划")
    rg = regime_d["regime"]
    if rg in ["Extreme Fear", "Fear"]:
        lines += [
            "1. **不恐慌抛售**；按分\u6279\u52a0\u4ed3\u8ba1\u5212\u6267\u884c\u7b2c\u4e00\u6863\u4e70\u5165",
            "2. 优先\u4e70\u5165 Top 3 推\u8350\uff08\u5206\u6570\u6700\u9ad8\uff09\uff0c\u6bcf\u7b14 \u2264 \u8ba1\u5212\u4ed3\u4f4d\u7684 1/3",
            "3. 保\u7559\u81f3\u5c11 20% \u73b0\u91d1\u5e94\u5bf9\u53ef\u80fd\u7684\u4e8c\u6b21\u63a2\u5e95",
        ]
    elif rg == "Neutral":
        lines += [
            "1. 持有\u73b0\u6709\u6838\u5fc3\u4ed3\u4f4d\uff0c\u4e0d\u8ffd\u6da8\u4e0d\u6050\u614c",
            "2. 关\u6ce8\u56de\u8c03\u81f3\u5747\u7ebf\u7684\u9ad8\u5206\u4e2a\u80a1\uff0c\u5206\u6279\u5c0f\u4ed3\u5e03\u5c40",
            "3. 新\u589e\u4ed3\u4f4d\u4f18\u5148\u914d\u7f6e\u70ed\u5ea6\u9ad8\u4f46\u98ce\u9669\u7f5a\u5206<15\u7684\u8d5b\u9053",
        ]
    elif rg == "Greed":
        lines += [
            "1. **不追\u9ad8**\uff0c\u6301\u6709\u6838\u5fc3\uff0c\u5bf9\u6da8\u5e45\u8fc7\u5927\u7684\u4e2a\u80a1\u8bbe\u7f6e\u6b62\u76c8\u4f4d",
            "2. 分\u6279\u5151\u73b0\u9ad8\u5f39\u6027\u5c0f\u7968\u5229\u6da6 (\u8bc4\u5206 Avoid/Trim)",
            "3. 新\u589e\u4ed3\u4f4d\u4fdd\u5b88\uff1a\u4ec5\u9650\u9ad8\u5206 + \u56de\u8c03 + \u4f4e\u98ce\u9669\u7f5a\u5206\u4e2a\u80a1",
        ]
    elif rg == "Extreme Greed":
        lines += [
            "1. **高弹\u6027\u4ed3\u5206\u6279\u6b62\u76c8**\uff0c\u964d\u4f4e\u9ad8 beta \u6301\u4ed3\u6bd4\u4f8b",
            "2. 保\u7559\u6838\u5fc3\u4ed3\uff0c\u5207\u5fcc\u4e00\u6b21\u6027\u6e05\u4ed3",
            "3. 新\u589e\u4ed3\u4f4d\u6682\u505c\uff0c\u63d0\u9ad8\u73b0\u91d1\u81f3 30% \u4ee5\u4e0a",
        ]
    else:
        lines += [
            "1. **立即\u964d\u4f4e\u9ad8 beta \u4ed3\u4f4d**\u81f3 15% \u4ee5\u4e0b",
            "2. 兑\u73b0\u6da8\u5e45\u6700\u5927\u7684\u4e2a\u80a1 2/3 \u4ed3\u4f4d",
            "3. 加\u4ed3\u9ec4\u91d1/\u73b0\u91d1\uff0c\u51c6\u5907\u63a5\u76d8\u4f18\u8d28\u8d44\u4ea7",
        ]

    lines.append("\n---")
    lines.append("*本日报由个人投行系统自动生成 · 数据源: akshare + yfinance + Alternative.me*")
    lines.append(f"*生成时间: {now_bj().strftime('%Y-%m-%d %H:%M:%S')} CST*")
    return "\n".join(lines)
