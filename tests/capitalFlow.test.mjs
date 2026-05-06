import assert from "node:assert/strict";
import test from "node:test";
import {
  calculateSummary,
  filterRecords,
  formatMoney,
  getSignal,
  groupBySector,
  parseCsv,
  sortByNetInflow
} from "../src/app.js";

const records = [
  { code: "AAA", name: "A 公司", sector: "科技", netInflow: 8, turnover: 80, close: 10, changePct: 2, streak: 2 },
  { code: "BBB", name: "B 公司", sector: "消费", netInflow: 1, turnover: 50, close: 20, changePct: 1, streak: 1 },
  { code: "CCC", name: "C 公司", sector: "科技", netInflow: -6, turnover: 60, close: 30, changePct: -3, streak: -2 }
];

test("formatMoney marks positive values and keeps two decimals", () => {
  assert.equal(formatMoney(3.456), "+3.46 亿");
  assert.equal(formatMoney(-1.2), "-1.20 亿");
});

test("getSignal classifies daily smart-money movement", () => {
  assert.equal(getSignal(records[0], 5), "强势流入");
  assert.equal(getSignal(records[1], 5), "温和流入");
  assert.equal(getSignal(records[2], 5), "明显流出");
});

test("calculateSummary aggregates filtered metrics", () => {
  const summary = calculateSummary(records, 5);
  assert.equal(summary.totalNet, 3);
  assert.equal(summary.inflowCount, 2);
  assert.equal(summary.strongCount, 1);
  assert.equal(Number(summary.averageStrength.toFixed(4)), 0.0067);
});

test("filterRecords supports sector and signal filters", () => {
  assert.deepEqual(filterRecords(records, { sector: "科技", signal: "全部", threshold: 5 }).map((record) => record.code), ["AAA", "CCC"]);
  assert.deepEqual(filterRecords(records, { sector: "全部", signal: "温和流入", threshold: 5 }).map((record) => record.code), ["BBB"]);
});

test("groupBySector and sorting rank by net inflow", () => {
  assert.deepEqual(groupBySector(records), [
    { sector: "消费", netInflow: 1 },
    { sector: "科技", netInflow: 2 }
  ].sort((a, b) => b.netInflow - a.netInflow));
  assert.deepEqual(sortByNetInflow(records).map((record) => record.code), ["AAA", "BBB", "CCC"]);
});

test("parseCsv imports monitoring records", () => {
  const csv = "code,name,sector,netInflow,turnover,close,changePct,streak\n000001,平安银行,银行,2.5,30,11.2,0.8,1";
  assert.deepEqual(parseCsv(csv), [
    { code: "000001", name: "平安银行", sector: "银行", netInflow: 2.5, turnover: 30, close: 11.2, changePct: 0.8, streak: 1 }
  ]);
});
