import React, { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import api from "../lib/api";
import { toast } from "sonner";
import { Save, ArrowUp, ArrowDown } from "lucide-react";

const CN_COLOR_UP = "text-red-400", CN_COLOR_DOWN = "text-emerald-400";
const US_COLOR_UP = "text-emerald-400", US_COLOR_DOWN = "text-red-400";
const PIE_COLORS = ["#14B8A6", "#0EA5E9", "#F59E0B", "#84CC16", "#F43F5E", "#94A3B8", "#A855F7", "#EC4899", "#06B6D4", "#22C55E"];

export default function Portfolio({ market, refreshTick }) {
  const [diag, setDiag] = useState(null);
  const [edits, setEdits] = useState({});
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const reload = () => {
    setLoading(true);
    api.portfolioDiagnose().then(setDiag).catch(() => setDiag(null)).finally(() => setLoading(false));
  };
  useEffect(() => { reload(); }, [refreshTick]);

  const onSave = async () => {
    const items = Object.entries(edits).map(([symbol, shares]) => ({ symbol, shares: parseFloat(shares) || 0 }));
    if (items.length === 0) { toast.info("没有修改"); return; }
    try {
      await api.portfolioUpdate(items);
      toast.success(`已保存 ${items.length} 项修改。请点 刷新数据 重算权重。`);
      setEdits({});
    } catch (e) {
      toast.error("保存失败: " + (e?.message || ""));
    }
  };

  if (loading) return <div className="text-sm text-muted-foreground">加载中…</div>;
  if (!diag) return <div className="text-sm text-muted-foreground">请先点右上角【刷新数据】按钮。</div>;

  const filtered = (diag.rows || []).filter((r) =>
    !search || r.symbol.toLowerCase().includes(search.toLowerCase()) ||
    (r.name && r.name.includes(search))
  );
  const sectorPie = (diag.sector_breakdown || [])
    .filter((s) => s.weight > 0)
    .map((s, i) => ({ ...s, color: PIE_COLORS[i % PIE_COLORS.length] }));
  const cur = diag.current_buckets || {};
  const tgt = diag.target_bands || {};

  const compareData = [
    { name: "AI\u79d1\u6280", current: cur.ai_tech || 0, target_min: tgt.ai_tech?.[0] || 0, target_max: tgt.ai_tech?.[1] || 0 },
    { name: "\u5c01\u88c5/HBM/\u6db2\u51b7", current: cur.packaging_hbm_cool || 0, target_min: tgt.packaging_hbm_cool?.[0] || 0, target_max: tgt.packaging_hbm_cool?.[1] || 0 },
    { name: "\u9ec4\u91d1\u80fd\u6e90\u519b\u5de5", current: cur.gold_energy || 0, target_min: tgt.gold_energy?.[0] || 0, target_max: tgt.gold_energy?.[1] || 0 },
    { name: "\u6bd4\u7279\u5e01", current: cur.btc || 0, target_min: tgt.btc?.[0] || 0, target_max: tgt.btc?.[1] || 0 },
    { name: "\u73b0\u91d1", current: cur.cash || 0, target_min: tgt.cash?.[0] || 0, target_max: tgt.cash?.[1] || 0 },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">持仓 · Portfolio</h1>
          <p className="text-sm text-muted-foreground mt-1">输入持股数量，系统按市值自动计算权重、赛道偏离与加减仓建议</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono text-[11px]">总市值估算 {Number(diag.total_value_cny || 0).toLocaleString()} CNY</Badge>
          <Button onClick={onSave} size="sm" disabled={Object.keys(edits).length === 0} data-testid="portfolio-save-button">
            <Save className="h-3.5 w-3.5 mr-1" /> 保存修改 ({Object.keys(edits).length})
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Card className="lg:col-span-5">
          <CardContent className="p-4 md:p-5">
            <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">赛道分布</div>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={sectorPie.length > 0 ? sectorPie : [{ sector: "未入持股数量", weight: 100, color: "#475569" }]} dataKey="weight" nameKey="sector" outerRadius={80} innerRadius={45} paddingAngle={1.5}>
                    {(sectorPie.length > 0 ? sectorPie : [{ color: "#475569" }]).map((s, i) => <Cell key={i} fill={s.color} stroke="hsl(var(--background))" />)}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                    formatter={(v, n) => [`${v.toFixed(2)}%`, n]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-1 max-h-40 overflow-auto pr-1 mt-2">
              {sectorPie.map((s) => (
                <div key={s.sector} className="text-[11px] flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
                  <span className="truncate">{s.sector}</span>
                  <span className="font-mono ml-auto">{s.weight.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-7">
          <CardContent className="p-4 md:p-5">
            <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">当前 vs 目标仓位</div>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={compareData} layout="vertical" margin={{ left: 0, right: 16, top: 0, bottom: 0 }}>
                  <CartesianGrid stroke="hsl(var(--border))" strokeDasharray="3 3" />
                  <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis type="category" dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} width={120} />
                  <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                  <Bar dataKey="current" fill="#14B8A6" name="\u5f53\u524d %" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="target_max" fill="#38BDF8" name="\u76ee\u6807\u4e0a\u9650 %" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="add">
        <TabsList>
          <TabsTrigger value="add" data-testid="tab-add"><ArrowUp className="h-3.5 w-3.5 mr-1" /> 建议加仓 ({diag.add_list?.length || 0})</TabsTrigger>
          <TabsTrigger value="trim" data-testid="tab-trim"><ArrowDown className="h-3.5 w-3.5 mr-1" /> 建议减仓 ({diag.trim_list?.length || 0})</TabsTrigger>
        </TabsList>
        <TabsContent value="add">
          <Card><CardContent className="p-3"><RecList list={diag.add_list || []} market={market} mood="add" /></CardContent></Card>
        </TabsContent>
        <TabsContent value="trim">
          <Card><CardContent className="p-3"><RecList list={diag.trim_list || []} market={market} mood="trim" /></CardContent></Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardContent className="p-4 md:p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted-foreground">持仓明细 · Holdings</div>
              <div className="text-sm text-foreground">在最右“持股数量”列中输入最新数量，点击 保存修改 后点右上角刷新。</div>
            </div>
            <Input data-testid="portfolio-search" placeholder="搜索代码/名称" value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-xs" />
          </div>
          <div className="overflow-x-auto rounded-md border border-border">
            <table className="w-full text-sm" data-testid="portfolio-holdings-table">
              <thead className="bg-muted/40 sticky top-0">
                <tr className="text-xs text-muted-foreground">
                  <th className="text-left px-3 py-2">代码</th>
                  <th className="text-left px-3 py-2">名称</th>
                  <th className="text-left px-3 py-2">赛道</th>
                  <th className="text-left px-3 py-2">市场</th>
                  <th className="text-right px-3 py-2">现价</th>
                  <th className="text-right px-3 py-2">涨跌</th>
                  <th className="text-right px-3 py-2">市值 (CNY)</th>
                  <th className="text-right px-3 py-2">权重</th>
                  <th className="text-right px-3 py-2">持股数量</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r) => {
                  const chg = r.chg_pct ?? 0;
                  const isCN = r.market === "CN";
                  const upCol = isCN ? CN_COLOR_UP : US_COLOR_UP;
                  const downCol = isCN ? CN_COLOR_DOWN : US_COLOR_DOWN;
                  const cls = chg > 0.01 ? upCol : chg < -0.01 ? downCol : "text-muted-foreground";
                  return (
                    <tr key={r.symbol} className="border-t border-border hover:bg-muted/30" data-testid="portfolio-holdings-row">
                      <td className="px-3 py-2 font-mono text-xs">{r.symbol}</td>
                      <td className="px-3 py-2">{r.name}</td>
                      <td className="px-3 py-2 text-xs text-muted-foreground">{r.sector}</td>
                      <td className="px-3 py-2"><Badge variant="outline" className="text-[10px]">{r.market}</Badge></td>
                      <td className="px-3 py-2 font-mono text-right tabular-nums">{r.price ? r.price.toFixed(2) : "—"}</td>
                      <td className={`px-3 py-2 font-mono text-right tabular-nums ${cls}`}>{r.chg_pct != null ? `${chg > 0 ? "+" : ""}${chg.toFixed(2)}%` : "—"}</td>
                      <td className="px-3 py-2 font-mono text-right tabular-nums">{r.market_value ? r.market_value.toLocaleString(undefined, { maximumFractionDigits: 0 }) : "—"}</td>
                      <td className="px-3 py-2 font-mono text-right tabular-nums">{r.weight != null ? `${r.weight.toFixed(2)}%` : "—"}</td>
                      <td className="px-3 py-2 text-right">
                        <Input
                          data-testid={`shares-input-${r.symbol}`}
                          type="number"
                          value={edits[r.symbol] ?? r.shares}
                          onChange={(e) => setEdits((p) => ({ ...p, [r.symbol]: e.target.value }))}
                          className="h-8 w-24 ml-auto text-right font-mono"
                        />
                      </td>
                    </tr>
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

function RecList({ list, market, mood }) {
  if (list.length === 0) return <div className="text-sm text-muted-foreground p-4">暂无此类建议</div>;
  return (
    <div className="divide-y divide-border">
      {list.map((r) => (
        <div key={r.symbol} className="flex items-center gap-3 px-3 py-2.5 hover:bg-muted/40" data-testid="portfolio-rec-row">
          <span className="font-mono text-xs text-muted-foreground w-16">{r.symbol}</span>
          <span className="text-sm flex-1 truncate">{r.name}</span>
          <span className="text-[10px] text-muted-foreground w-24 truncate">{r.sector}</span>
          <span className={`text-xs ${mood === "add" ? "text-emerald-300" : "text-amber-300"}`}>{r.reason}</span>
        </div>
      ))}
    </div>
  );
}
