import React from "react";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { cn } from "../lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

const REGIME_STYLES = {
  "Extreme Fear":  { bg: "from-emerald-500/20 to-emerald-700/10", text: "text-emerald-300", border: "border-emerald-500/30", icon: TrendingDown },
  "Fear":          { bg: "from-emerald-500/15 to-cyan-700/5",     text: "text-emerald-200", border: "border-emerald-500/25", icon: TrendingDown },
  "Neutral":       { bg: "from-slate-500/15 to-slate-700/10",     text: "text-slate-200",  border: "border-slate-500/25",  icon: Minus },
  "Greed":         { bg: "from-amber-500/15 to-orange-700/10",    text: "text-amber-300",  border: "border-amber-500/25",  icon: TrendingUp },
  "Extreme Greed": { bg: "from-orange-500/20 to-red-700/10",      text: "text-orange-300", border: "border-orange-500/30", icon: TrendingUp },
  "Bubble Risk":   { bg: "from-red-500/25 to-rose-700/15",        text: "text-red-300",    border: "border-red-500/35",    icon: TrendingUp },
};

export default function MarketPhaseCard({ regime, regimeCN, score, action, missingSources }) {
  const style = REGIME_STYLES[regime] || REGIME_STYLES.Neutral;
  const Icon = style.icon;
  return (
    <Card data-testid="market-phase-card" className={cn("relative overflow-hidden border", style.border)}>
      <div className={cn("absolute inset-0 bg-gradient-to-br opacity-100 pointer-events-none", style.bg)} />
      <CardContent className="relative p-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5">Market Phase · 市场阶段</div>
        <div className="flex items-center gap-3 mb-2">
          <div className={cn("font-semibold text-3xl md:text-4xl tracking-tight", style.text)} data-testid="market-phase-name">
            {regimeCN || regime || "—"}
          </div>
          <Icon className={cn("h-6 w-6", style.text)} />
        </div>
        <div className="flex items-center gap-2 mb-3">
          <Badge variant="outline" className="font-mono text-xs">{regime}</Badge>
          <Badge variant="secondary" className="font-mono text-xs">综合分 {score?.toFixed?.(1) ?? score ?? "—"}</Badge>
        </div>
        <div className="text-sm text-foreground/90 leading-relaxed">
          <span className="text-muted-foreground">建议动作 · </span>
          <span className="font-medium">{action || "—"}</span>
        </div>
        {missingSources?.length > 0 && (
          <div className="mt-3 text-[11px] text-amber-400/90 leading-relaxed">
            ⚠ 部分数据源丢失: {missingSources.slice(0, 3).join(", ")}{missingSources.length > 3 ? "..." : ""}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
