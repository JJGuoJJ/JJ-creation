import React from "react";
import { Card, CardContent } from "./ui/card";
import { Progress } from "./ui/progress";
import ActionBadge from "./ActionBadge";
import { cn } from "../lib/utils";
import { Flame, ShieldAlert, Activity } from "lucide-react";

function barColor(heat) {
  if (heat == null) return "bg-slate-500";
  if (heat < 35) return "bg-emerald-500";
  if (heat < 55) return "bg-cyan-500";
  if (heat < 75) return "bg-amber-500";
  return "bg-red-500";
}

export default function SectorHeatList({ sectors, market }) {
  if (!sectors || sectors.length === 0) {
    return (
      <Card><CardContent className="p-5 text-sm text-muted-foreground">暂无赛道数据</CardContent></Card>
    );
  }
  return (
    <Card>
      <CardContent className="p-4 md:p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">赛道热度排名 · AI Chain Heat</div>
            <div className="text-sm text-foreground mt-0.5">中文赛道、热度、动作建议</div>
          </div>
        </div>
        <div className="space-y-2.5">
          {sectors.map((s) => (
            <div
              key={s.sector}
              data-testid="sector-heat-score-row"
              className="grid grid-cols-12 items-center gap-3 p-2.5 rounded-md hover:bg-muted/40 transition-colors"
            >
              <div className="col-span-3 text-sm font-medium">{s.sector}</div>
              <div className="col-span-5 flex items-center gap-2">
                <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className={cn("h-full rounded-full transition-all", barColor(s.heat_score))}
                    style={{ width: `${Math.min(100, Math.max(0, s.heat_score || 0))}%` }}
                  />
                </div>
                <span className="font-mono tabular-nums text-sm w-10 text-right">{s.heat_score?.toFixed?.(1) ?? "—"}</span>
              </div>
              <div className="col-span-2 text-[11px] text-muted-foreground font-mono flex items-center gap-2">
                {s.detail?.r20_avg != null && (
                  <span title="20日均涨幅">{s.detail.r20_avg >= 0 ? "+" : ""}{s.detail.r20_avg.toFixed(1)}%</span>
                )}
                {s.risk != null && s.risk > 0 && (
                  <span className="inline-flex items-center text-amber-300" title="风险罚分">
                    <ShieldAlert className="h-3 w-3" /> {s.risk}
                  </span>
                )}
              </div>
              <div className="col-span-2 flex justify-end">
                <ActionBadge action={s.action} />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
