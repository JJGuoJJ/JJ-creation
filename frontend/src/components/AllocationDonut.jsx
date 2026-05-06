import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardContent } from "./ui/card";

const COLORS = ["#14B8A6", "#0EA5E9", "#F59E0B", "#84CC16", "#F43F5E", "#94A3B8"];

const LABELS = {
  equity: "总权益",
  ai_tech: "AI科技",
  packaging_hbm_cool: "封装/HBM/液冷",
  gold_energy: "黄金能源军工",
  btc: "比特币",
  cash: "现金",
};

export default function AllocationDonut({ allocation, current }) {
  if (!allocation) return null;
  const data = Object.entries(allocation)
    .filter(([k, v]) => Array.isArray(v) && v.length === 2 && k !== "equity")
    .map(([k, v], i) => ({
      name: LABELS[k] || k,
      key: k,
      midpoint: (v[0] + v[1]) / 2,
      min: v[0],
      max: v[1],
      color: COLORS[i % COLORS.length],
    }));
  return (
    <Card data-testid="allocation-donut-chart">
      <CardContent className="p-4 md:p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">仓位建议 · Recommended Allocation</div>
            <div className="text-sm text-foreground mt-0.5">总权益 {allocation.equity?.[0]}% – {allocation.equity?.[1]}%</div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div className="md:col-span-2 h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data} dataKey="midpoint" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2}>
                  {data.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} stroke="hsl(var(--background))" />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  formatter={(v, n, p) => [`${p?.payload?.min}\u2013${p?.payload?.max}%`, p?.payload?.name]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="md:col-span-3 space-y-2">
            {data.map((d) => {
              const cur = (current && current[d.key]) ?? null;
              const inside = cur != null && cur >= d.min && cur <= d.max;
              return (
                <div key={d.key} className="flex items-center gap-3 text-sm">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: d.color }} />
                  <span className="flex-1 text-foreground">{d.name}</span>
                  <span className="font-mono text-xs text-muted-foreground">{d.min}–{d.max}%</span>
                  {cur != null && (
                    <span
                      className={`ml-2 inline-flex items-center text-[10px] font-mono px-1.5 py-0.5 rounded ${
                        inside ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"
                      }`}
                      title="当前仓位"
                    >
                      当前 {cur?.toFixed?.(1) ?? cur}%
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
