const STORAGE_KEY = "jj-capital-flow-records";
const THRESHOLD_KEY = "jj-capital-flow-threshold";

export const demoRecords = [
  { code: "300750", name: "宁德时代", sector: "新能源", netInflow: 12.8, turnover: 91.4, close: 214.6, changePct: 3.42, streak: 3 },
  { code: "601318", name: "中国平安", sector: "非银金融", netInflow: 7.3, turnover: 58.2, close: 48.9, changePct: 1.84, streak: 2 },
  { code: "600519", name: "贵州茅台", sector: "食品饮料", netInflow: 5.9, turnover: 76.5, close: 1698.1, changePct: 0.92, streak: 1 },
  { code: "002475", name: "立讯精密", sector: "消费电子", netInflow: 4.6, turnover: 43.8, close: 33.7, changePct: 2.15, streak: 4 },
  { code: "688981", name: "中芯国际", sector: "半导体", netInflow: 3.2, turnover: 69.7, close: 52.4, changePct: 0.61, streak: 1 },
  { code: "000977", name: "浪潮信息", sector: "人工智能", netInflow: 2.7, turnover: 64.1, close: 41.6, changePct: 4.38, streak: 2 },
  { code: "000858", name: "五粮液", sector: "食品饮料", netInflow: -1.6, turnover: 39.9, close: 143.2, changePct: -0.74, streak: -1 },
  { code: "600036", name: "招商银行", sector: "银行", netInflow: -3.4, turnover: 51.6, close: 35.8, changePct: -1.23, streak: -2 },
  { code: "601012", name: "隆基绿能", sector: "新能源", netInflow: -4.8, turnover: 47.7, close: 18.3, changePct: -2.91, streak: -3 }
];

