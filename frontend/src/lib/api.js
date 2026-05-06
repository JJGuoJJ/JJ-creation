import axios from "axios";

const BASE = (process.env.REACT_APP_BACKEND_URL || "") + "/api";

const client = axios.create({
  baseURL: BASE,
  timeout: 300000,
});

export const api = {
  health: () => client.get("/health").then((r) => r.data),
  refreshData: (useLLM = true) => client.post(`/refresh-data?use_llm=${useLLM}`).then((r) => r.data),
  marketOverview: () => client.get("/market/overview").then((r) => r.data),
  fearGreedHistory: (days = 60) => client.get(`/indicators/fear-greed?days=${days}`).then((r) => r.data),
  sectors: () => client.get("/sectors").then((r) => r.data),
  watchlist: (params = {}) => client.get("/watchlist", { params }).then((r) => r.data),
  recommendationsToday: (limit = 20) => client.get(`/recommendations/today?limit=${limit}`).then((r) => r.data),
  portfolio: () => client.get("/portfolio").then((r) => r.data),
  portfolioDiagnose: () => client.get("/portfolio/diagnose").then((r) => r.data),
  portfolioUpdate: (items) => client.post("/portfolio/update", items).then((r) => r.data),
  reportsList: () => client.get("/reports/list").then((r) => r.data),
  report: (date) => client.get(`/reports/${date}`).then((r) => r.data),
  thresholds: () => client.get("/settings/thresholds").then((r) => r.data),
  updateThresholds: (payload) => client.post("/settings/thresholds", payload).then((r) => r.data),
  riskProfile: () => client.get("/settings/risk-profile").then((r) => r.data),
  setRiskProfile: (profile) => client.post("/settings/risk-profile", { risk_profile: profile }).then((r) => r.data),
  watchlistConfig: () => client.get("/settings/watchlist").then((r) => r.data),
  backtest: (symbol, days) => client.post(`/backtest/run?symbol=${encodeURIComponent(symbol)}&days=${days}`).then((r) => r.data),
};

export function reportDownloadUrl(date) {
  return `${BASE}/reports/${date}/download`;
}

export default api;
