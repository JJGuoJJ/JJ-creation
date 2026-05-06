import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Overview from "./pages/Overview";
import Portfolio from "./pages/Portfolio";
import Sectors from "./pages/Sectors";
import Watchlist from "./pages/Watchlist";
import Sentiment from "./pages/Sentiment";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import "./App.css";
import api from "./lib/api";

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [dark, setDark] = useState(true);
  const [market, setMarket] = useState("CN");
  const [lastUpdate, setLastUpdate] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  useEffect(() => {
    api.health().then((h) => {
      if (h.last_data_date) setLastUpdate(`最近数据日期 · ${h.last_data_date}`);
      else setLastUpdate("尚未初次刷新");
    }).catch(() => setLastUpdate("后端连接失败"));
  }, [refreshTick]);

  const onRefreshDone = () => setRefreshTick((t) => t + 1);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background text-foreground app-bg">
        <div className="flex">
          <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
          <div className="flex-1 min-w-0">
            <Header
              market={market}
              setMarket={setMarket}
              dark={dark}
              setDark={setDark}
              lastUpdate={lastUpdate}
              onRefreshDone={onRefreshDone}
            />
            <main className="px-4 lg:px-6 py-5 lg:py-6 max-w-[1600px] mx-auto">
              <Routes>
                <Route path="/" element={<Overview market={market} refreshTick={refreshTick} />} />
                <Route path="/portfolio" element={<Portfolio market={market} refreshTick={refreshTick} />} />
                <Route path="/sectors" element={<Sectors market={market} refreshTick={refreshTick} />} />
                <Route path="/watchlist" element={<Watchlist market={market} refreshTick={refreshTick} />} />
                <Route path="/sentiment" element={<Sentiment refreshTick={refreshTick} />} />
                <Route path="/reports" element={<Reports refreshTick={refreshTick} />} />
                <Route path="/settings" element={<Settings refreshTick={refreshTick} onRefreshDone={onRefreshDone} />} />
              </Routes>
            </main>
          </div>
        </div>
        <Toaster position="top-right" richColors closeButton />
      </div>
    </BrowserRouter>
  );
}
