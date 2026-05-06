import React from "react";
import { cn } from "../lib/utils";

const MAP = {
  "加仓":   "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  "回调加仓": "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  "小仓位布局": "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
  "超卖小仓位": "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
  "持有":   "bg-slate-500/15 text-slate-200 border-slate-500/30",
  "观望":   "bg-slate-500/15 text-slate-200 border-slate-500/30",
  "等待":   "bg-slate-500/15 text-slate-200 border-slate-500/30",
  "减仓":   "bg-amber-500/15 text-amber-300 border-amber-500/30",
  "减仓止盈": "bg-amber-500/15 text-amber-300 border-amber-500/30",
  "回避":   "bg-red-500/15 text-red-300 border-red-500/30",
  "回避追涨": "bg-red-500/15 text-red-300 border-red-500/30",
  "风险控制": "bg-red-500/15 text-red-300 border-red-500/30",
};

export default function ActionBadge({ action, className }) {
  const cls = MAP[action] || "bg-muted text-foreground border-border";
  return (
    <span data-testid="action-badge" className={cn("inline-flex items-center text-[11px] font-medium px-2 py-0.5 rounded-md border", cls, className)}>
      {action || "—"}
    </span>
  );
}
