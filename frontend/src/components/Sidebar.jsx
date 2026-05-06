import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard, Briefcase, Layers, ListChecks,
  Activity, FileText, Settings, ChevronLeft, Sparkles
} from "lucide-react";
import { cn } from "../lib/utils";

const NAV = [
  { to: "/", label: "总览", icon: LayoutDashboard, en: "Overview" },
  { to: "/portfolio", label: "持仓", icon: Briefcase, en: "Portfolio" },
  { to: "/sectors", label: "赛道", icon: Layers, en: "Sectors" },
  { to: "/watchlist", label: "观察池", icon: ListChecks, en: "Watchlist" },
  { to: "/sentiment", label: "情绪", icon: Activity, en: "Sentiment" },
  { to: "/reports", label: "报告", icon: FileText, en: "Reports" },
  { to: "/settings", label: "设置", icon: Settings, en: "Settings" },
];

export default function Sidebar({ collapsed, setCollapsed }) {
  const location = useLocation();
  return (
    <aside
      data-testid="app-sidebar"
      className={cn(
        "hidden md:flex flex-col border-r border-border bg-card/40 backdrop-blur-sm sticky top-0 h-screen transition-all duration-200",
        collapsed ? "w-[72px]" : "w-[240px]"
      )}
    >
      <div className="flex items-center justify-between h-14 px-4 border-b border-border">
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-cyan-500 to-sky-600 flex items-center justify-center">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          {!collapsed && (
            <div className="leading-tight">
              <div className="font-semibold text-sm">PIB</div>
              <div className="text-[10px] text-muted-foreground">Personal Investment Bank</div>
            </div>
          )}
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          data-testid="sidebar-collapse-toggle"
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform", collapsed && "rotate-180")} />
        </button>
      </div>
      <nav className="flex-1 py-3 px-2 space-y-1">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              data-testid={`nav-${item.en.toLowerCase()}`}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 h-10 text-sm transition-colors relative",
                active
                  ? "bg-primary/10 text-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[2px] bg-primary rounded-r" />}
              <Icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
              {!collapsed && active && (
                <span className="ml-auto text-[10px] text-muted-foreground font-mono">{item.en}</span>
              )}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-border">
        {!collapsed && (
          <div className="text-[10px] text-muted-foreground leading-tight">
            <div>FastAPI · SQLite · React</div>
            <div className="font-mono">v1.0 MVP</div>
          </div>
        )}
      </div>
    </aside>
  );
}
