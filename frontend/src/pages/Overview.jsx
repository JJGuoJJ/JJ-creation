import React, { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Skeleton } from "../components/ui/skeleton";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import MarketPhaseCard from "../components/MarketPhaseCard";
import FearGreedGauge from "../components/FearGreedGauge";
import AllocationDonut from "../components/AllocationDonut";
import SectorHeatList from "../components/SectorHeatList";
import ActionBadge from "../components/ActionBadge";
import api from "../lib/api";
import { Activity, AlertTriangle, Flame, FileText, ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function Overview({ market, refreshTick }) {
  const [overview, setOverview] = useState(null);
  const [sectors, setSectors] = useState([]);
  const [recs, setRecs] = useState([]);
  const [diag, setDiag] = useState(null);
  const [loading, setLoading] = useState(true);
  const [empty, setEmpty] = useState(false);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    Promise.all([
      api.marketOverview(),
      api.sectors().catch(() => ({ sectors: [] })),
      api.recommendationsToday(8).catch(() => ({ recommendations: [] })),
      api.portfolioDiagnose().catch(() => null),
    ])
      .then(([ov, sec, rec, di]) => {
        if (!alive) return;
        if (ov.empty) {
          setEmpty(true);
        } else {
          setOverview(ov);
          setEmpty(false);
        }
        setSectors(sec.sectors || []);
        setRecs(rec.recommendations || []);
        setDiag(di);
      })
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [refreshTick]);

  if (loading) {
    return <SkeletonOverview />;
  }
  if (empty) {
    return <EmptyState />;
  }
  if (!overview) return null;

  const fp = overview.full_payload || {};
  const allocBands = fp.allocation || overview.allocation;
  const cur = diag?.current_buckets;
  const missingSrc = fp.missing_sources || [];

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">总览 · Overview</h1>
          <p className="text-sm text-muted-foreground mt-1">
            一屏看完：市场阶段 → 情绪 → 仓位 → 动作 → 风险信号
          </p>
        </div>
        <Badge variant="outline" className="font-mono text-[11px]">数据日期 · {overview.date}</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-4">
          <MarketPhaseCard
            regime={overview.regime}
            regimeCN={overview.regime_cn}
            score={overview.combined_score}
            action={overview.action_summary}
            missingSources={missingSrc}
          />
        </div>
        <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <FearGreedGauge
            title="Global Fear & Greed"
            subtitle="全球恐惧贪婪指数"
            score={overview.global_fng}
            testId="global-fng-gauge"
          />
          <FearGreedGauge
            title="China Tech F&G"
            subtitle="中国科技恐惧贪婪指数"
            score={overview.china_tech_fng}
            testId="china-fng-gauge"
          />
          <FearGreedGauge
            title="Crypto F&G"
            subtitle="加密恐惧贪婪指数"
            score={overview.crypto_fng}
            testId="crypto-fng-gauge"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-7">
          <AllocationDonut allocation={allocBands} current={cur} />
        </div>
        <div className="lg:col-span-5">
          <Card>
            <CardContent className="p-4 md:p-5">
              <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5">
                <Flame className="h-3.5 w-3.5 inline mr-1" /> 今日 Top 推荐 · Top Picks
              </div>
              <div className="text-sm text-foreground mb-3">
                按综合分排序，点击查看全量
              </div>
              <div className="space-y-1">
                {recs.slice(0, 8).map((r) => (
                  <Link
                    key={r.symbol}
                    to="/watchlist"
                    className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-muted/40 transition-colors"
                    data-testid="top-pick-row"
                  >
                    <span className="font-mono text-[11px] text-muted-foreground w-12">{r.symbol}</span>
                    <span className="text-sm flex-1 truncate">{r.name}</span>
                    <span className="text-[10px] text-muted-foreground w-16 truncate">{r.sector}</span>
                    <span className="font-mono tabular-nums text-sm w-10 text-right">{r.score?.toFixed?.(1) ?? r.score}</span>
                    <ActionBadge action={r.action_cn} />
                  </Link>
                ))}
                {recs.length === 0 && (
                  <div className="text-xs text-muted-foreground">暂无推荐</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-8">
          <SectorHeatList sectors={sectors} market={market} />
        </div>
        <div className="lg:col-span-4">
          <RiskSignals overview={overview} sectors={sectors} />
        </div>
      </div>

      <Card>
        <CardContent className="p-4 md:p-5">
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs uppercase tracking-wider text-muted-foreground">策略师解读 · Strategist Note</div>
            <Link to="/reports" className="text-xs text-primary inline-flex items-center gap-1 hover:underline">
              <FileText className="h-3.5 w-3.5" /> 查看完整报告 <ChevronRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="text-sm leading-relaxed text-foreground/90 whitespace-pre-line">
            {fp.llm_interpretation || "本人策略台：按规则引擎生成。刷新一次获取完整解读。"}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function RiskSignals({ overview, sectors }) {
  const flags = [];
  if (overview.global_fng > 85) flags.push({ level: "high", text: `全球情绪接近极度贪婪 (${overview.global_fng})` });
  if (overview.china_tech_fng > 85) flags.push({ level: "high", text: `A股科技情绪接近极度贪婪 (${overview.china_tech_fng})` });
  if (overview.global_fng < 25) flags.push({ level: "opp", text: `全球情绪极度恐慌 (${overview.global_fng})，可分批低吸` });
  if (overview.china_tech_fng < 25) flags.push({ level: "opp", text: `A股科技情绪极度恐慌 (${overview.china_tech_fng})` });
  for (const s of sectors) {
    if (s.risk != null && s.risk >= 25) flags.push({ level: "high", text: `${s.sector} 赛道过热 (风险罚分 ${s.risk})，不建议追涨` });
    else if (s.heat_score != null && s.heat_score > 75) flags.push({ level: "med", text: `${s.sector} 赛道热度偏高 (${s.heat_score})` });
  }
  if (flags.length === 0) flags.push({ level: "info", text: "暂无重大风险信号" });
  return (
    <Card>
      <CardContent className="p-4 md:p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs uppercase tracking-wider text-muted-foreground">
            <AlertTriangle className="h-3.5 w-3.5 inline mr-1" /> 风险信号 · Risk Signals
          </div>
        </div>
        <ul className="space-y-2" data-testid="risk-signals">
          {flags.map((f, i) => {
            const c = f.level === "high" ? "text-red-300 bg-red-500/10" :
                      f.level === "med"  ? "text-amber-300 bg-amber-500/10" :
                      f.level === "opp"  ? "text-emerald-300 bg-emerald-500/10" :
                                            "text-slate-300 bg-slate-500/10";
            return (
              <li key={i} className={`text-xs leading-relaxed px-3 py-2 rounded-md border border-border ${c}`}>
                {f.text}
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}

function SkeletonOverview() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Skeleton className="lg:col-span-4 h-44" />
        <Skeleton className="lg:col-span-8 h-44" />
      </div>
      <Skeleton className="h-64" />
      <Skeleton className="h-64" />
    </div>
  );
}

function EmptyState() {
  const [refreshing, setRefreshing] = useState(false);
  const refresh = async () => {
    setRefreshing(true);
    try {
      await api.refreshData(true);
      window.location.reload();
    } catch (e) {
      setRefreshing(false);
    }
  };
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <Activity className="h-10 w-10 text-muted-foreground mb-3" />
      <h2 className="text-xl font-semibold mb-2">还没有数据</h2>
      <p className="text-sm text-muted-foreground max-w-md mb-4">
        点击下方按钮从 akshare/yfinance/Alternative.me 获取今日数据，计算 Fear & Greed、赛道热度、仓位建议与中文日报。刷新耗时约 60-90 秒。
      </p>
      <Button onClick={refresh} disabled={refreshing} data-testid="empty-refresh-button">
        {refreshing ? "刷新中…" : "立即初次刷新"}
      </Button>
    </div>
  );
}
