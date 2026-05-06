import React, { useEffect, useState, useMemo } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "../components/ui/select";
import ActionBadge from "../components/ActionBadge";
import api from "../lib/api";
import { ChevronDown, ChevronRight } from "lucide-react";

export default function Watchlist({ refreshTick }) {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("all");
  const [market, setMarket] = useState("all");
  const [action, setAction] = useState("all");
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    setLoading(true);
    api.watchlist().then((r) => setRecs(r.recommendations || [])).finally(() => setLoading(false));
  }, [refreshTick]);

  const sectorOptions = useMemo(() => Array.from(new Set(recs.map((r) => r.sector))).filter(Boolean).sort(), [recs]);
  const actionOptions = useMemo(() => Array.from(new Set(recs.map((r) => r.action_cn))).filter(Boolean).sort(), [recs]);

  const filtered = recs.filter((r) =>
    (sector === "all" || r.sector === sector) &&
    (market === "all" || r.market === market) &&
    (action === "all" || r.action_cn === action) &&
    (!search || r.symbol.toLowerCase().includes(search.toLowerCase()) || (r.name && r.name.includes(search)))
  );

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">观察池 · Watchlist</h1>
          <p className="text-sm text-muted-foreground mt-1">按综合分排序的股票推荐，点击展开查看技术指标与得分构成</p>
        </div>
        <Badge variant="outline" className="font-mono text-[11px]">{filtered.length} / {recs.length} 个标的</Badge>
      </div>

      <Card>
        <CardContent className="p-3 flex flex-wrap items-center gap-2">
          <Input data-testid="watchlist-search" placeholder="搜索代码/名称" value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-xs h-9" />
          <Select value={sector} onValueChange={setSector}>
            <SelectTrigger data-testid="filter-sector" className="h-9 w-[160px]"><SelectValue placeholder="赛道" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部赛道</SelectItem>
              {sectorOptions.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={market} onValueChange={setMarket}>
            <SelectTrigger data-testid="filter-market" className="h-9 w-[120px]"><SelectValue placeholder="市场" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部市场</SelectItem>
              <SelectItem value="CN">A股</SelectItem>
              <SelectItem value="US">美股</SelectItem>
              <SelectItem value="Crypto">加密</SelectItem>
            </SelectContent>
          </Select>
          <Select value={action} onValueChange={setAction}>
            <SelectTrigger data-testid="filter-action" className="h-9 w-[140px]"><SelectValue placeholder="动作" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部动作</SelectItem>
              {actionOptions.map((a) => <SelectItem key={a} value={a}>{a}</SelectItem>)}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="watchlist-table">
              <thead className="bg-muted/40 sticky top-0">
                <tr className="text-xs text-muted-foreground">
                  <th className="px-3 py-2 w-8"></th>
                  <th className="text-left px-3 py-2">#</th>
                  <th className="text-left px-3 py-2">代码</th>
                  <th className="text-left px-3 py-2">名称</th>
                  <th className="text-left px-3 py-2">赛道</th>
                  <th className="text-left px-3 py-2">市场</th>
                  <th className="text-right px-3 py-2">现价</th>
                  <th className="text-right px-3 py-2">20日</th>
                  <th className="text-right px-3 py-2">RSI</th>
                  <th className="text-right px-3 py-2">vs MA20</th>
                  <th className="text-right px-3 py-2">赛道热度</th>
                  <th className="text-right px-3 py-2">怼合分</th>
                  <th className="text-left px-3 py-2">动作</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={13} className="text-center text-sm text-muted-foreground py-8">加载中…</td></tr>
                )}
                {!loading && filtered.length === 0 && (
                  <tr><td colSpan={13} className="text-center text-sm text-muted-foreground py-8">没有符合条件的标的</td></tr>
                )}
                {filtered.map((r, i) => {
                  const exp = expanded[r.symbol];
                  const ind = r.indicators || {};
                  const isCN = r.market === "CN";
                  const r20 = ind.ret_20d ?? 0;
                  const r20Color = (isCN ? r20 > 0 : r20 > 0) ? (isCN ? "text-red-400" : "text-emerald-400") : (isCN ? "text-emerald-400" : "text-red-400");
                  return (
                    <React.Fragment key={r.symbol}>
                      <tr
                        className="border-t border-border hover:bg-muted/30 cursor-pointer"
                        data-testid="watchlist-row"
                        onClick={() => setExpanded((p) => ({ ...p, [r.symbol]: !exp }))}
                      >
                        <td className="px-3 py-2">{exp ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">{i + 1}</td>
                        <td className="px-3 py-2 font-mono text-xs">{r.symbol}</td>
                        <td className="px-3 py-2">{r.name}</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">{r.sector}</td>
                        <td className="px-3 py-2"><Badge variant="outline" className="text-[10px]">{r.market}</Badge></td>
                        <td className="px-3 py-2 font-mono text-right tabular-nums">{ind.last_close?.toFixed?.(2) ?? "—"}</td>
                        <td className={`px-3 py-2 font-mono text-right tabular-nums ${r20 > 0.01 ? r20Color : r20 < -0.01 ? r20Color : "text-muted-foreground"}`}>
                          {ind.ret_20d != null ? `${r20 > 0 ? "+" : ""}${r20.toFixed(1)}%` : "—"}
                        </td>
                        <td className="px-3 py-2 font-mono text-right tabular-nums">{ind.rsi_14?.toFixed?.(0) ?? "—"}</td>
                        <td className="px-3 py-2 font-mono text-right tabular-nums">{ind.pct_from_ma20 != null ? `${ind.pct_from_ma20 > 0 ? "+" : ""}${ind.pct_from_ma20.toFixed(1)}%` : "—"}</td>
                        <td className="px-3 py-2 font-mono text-right tabular-nums">{ind.sector_heat?.toFixed?.(0) ?? "—"}</td>
                        <td className="px-3 py-2 font-mono text-right tabular-nums font-semibold">{r.score?.toFixed?.(1) ?? "—"}</td>
                        <td className="px-3 py-2"><ActionBadge action={r.action_cn} /></td>
                      </tr>
                      {exp && (
                        <tr className="border-t border-border bg-muted/20">
                          <td colSpan={13} className="px-6 py-3">
                            <div className="text-xs text-foreground/90 leading-relaxed mb-2">{r.reason}</div>
                            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
                              <Mini label="60日收益" v={ind.ret_60d != null ? `${ind.ret_60d > 0 ? "+" : ""}${ind.ret_60d.toFixed(1)}%` : "—"} />
                              <Mini label="vs MA60" v={ind.pct_from_ma60 != null ? `${ind.pct_from_ma60 > 0 ? "+" : ""}${ind.pct_from_ma60.toFixed(1)}%` : "—"} />
                              <Mini label="vs MA200" v={ind.pct_from_ma200 != null ? `${ind.pct_from_ma200 > 0 ? "+" : ""}${ind.pct_from_ma200.toFixed(1)}%` : "—"} />
                              <Mini label="波动率20d" v={ind.vol_20d != null ? `${ind.vol_20d.toFixed(1)}%` : "—"} />
                              <Mini label="最大回撒20d" v={ind.mdd_120d != null ? `${ind.mdd_120d.toFixed(1)}%` : "—"} />
                              <Mini label="量比" v={ind.volume_ratio != null ? `${ind.volume_ratio.toFixed(2)}x` : "—"} />
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function Mini({ label, v }) {
  return (
    <div className="flex items-center justify-between px-2 py-1.5 rounded bg-card border border-border">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-mono tabular-nums">{v}</span>
    </div>
  );
}
