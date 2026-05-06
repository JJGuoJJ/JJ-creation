import React from "react";
import { Card, CardContent } from "./ui/card";
import { cn } from "../lib/utils";

function classifyFNG(score) {
  if (score == null) return { label: "—", color: "text-slate-300" };
  if (score < 25) return { label: "极度恐慌", color: "text-emerald-400" };
  if (score < 40) return { label: "恐慌", color: "text-emerald-300" };
  if (score < 60) return { label: "中性", color: "text-slate-200" };
  if (score < 75) return { label: "贪婪", color: "text-amber-300" };
  if (score < 90) return { label: "极度贪婪", color: "text-orange-400" };
  return { label: "泡沫", color: "text-red-400" };
}

function Gauge({ score }) {
  const v = Math.min(100, Math.max(0, score ?? 50));
  // SVG arc 0..180 deg
  const cx = 60, cy = 60, r = 48;
  const angle = -180 + (v / 100) * 180;
  const rad = (angle * Math.PI) / 180;
  const x = cx + r * Math.cos(rad);
  const y = cy + r * Math.sin(rad);
  const colorAt = (s) => s < 25 ? "#34d399" : s < 40 ? "#10b981" : s < 60 ? "#94a3b8" : s < 75 ? "#f59e0b" : s < 90 ? "#fb923c" : "#ef4444";
  return (
    <svg viewBox="0 0 120 70" className="w-full max-w-[180px]">
      <defs>
        <linearGradient id="fg-grad" x1="0" x2="1">
          <stop offset="0%" stopColor="#34d399" />
          <stop offset="35%" stopColor="#94a3b8" />
          <stop offset="70%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#ef4444" />
        </linearGradient>
      </defs>
      <path d="M 12 60 A 48 48 0 0 1 108 60" stroke="hsl(var(--border))" strokeWidth="10" fill="none" />
      <path d="M 12 60 A 48 48 0 0 1 108 60" stroke="url(#fg-grad)" strokeWidth="10" fill="none" strokeLinecap="round" strokeDasharray={`${(v / 100) * 150} 150`} />
      <circle cx={x} cy={y} r="4" fill={colorAt(v)} stroke="hsl(var(--background))" strokeWidth="2" />
      <text x="60" y="55" textAnchor="middle" fontSize="22" fontWeight="700" fill="currentColor" fontFamily="IBM Plex Mono, monospace">
        {v.toFixed(0)}
      </text>
    </svg>
  );
}

export default function FearGreedGauge({ title, subtitle, score, testId }) {
  const { label, color } = classifyFNG(score);
  return (
    <Card data-testid={testId || "fear-greed-gauge-card"} className="hover:shadow-md transition-shadow">
      <CardContent className="p-4 md:p-5">
        <div className="flex items-center justify-between mb-1.5">
          <div className="text-xs uppercase tracking-wider text-muted-foreground">{title}</div>
          <div className={cn("text-xs font-medium", color)}>{label}</div>
        </div>
        <div className="flex items-center justify-center -my-1">
          <Gauge score={score} />
        </div>
        {subtitle && <div className="text-xs text-muted-foreground text-center mt-1">{subtitle}</div>}
      </CardContent>
    </Card>
  );
}
