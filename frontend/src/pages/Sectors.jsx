import React, { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import ActionBadge from "../components/ActionBadge";
import api from "../lib/api";
import { Flame, Activity, ShieldAlert } from "lucide-react";

export default function Sectors({ refreshTick }) {
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    api.sectors().then((r) => setSectors(r.sectors || [])).finally(() => setLoading(false));
  }, [refreshTick]);

  const filtered = sectors.filter((s) => !search || s.sector.includes(search));

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">赛道 · Sectors</h1>
          <p className="text-sm text-muted-foreground mt-1">AI 产业链与核心赛道热度、风险、动作建议</p>
        </div>
        <Input data-testid="sectors-search" placeholder="搜索赛道" value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-xs" />
      </div>

      {loading ? (
        <div className="text-sm text-muted-foreground">加载中…</div>
      ) : filtered.length === 0 ? (
        <Card><CardContent className="p-6 text-sm text-muted-foreground">请先点右上角【刷新数据】。</CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((s) => <SectorCard key={s.sector} s={s} />)}
        </div>
      )}
    </div>
  );
}

function SectorCard({ s }) {
  const heat = s.heat_score;
  const heatColor = heat == null ? "text-slate-400" : heat < 35 ? "text-emerald-300" : heat < 55 ? "text-cyan-300" : heat < 75 ? "text-amber-300" : "text-red-300";
  const heatBg = heat == null ? "from-slate-500/10" : heat < 35 ? "from-emerald-500/10" : heat < 55 ? "from-cyan-500/10" : heat < 75 ? "from-amber-500/10" : "from-red-500/10";
  const d = s.detail || {};
  return (
    <Card data-testid="sector-card" className="relative overflow-hidden hover:shadow-lg transition-shadow">
      <div className={`absolute inset-0 bg-gradient-to-br ${heatBg} to-transparent opacity-80 pointer-events-none`} />
      <CardContent className="relative p-5">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">Sector · 赛道</div>
            <div className="text-lg font-semibold mt-1">{s.sector}</div>
          </div>
          <ActionBadge action={s.action} />
        </div>
        <div className="mt-4 flex items-end gap-2">
          <div className={`text-4xl font-mono tabular-nums font-semibold ${heatColor}`}>{heat?.toFixed?.(1) ?? "—"}</div>
          <div className="text-xs text-muted-foreground mb-1">热度分 / 100</div>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          <Stat label="动量分" value={d.momentum?.toFixed?.(1)} />
          <Stat label="量能分" value={d.volume?.toFixed?.(1)} />
          <Stat label="广度分" value={d.breadth?.toFixed?.(1)} />
          <Stat label="风险罚分" value={d.risk_penalty} icon={ShieldAlert} />
          <Stat label="20日均涨" value={d.r20_avg != null ? `${d.r20_avg >= 0 ? "+" : ""}${d.r20_avg.toFixed(1)}%` : "—"} />
          <Stat label="60日均涨" value={d.r60_avg != null ? `${d.r60_avg >= 0 ? "+" : ""}${d.r60_avg.toFixed(1)}%` : "—"} />
          <Stat label="平均RSI" value={d.rsi_avg?.toFixed?.(1)} />
          <Stat label="平均量比" value={d.vol_ratio != null ? `${d.vol_ratio.toFixed(2)}x` : "—"} />
        </div>
      </CardContent>
    </Card>
  );
}

function Stat({ label, value, icon: Icon }) {
  return (
    <div className="flex items-center justify-between text-xs border-b border-border/50 py-1">
      <span className="text-muted-foreground inline-flex items-center gap-1">
        {Icon && <Icon className="h-3 w-3" />} {label}
      </span>
      <span className="font-mono tabular-nums text-foreground">{value ?? "—"}</span>
    </div>
  );
}
