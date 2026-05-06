import React, { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api, { reportDownloadUrl } from "../lib/api";
import { Download, FileText, ChevronRight } from "lucide-react";

export default function Reports({ refreshTick }) {
  const [list, setList] = useState([]);
  const [selected, setSelected] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    api.reportsList().then((r) => {
      setList(r.reports || []);
      if ((r.reports || []).length > 0) setSelected(r.reports[0].date);
    }).finally(() => setLoading(false));
  }, [refreshTick]);

  useEffect(() => {
    if (!selected) { setReport(null); return; }
    api.report(selected).then(setReport).catch(() => setReport(null));
  }, [selected]);

  const filtered = list.filter((r) => !search || r.date.includes(search) || (r.summary || "").includes(search));

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">报告 · Reports</h1>
          <p className="text-sm text-muted-foreground mt-1">中文每日策略报告，可下载 Markdown</p>
        </div>
        {selected && (
          <Button asChild variant="outline" size="sm" data-testid="reports-download-button">
            <a href={reportDownloadUrl(selected)} target="_blank" rel="noreferrer"><Download className="h-3.5 w-3.5 mr-1" /> 下载 Markdown</a>
          </Button>
        )}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Card className="lg:col-span-3">
          <CardContent className="p-3">
            <Input data-testid="reports-search" placeholder="搜索报告" value={search} onChange={(e) => setSearch(e.target.value)} className="h-8 mb-2" />
            <div data-testid="reports-list" className="max-h-[600px] overflow-auto space-y-1">
              {loading && <div className="text-xs text-muted-foreground">加载中…</div>}
              {!loading && filtered.length === 0 && (
                <div className="text-xs text-muted-foreground p-3">暂无报告。请先点右上角【刷新数据】。</div>
              )}
              {filtered.map((r) => {
                const sel = selected === r.date;
                return (
                  <button
                    key={r.date}
                    onClick={() => setSelected(r.date)}
                    data-testid="reports-item"
                    className={`w-full text-left rounded-md px-3 py-2 transition-colors ${sel ? "bg-primary/10 border border-primary/30" : "hover:bg-muted/40 border border-transparent"}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs">{r.date}</span>
                      {sel && <ChevronRight className="h-3 w-3 text-primary" />}
                    </div>
                    <div className="text-[11px] text-muted-foreground mt-1 line-clamp-1">{r.summary || r.title}</div>
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>
        <Card className="lg:col-span-9">
          <CardContent className="p-4 md:p-6">
            {!report ? (
              <div className="text-sm text-muted-foreground py-12 text-center">
                <FileText className="h-8 w-8 mx-auto mb-3 text-muted-foreground/60" />
                <div>选择左侧报告查看</div>
              </div>
            ) : (
              <div className="markdown-body" data-testid="reports-markdown-viewer">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{report.markdown}</ReactMarkdown>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
