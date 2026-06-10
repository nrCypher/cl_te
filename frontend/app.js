// Minimal vanilla-JS client for the workshop scheduler API.
// No build step: served statically by FastAPI and talks to /api/* endpoints.

const API = "/api";
const state = { scenario: null, priorityByWorkOrder: {} };

const $ = (id) => document.getElementById(id);
const setStatus = (msg) => ($("status").textContent = msg);

async function postJSON(path, body) {
  const res = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

async function getJSON(path) {
  const res = await fetch(API + path);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

async function simulate() {
  setStatus("Simulating…");
  $("btn-solve").disabled = true;
  const seed = parseInt($("seed").value, 10) || 0;
  const size = $("size").value;
  const scenario = await postJSON("/simulate", { seed, size });
  state.scenario = scenario;
  state.priorityByWorkOrder = {};
  scenario.work_orders.forEach((wo) => {
    state.priorityByWorkOrder[wo.id] = wo.priority;
  });
  setStatus(
    `Scenario ${scenario.id}: ${scenario.machines.length} machines, ` +
      `${scenario.work_orders.length} work orders.`
  );
  $("btn-solve").disabled = false;
  $("gantt").innerHTML = "";
  $("kpis").innerHTML = "";
  $("alerts").innerHTML = "";
}

async function solve() {
  if (!state.scenario) return;
  setStatus("Solving…");
  const result = await postJSON("/solve", { scenario_id: state.scenario.id });
  setStatus(`Solver: ${result.status} (${result.wall_time_s.toFixed(2)}s).`);
  const schedule = await getJSON(`/schedule?scenario_id=${state.scenario.id}`);
  renderGantt(schedule);
  const kpis = await getJSON(`/kpis?scenario_id=${state.scenario.id}`);
  renderKpis(kpis);
  const alerts = await getJSON(`/alerts?scenario_id=${state.scenario.id}`);
  renderAlerts(alerts.alerts);
}

function renderGantt(schedule) {
  const gantt = $("gantt");
  gantt.innerHTML = "";
  const horizon = Math.max(schedule.makespan_min, 1);
  schedule.rows.forEach((row) => {
    const rowEl = document.createElement("div");
    rowEl.className = "gantt-row";
    const label = document.createElement("div");
    label.className = "gantt-label";
    label.textContent = row.machine_name;
    const track = document.createElement("div");
    track.className = "gantt-track";
    row.operations.forEach((op) => {
      const bar = document.createElement("div");
      const prio = state.priorityByWorkOrder[op.work_order_id] || "medium";
      bar.className = `bar ${prio}`;
      bar.style.left = `${(100 * op.start_min) / horizon}%`;
      bar.style.width = `${Math.max(1, (100 * (op.end_min - op.start_min)) / horizon)}%`;
      bar.title = `${op.work_order_code} · ${op.op_type} · ${op.start_min}-${op.end_min} min`;
      bar.textContent = op.work_order_code;
      track.appendChild(bar);
    });
    rowEl.appendChild(label);
    rowEl.appendChild(track);
    gantt.appendChild(rowEl);
  });
}

function kpiCard(label, value) {
  return `<div class="kpi-card"><div class="label">${label}</div><div class="value">${value}</div></div>`;
}

function renderKpis(k) {
  $("kpis").innerHTML = [
    kpiCard("Scheduled", `${k.scheduled_orders}/${k.total_orders}`),
    kpiCard("On-time", `${(k.on_time_rate * 100).toFixed(0)}%`),
    kpiCard("Avg lateness", `${k.avg_lateness_min.toFixed(0)}m`),
    kpiCard("Makespan", `${k.makespan_min}m`),
    kpiCard("Utilisation", `${k.overall_utilisation_pct.toFixed(0)}%`),
    kpiCard("Backlog", k.backlog_size),
    kpiCard("Tonnage today", `${k.tonnage_scheduled_today_kg.toFixed(0)}kg`),
    kpiCard("Alerts", k.num_alerts),
  ].join("");
}

function renderAlerts(alerts) {
  const ul = $("alerts");
  ul.innerHTML = "";
  if (!alerts.length) {
    ul.innerHTML = "<li class='info'>No alerts 🎉</li>";
    return;
  }
  alerts.forEach((a) => {
    const li = document.createElement("li");
    li.className = a.severity;
    li.textContent = `[${a.type}] ${a.message}`;
    ul.appendChild(li);
  });
}

$("btn-simulate").addEventListener("click", () => simulate().catch((e) => setStatus(e.message)));
$("btn-solve").addEventListener("click", () => solve().catch((e) => setStatus(e.message)));
