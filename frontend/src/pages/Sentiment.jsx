import React, { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar } from "recharts";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import api from "../lib/api";
import { Activity } from "lucide-react";

export default function Sentiment({ refreshTick }) {
  const [hist, setHist] = useState([]);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([api.fearGreedHistory(60), api.marketOverview().catch(() => null)])
      .then(([h, ov]) => {
        setHist(h.history || []);
        if (ov && !ov.empty) setOverview(ov);
      }).finally(() => setLoading(false));
  }, [refreshTick]);

  const fp = overview?.full_payload || {};
  const gb = fp?.global_fng?.breakdown || {};
  const cb = fp?.china_tech_fng?.breakdown || {};
  const buildBreakdown = (b) =>
    Object.entries(b)
      .filter(([_, v]) => v.score != null)
      .map(([k, v]) => ({ name: v.label || k, score: Math.round(v.score), weight: v.weight }));
  const gbData = buildBreakdown(gb);
  const cbData = buildBreakdown(cb);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">情绪 · Fear &amp; Greed</h1>
        <p className="text-sm text-muted-foreground mt-1">全球 / 中国科技 / Crypto 三条情绪曲线 + 因子贡献</p>
      </div>

      <Card>
        <CardContent className="p-4 md:p-5">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">历史 60 天 · Historical Curves</div>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hist} margin={{ top: 10, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="hsl(var(--border))" strokeDasharray="3 3" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", fontSize: 12, borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="global_fng" stroke="#0EA5E9" strokeWidth={2} dot={false} name="\u5168\u7403 F&G" />
                <Line type="monotone" dataKey="china_tech_fng" stroke="#F59E0B" strokeWidth={2} dot={false} name="\u4e2d\u56fd\u79d1\u6280 F&G" />
                <Line type="monotone" dataKey="crypto_fng" stroke="#A855F7" strokeWidth={2} dot={false} name="Crypto F&G" />
                <Line type="monotone" dataKey="ai_chain_score" stroke="#22C55E" strokeWidth={2} dot={false} name="AI \u4ea7\u4e1a\u94fe\u70ed\u5ea6" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {hist.length === 0 && !loading && (
            <div className="py-8 text-center text-sm text-muted-foreground">历史数据不足。多次刷新数据后会逐渐累积。</div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="global">
        <TabsList>
          <TabsTrigger value="global" data-testid="tab-global-breakdown">全球 因子贡献</TabsTrigger>
          <TabsTrigger value="china" data-testid="tab-china-breakdown">中国科技 因子贡献</TabsTrigger>
        </TabsList>
        <TabsContent value="global">
          <Card><CardContent className="p-4 md:p-5"><BreakdownChart data={gbData} /></CardContent></Card>
        </TabsContent>
        <TabsContent value="china">
          <Card><CardContent className="p-4 md:p-5"><BreakdownChart data={cbData} /></CardContent></Card>
        </TabsContent>
      </Tabs>

      {fp?.global_fng?.missing?.length > 0 && (
        <div className="text-xs text-amber-300">
          ⚠ 全球指数缺失因子: {fp.global_fng.missing.join(", ")}
        </div>
      )}
      {fp?.china_tech_fng?.missing?.length > 0 && (
        <div className="text-xs text-amber-300">
          ⚠ 中国科技指数缺失因子: {fp.china_tech_fng.missing.join(", ")}
        </div>
      )}
    </div>
  );
}

function BreakdownChart({ data }) {
  if (data.length === 0) return <div className="text-sm text-muted-foreground py-6">请先点右上角【刷新数据】。</div>;
  return (
    <div className="h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 16, top: 10, bottom: 10 }}>
          <CartesianGrid stroke="hsl(var(--border))" strokeDasharray="3 3" />
          <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={11} domain={[0, 100]} />
          <YAxis type="category" dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} width={180} />
          <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", fontSize: 12 }} />
          <Bar dataKey="score" fill="#14B8A6" name="\u56e0\u5b50\u5f97\u5206" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
