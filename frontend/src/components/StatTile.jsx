import React from "react";
import { cn } from "../lib/utils";

export function StatTile({ label, value, suffix, sub, accent, testId, className, icon: Icon }) {
  return (
    <div
      data-testid={testId}
      className={cn(
        "rounded-xl border border-border bg-card p-4 md:p-5 shadow-sm hover:shadow-md transition-shadow",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </div>
      <div className="mt-2 flex items-baseline gap-1.5">
        <div className={cn("font-mono tabular-nums text-3xl md:text-4xl font-semibold", accent)}>
          {value ?? "—"}
        </div>
        {suffix && <div className="text-sm text-muted-foreground">{suffix}</div>}
      </div>
      {sub && <div className="mt-1.5 text-xs text-muted-foreground">{sub}</div>}
    </div>
  );
}
