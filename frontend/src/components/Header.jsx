import React, { useEffect, useState } from "react";
import { Sun, Moon, RefreshCcw, Globe, AlertCircle } from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import api from "../lib/api";
import { toast } from "sonner";

export default function Header({ market, setMarket, dark, setDark, lastUpdate, onRefreshDone }) {
  const [refreshing, setRefreshing] = useState(false);
  const refresh = async () => {
    setRefreshing(true);
    toast.info("刷新中，约需 60-90 秒（拼接 akshare/yfinance 数据）…");
    try {
      const r = await api.refreshData(true);
      if (r.missing_sources?.length) {
        toast.warning(`刷新完成，但部分数据源丢失: ${r.missing_sources.join(", ")}`);
      } else {
        toast.success(`刷新完成 · ${r.regime_cn} · 耗时 ${r.elapsed_seconds}s`);
      }
      onRefreshDone?.();
    } catch (e) {
      toast.error(`刷新失败: ${e?.response?.data?.detail || e.message}`);
    } finally {
      setRefreshing(false);
    }
  };
  return (
    <header data-testid="app-header" className="sticky top-0 z-40 h-14 border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="h-full px-4 lg:px-6 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="text-sm text-muted-foreground hidden lg:block">个人投行系统</div>
          {lastUpdate && (
            <Badge variant="outline" className="font-mono text-[11px]" data-testid="last-update-badge">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse-soft" />
              {lastUpdate}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setMarket(market === "CN" ? "US" : "CN")}
            data-testid="market-color-convention-toggle"
            className="font-mono text-xs gap-1"
          >
            <Globe className="h-3.5 w-3.5" />
            {market === "CN" ? "A股色例 (红涨绿跌)" : "美股色例 (绿涨红跌)"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDark(!dark)}
            data-testid="theme-toggle"
            className="px-2.5"
          >
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <Button
            size="sm"
            onClick={refresh}
            disabled={refreshing}
            data-testid="refresh-data-button"
            className="gap-1.5"
          >
            <RefreshCcw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin" : ""}`} />
            {refreshing ? "刷新中…" : "刷新数据"}
          </Button>
        </div>
      </div>
    </header>
  );
}
