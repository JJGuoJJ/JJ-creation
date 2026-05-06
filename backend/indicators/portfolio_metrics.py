"""Portfolio diagnosis: maps current_positions+shares -> weights, sector exposure, deviation."""
from typing import Dict, Any, List
from backend.core.config import get_portfolio
from backend.indicators.technical import compute_indicators
from backend.data_providers import akshare_provider, yfinance_provider


USD_CNY = 7.2  # rough


def diagnose_portfolio(allocation: Dict[str, Any], sector_heat: Dict[str, Any]) -> Dict[str, Any]:
    positions = get_portfolio()
    rows = []
    total_value_cny = 0.0
    for sym, info in positions.items():
        market = info.get("market", "CN")
        sector = info.get("sector", "")
        name = info.get("name", sym)
        shares = float(info.get("shares", 0) or 0)
        df = None
        if market == "CN":
            df = akshare_provider.fetch_a_stock(sym)
        else:
            df = yfinance_provider.fetch_history(sym)
        last_close = None; chg_pct = None; rsi = None
        if df is not None:
            ind = compute_indicators(df)
            last_close = ind.get("last_close"); chg_pct = ind.get("chg_pct"); rsi = ind.get("rsi_14")
        # market value in CNY
        if last_close and shares:
            mv = last_close * shares
            if market != "CN":
                mv *= USD_CNY
        else:
            mv = 0.0
        total_value_cny += mv
        rows.append({
            "symbol": sym,
            "name": name,
            "sector": sector,
            "market": market,
            "shares": shares,
            "price": last_close,
            "chg_pct": chg_pct,
            "rsi": rsi,
            "market_value_cny": mv,
        })
    # Compute weight
    if total_value_cny > 0:
        for r in rows:
            r["weight"] = round(r["market_value_cny"] / total_value_cny * 100, 2)
    else:
        # equal weight
        n = len(rows)
        for r in rows:
            r["weight"] = round(100.0 / n, 2) if n > 0 else 0.0

    # Sector aggregation
    sector_weights: Dict[str, float] = {}
    for r in rows:
        sector_weights[r["sector"]] = sector_weights.get(r["sector"], 0) + r["weight"]
    sector_breakdown = sorted(
        [{"sector": k, "weight": round(v, 2),
          "heat": (sector_heat.get(k) or {}).get("heat")} for k, v in sector_weights.items()],
        key=lambda x: -x["weight"]
    )

    # Group buckets
    ai_tech_sectors = {
        "\u5149\u6a21\u5757", "\u5148\u8fdb\u5c01\u88c5", "HBM\u5b58\u50a8", "\u5b58\u50a8\u82af\u7247",
        "\u7535\u529b\u6db2\u51b7", "AI\u670d\u52a1\u5668", "AI\u7b97\u529b", "\u5168\u7403AI\u82af\u7247",
        "\u5168\u7403AI\u5e73\u53f0", "\u534a\u5bfc\u4f53\u6d4b\u8bd5", "\u534a\u5bfc\u4f53\u8bbe\u5907",
        "\u5149\u901a\u4fe1\u6fc0\u5149", "\u4fe1\u521b\u8f6f\u4ef6", "\u4fe1\u521b\u786c\u4ef6",
        "\u6d88\u8d39\u7535\u5b50\u5236\u9020", "\u70ed\u7ba1\u7406", "\u8f6f\u4ef6\u670d\u52a1",
        "\u519b\u5de5\u7535\u5b50", "\u56fe\u50cf\u4f20\u611f\u5668",
    }
    packaging_hbm_cooling = {
        "\u5148\u8fdb\u5c01\u88c5", "HBM\u5b58\u50a8", "\u7535\u529b\u6db2\u51b7",
        "\u534a\u5bfc\u4f53\u6d4b\u8bd5", "\u534a\u5bfc\u4f53\u8bbe\u5907",
    }
    gold_energy_military = {
        "\u9ec4\u91d1", "\u77f3\u6cb9", "\u77f3\u6cb9\u77f3\u5316", "\u6cb9\u670d",
        "\u519b\u5de5", "\u519b\u5de5\u53d1\u52a8\u673a", "\u519b\u5de5\u7535\u5b50",
        "\u949b\u6750\u6599\u519b\u5de5", "\u536b\u661f\u519b\u5de5", "\u536b\u661f\u901a\u4fe1",
        "\u6838\u7535\u5de5\u7a0b", "\u6838\u5de5\u4e1a\u88c5\u5907", "\u80fd\u6e90",
    }
    crypto = {"\u6bd4\u7279\u5e01\u52a0\u5bc6"}

    cur_ai_tech = sum(r["weight"] for r in rows if r["sector"] in ai_tech_sectors)
    cur_packaging = sum(r["weight"] for r in rows if r["sector"] in packaging_hbm_cooling)
    cur_gold = sum(r["weight"] for r in rows if r["sector"] in gold_energy_military)
    cur_btc = sum(r["weight"] for r in rows if r["sector"] in crypto)
    cur_equity = sum(r["weight"] for r in rows)  # all stocks (excluding cash)

    # Recommendation actions per holding
    add_list = []
    trim_list = []
    for r in rows:
        sec = r["sector"]
        sec_h = (sector_heat.get(sec) or {}).get("heat")
        rsi = r.get("rsi") or 50
        chg = r.get("chg_pct") or 0
        if sec_h is not None and sec_h > 70 and rsi < 65:
            add_list.append({**r, "reason": f"\u8d5b\u9053\u70ed\u5ea6\u9ad8({sec_h:.0f}), \u4e2a\u80a1\u672a\u8fc7\u70ed\uff0c\u53ef\u9002\u5f53\u52a0\u4ed3"})
        elif rsi > 80:
            trim_list.append({**r, "reason": f"RSI={rsi:.0f}\u8fc7\u70ed\uff0c\u5efa\u8bae\u51cf\u4ed3"})
        elif sec_h is not None and sec_h < 35:
            trim_list.append({**r, "reason": f"\u8d5b\u9053\u70ed\u5ea6\u504f\u4f4e({sec_h:.0f})\uff0c\u8003\u8651\u51cf\u4ed3"})

    return {
        "rows": rows,
        "total_value_cny": round(total_value_cny, 2),
        "sector_breakdown": sector_breakdown,
        "current_buckets": {
            "equity": round(cur_equity, 2),
            "ai_tech": round(cur_ai_tech, 2),
            "packaging_hbm_cool": round(cur_packaging, 2),
            "gold_energy": round(cur_gold, 2),
            "btc": round(cur_btc, 2),
            "cash": round(max(0, 100 - cur_equity), 2),
        },
        "target_bands": allocation,
        "add_list": add_list[:8],
        "trim_list": trim_list[:8],
    }
