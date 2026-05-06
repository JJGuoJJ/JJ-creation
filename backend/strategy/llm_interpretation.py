"""LLM-based deep interpretation (optional)."""
import asyncio
from typing import Dict, Any
from backend.core.config import EMERGENT_LLM_KEY
from backend.core.logger import logger


def build_prompt(payload: Dict[str, Any]) -> str:
    g = payload["global_fng"]["score"]
    c = payload["china_tech_fng"]["score"]
    regime = payload["regime"]["regime"]
    bands = payload["allocation"]
    top_secs = sorted(
        [(k, v["heat"]) for k, v in payload["sector_heat"].items() if v.get("heat") is not None],
        key=lambda x: -x[1])[:3]
    top_recs = payload.get("recommendations", [])[:5]
    sec_summary = ", ".join([f"{k}({h})" for k, h in top_secs])
    rec_summary = "; ".join([f"{r['symbol']} {r['name']}({r['action_cn']})" for r in top_recs])
    return f"""你是资深投行策略师。请基于以下今日数据，用中文输出 5–6 句专业策略解读（摸根/摩根风格）：

- 全球恐惧贪婪指数: {g}
- 中国科技恐惧贪婪指数: {c}
- 市场阶段: {regime}
- 建议权益仓位: {bands.get('equity',[55,65])[0]}%–{bands.get('equity',[55,65])[1]}%
- 建议 AI 科技仓位: {bands.get('ai_tech',[35,50])[0]}%–{bands.get('ai_tech',[35,50])[1]}%
- 热门赛道 (热度分): {sec_summary or '数据不足'}
- Top 5 个股推荐: {rec_summary or '暂无'}

要求：
1. 开头一句话定调。
2. 指出今日 1–2 个机会点、 1 个风险点。
3. 明日具体操作倾向。
4. 不要免责声明/空话/折扣语。
5. 控制在 180 字以内，语言简洁、体现专业。"""


def get_interpretation(payload: Dict[str, Any]) -> str:
    if not EMERGENT_LLM_KEY:
        return ""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        prompt = build_prompt(payload)

        async def run():
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id="pib_daily",
                           system_message="You are an elite investment bank strategist.")
            chat.with_model("openai", "gpt-4o-mini")
            return await chat.send_message(UserMessage(text=prompt))
        try:
            return asyncio.run(run())
        except RuntimeError:
            # Already in event loop (FastAPI). Use new loop.
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(run())
            finally:
                loop.close()
    except Exception as e:
        logger.warning(f"LLM interpretation failed: {e}")
        return ""