export function formatMoney(value) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)} 亿`;
}

export function getStrength(record) {
  if (!record.turnover) {
    return 0;
  }
  return record.netInflow / record.turnover;
}

export function getSignal(record, threshold = 5) {
  const strength = getStrength(record);
  if (record.netInflow >= threshold && strength >= 0.08) {
    return "强势流入";
  }
  if (record.netInflow > 0) {
    return "温和流入";
  }
  if (record.netInflow > -threshold) {
    return "资金分歧";
  }
  return "明显流出";
}

export function calculateSummary(records, threshold = 5) {
  const totalNet = records.reduce((sum, record) => sum + record.netInflow, 0);
  const inflowCount = records.filter((record) => record.netInflow > 0).length;
  const strongCount = records.filter((record) => record.netInflow >= threshold).length;
  const averageStrength = records.length
    ? records.reduce((sum, record) => sum + getStrength(record), 0) / records.length
    : 0;

  return { totalNet, inflowCount, strongCount, averageStrength };
}

export function filterRecords(records, { sector = "全部", signal = "全部", threshold = 5 } = {}) {
  return records.filter((record) => {
    const sectorMatched = sector === "全部" || record.sector === sector;
    const signalMatched = signal === "全部" || getSignal(record, threshold) === signal;
    return sectorMatched && signalMatched;
  });
}

export function groupBySector(records) {
  const grouped = records.reduce((result, record) => {
    result[record.sector] = (result[record.sector] ?? 0) + record.netInflow;
    return result;
  }, {});

  return Object.entries(grouped)
    .map(([sector, netInflow]) => ({ sector, netInflow }))
    .sort((a, b) => b.netInflow - a.netInflow);
}

export function sortByNetInflow(records) {
  return [...records].sort((a, b) => b.netInflow - a.netInflow);
}

export function parseCsv(text) {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  if (!headerLine) {
    return [];
  }

  const headers = headerLine.split(",").map((header) => header.trim());
  return lines
    .filter(Boolean)
    .map((line) => {
      const values = line.split(",").map((value) => value.trim());
      const row = Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
      return {
        code: row.code,
        name: row.name,
        sector: row.sector,
        netInflow: Number(row.netInflow),
        turnover: Number(row.turnover),
        close: Number(row.close),
        changePct: Number(row.changePct),
        streak: Number(row.streak)
      };
    })
    .filter((record) => record.code && record.name && Number.isFinite(record.netInflow));
}

function readStoredRecords() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || demoRecords;
  } catch {
    return demoRecords;
  }
}

function saveRecords(records) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
}

function renderSectorOptions(records, selectedSector) {
  const sectorFilter = document.querySelector("#sector-filter");
  const sectors = [...new Set(records.map((record) => record.sector))].sort();
  sectorFilter.innerHTML = ["全部", ...sectors]
    .map((sector) => `<option value="${sector}" ${sector === selectedSector ? "selected" : ""}>${sector === "全部" ? "全部行业" : sector}</option>`)
    .join("");
}

function renderSummary(records, threshold) {
  const summary = calculateSummary(records, threshold);
  document.querySelector("#summary-net").textContent = formatMoney(summary.totalNet);
  document.querySelector("#summary-net").className = summary.totalNet >= 0 ? "value-up" : "value-down";
  document.querySelector("#summary-net-note").textContent = summary.totalNet >= 0 ? "市场风险偏好改善" : "资金整体偏谨慎";
  document.querySelector("#summary-inflow-count").textContent = `${summary.inflowCount} 只`;
  document.querySelector("#summary-strong-count").textContent = `${summary.strongCount} 只`;
  document.querySelector("#summary-strength").textContent = `${(summary.averageStrength * 100).toFixed(2)}%`;
}

function renderSectorBars(records) {
  const sectorBars = document.querySelector("#sector-bars");
  const sectors = groupBySector(records);
  const maxAbs = Math.max(...sectors.map((item) => Math.abs(item.netInflow)), 1);
  sectorBars.innerHTML = sectors
    .map((item) => {
      const width = Math.max((Math.abs(item.netInflow) / maxAbs) * 100, 5);
      const negativeClass = item.netInflow < 0 ? " is-negative" : "";
      return `<div class="bar-row">
        <span>${item.sector}</span>
        <div class="bar-track"><div class="bar-fill${negativeClass}" style="width: ${width}%"></div></div>
        <span class="${item.netInflow >= 0 ? "value-up" : "value-down"}">${formatMoney(item.netInflow)}</span>
      </div>`;
    })
    .join("");
}

function renderAlerts(records, threshold) {
  const alerts = records.filter((record) => Math.abs(record.netInflow) >= threshold);
  document.querySelector("#alert-count").textContent = `${alerts.length} 条`;
  document.querySelector("#alert-list").innerHTML = alerts.length
    ? alerts
        .map((record) => `<li>${record.name}（${record.code}）主力净流入 ${formatMoney(record.netInflow)}，连续 ${Math.abs(record.streak)} 天${record.streak >= 0 ? "流入" : "流出"}。</li>`)
        .join("")
    : "<li>暂无触发预警的标的，可降低阈值或导入最新数据。</li>";
}

function renderTable(records, threshold) {
  document.querySelector("#flow-table-body").innerHTML = sortByNetInflow(records)
    .map((record) => {
      const signal = getSignal(record, threshold);
      const strongClass = signal === "强势流入" ? " signal--strong" : "";
      const outClass = signal === "明显流出" ? " signal--out" : "";
      return `<tr>
        <td>${record.code}</td>
        <td><strong>${record.name}</strong></td>
        <td>${record.sector}</td>
        <td class="${record.netInflow >= 0 ? "value-up" : "value-down"}">${formatMoney(record.netInflow)}</td>
        <td>${formatMoney(record.turnover)}</td>
        <td>${(getStrength(record) * 100).toFixed(2)}%</td>
        <td class="${record.changePct >= 0 ? "value-up" : "value-down"}">${record.changePct.toFixed(2)}%</td>
        <td>${Math.abs(record.streak)} 天${record.streak >= 0 ? "流入" : "流出"}</td>
        <td><span class="signal${strongClass}${outClass}">${signal}</span></td>
      </tr>`;
    })
    .join("");
}

function render(records) {
  const sector = document.querySelector("#sector-filter").value;
  const signal = document.querySelector("#signal-filter").value;
  const threshold = Number(document.querySelector("#alert-threshold").value) || 5;
  const filteredRecords = filterRecords(records, { sector, signal, threshold });

  localStorage.setItem(THRESHOLD_KEY, String(threshold));
  renderSectorOptions(records, sector);
  renderSummary(filteredRecords, threshold);
  renderSectorBars(filteredRecords);
  renderAlerts(filteredRecords, threshold);
  renderTable(filteredRecords, threshold);
}

function boot() {
  const root = document.querySelector("[data-testid='capital-flow-page']");
  if (!root) {
    return;
  }

  let records = readStoredRecords();
  const today = new Date().toISOString().slice(0, 10);
  document.querySelector("#trade-date").value = today;
  document.querySelector("#alert-threshold").value = localStorage.getItem(THRESHOLD_KEY) || "5";
  renderSectorOptions(records, "全部");
  render(records);

  ["#sector-filter", "#signal-filter", "#alert-threshold", "#trade-date"].forEach((selector) => {
    document.querySelector(selector).addEventListener("input", () => render(records));
  });

  document.querySelector("#load-sample").addEventListener("click", () => {
    records = demoRecords;
    saveRecords(records);
    document.querySelector("#sector-filter").value = "全部";
    document.querySelector("#signal-filter").value = "全部";
    render(records);
  });

  document.querySelector("#csv-upload").addEventListener("change", async (event) => {
    const [file] = event.target.files;
    if (!file) {
      return;
    }
    const imported = parseCsv(await file.text());
    if (imported.length) {
      records = imported;
      saveRecords(records);
      document.querySelector("#sector-filter").value = "全部";
      document.querySelector("#signal-filter").value = "全部";
      render(records);
    }
  });
}

if (typeof document !== "undefined") {
  boot();
}
