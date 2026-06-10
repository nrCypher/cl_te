# Sheet-Metal Workshop Production Scheduler

A modular **production-scheduling prototype** for a sheet-metal workshop. With no
real dataset yet, the system first **simulates** realistic synthetic production
data, then **schedules** operations with **Google OR-Tools CP-SAT**, and
**exposes** everything through a **FastAPI** REST API plus a minimal Gantt UI.

The architecture keeps the simulator, domain models, solver, KPI, persistence,
and API layers cleanly separated so the fake simulator can later be swapped for
SAP / MES / shop-floor feeds without touching the solver or API code.

---

## Summary

| Capability | Where |
|---|---|
| Synthetic data generation (seeded, reproducible, 3 size presets) | `app/simulator/` |
| Domain models (Pydantic v2) | `app/models/` |
| OR-Tools CP-SAT scheduler | `app/solver/` |
| KPIs & alerts | `app/kpi/` |
| SQLite persistence behind an abstraction | `app/repository/` |
| Orchestration (all business logic) | `app/services/` |
| REST API (thin routers) | `app/api/` |
| Gantt demo UI | `frontend/` |
| Tests (simulator, solver, KPI, API) | `tests/` |

---

## Architecture

```
api  ──►  services  ──►  { simulator, solver, kpi }  ──►  models
                    └──►  repository (SQLite, behind ABC)  ──►  models
```

* **Dependencies flow one way** toward `models/`. The solver, KPI, and API
  layers depend only on domain models, never on the simulator — that is what
  makes the ERP/MES swap a single-file change in `services/scenario_service.py`.
* **No business logic in routes.** Routers validate input, call a service, and
  return a model. Gantt grouping is an explicit presenter (`app/api/presenters.py`).
* **Persistence is abstract.** `repository/base.py` defines ABCs; the default
  implementation stores Pydantic JSON blobs in SQLite. Replace it with Postgres
  or an ERP gateway without changing services.

### Folder structure

```
app/
  config.py                # env-overridable settings (pydantic-settings)
  main.py                  # FastAPI factory, router + StaticFiles mount
  models/                  # enums, domain, scenario, scheduling, kpi
  simulator/               # config (size presets) + seeded generator
  solver/                  # CP-SAT model builder + solve
  kpi/                     # KPI + alert computation (pure functions)
  repository/              # ABCs + SQLite implementation
  services/                # scenario / scheduling / analytics orchestration
  api/                     # routers, schemas (DTOs), presenters, deps
frontend/                  # index.html + app.js + styles.css (no build step)
tests/                     # simulator, solver, kpi, api
Dockerfile, docker-compose.yml, requirements.txt
```

---

## Domain model

All times are **integer minutes from `scenario.horizon_start`** internally
(CP-SAT-friendly) and converted to ISO datetimes at the API boundary
(frontend-friendly).

* **Machine** — `type` (laser, stamping, bending, welding, additive, finishing,
  treatment, assembly), `capacity`, `speed_factor`, `cost_per_hour`.
* **Material / Product / Routing / OperationTemplate** — master data. A routing
  is an ordered list of operation templates (quantity-independent).
* **WorkOrder** — product, quantity, `release_date`, `due_date`, `priority`.
* **Operation** — the *concrete* schedulable instance, expanded per work order
  from the routing. `duration_min = setup + processing × qty`, with a resolved
  `eligible_machine_ids` list and a linear `predecessor_id` chain.
* **Shift / MaintenanceWindow / Breakdown / Operator** — calendar & disruptions.
* **ScheduledOperation / Schedule** — solver output, Gantt-ready.
* **SolverConfig / SolverResult** — solver knobs and outcome.
* **KPI / Alert** — dashboard metrics and conditions.

---

## Synthetic simulator

`SyntheticDataGenerator(seed, config, size)` draws every value from a single
`random.Random(seed)`, so `(seed, size)` is **fully reproducible** (contractually
tested). It builds materials → machines (≥1 per machine type) → routings (realistic
sheet-metal flow: cut → stamp/bend → weld → treat/finish → assemble) → products →
work orders (priority-skewed, a configurable fraction with deliberately tight due
dates) → shifts → maintenance windows → breakdowns. Scenarios are **feasible by
construction**: every operation type that appears has at least one eligible machine.

Size presets live in `app/simulator/config.py`:

| Size | Machines | Work orders | Horizon |
|---|---|---|---|
| small | 8 | 6–8 | 4 days |
| medium | 8–16 | 18–28 | 7 days |
| large | 16–32 | 70–120 | 10 days |

---

## OR-Tools solver

A CP-SAT model (`app/solver/cp_sat_solver.py`):

* **Alternative machines** — one *optional interval per eligible machine* with a
  presence literal; `AddExactlyOne` picks one. Chosen duration is the nominal
  time rescaled by the machine's `speed_factor`.
* **Precedence** — `start(op) ≥ end(predecessor)` per work-order chain; first op
  also respects the work order's release date.
* **Machine capacity** — `AddNoOverlap` per machine.
* **Maintenance / breakdowns** — fixed blocked intervals added to the machine's
  `NoOverlap` (toggled by `SolverConfig.enable_maintenance / enable_breakdowns`).
* **Objective** — weighted sum of **makespan + total tardiness +
  priority-weighted tardiness + peak machine load** (utilisation balance).

The solver never raises: OR-Tools status is mapped to a `SolverStatus` enum and
an empty-but-valid schedule is returned when no assignment exists.

---

## API

All endpoints are under the `/api` prefix; the Gantt UI is at `/`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/simulate` | Generate + persist a scenario, return full payload |
| POST | `/api/scenarios` | Create a scenario, return a summary |
| GET | `/api/scenarios` | List scenario summaries |
| GET | `/api/scenarios/{id}` | Full scenario |
| GET | `/api/machines?scenario_id=` | Machines |
| GET | `/api/work-orders?scenario_id=` | Work orders + expanded operations |
| POST | `/api/solve` | Run the solver, persist the schedule |
| GET | `/api/schedule?scenario_id=` (or `?schedule_id=`) | Gantt-ready schedule |
| GET | `/api/kpis?scenario_id=` | KPIs |
| GET | `/api/alerts?scenario_id=` | Alerts |
| GET | `/health` | Health check |

Interactive docs: `http://localhost:8000/docs`.

---

## Run locally

### With Python

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://localhost:8000  (Gantt UI)  and  /docs  (OpenAPI)
```

Quick API walk-through:

```bash
# 1. Simulate a small, reproducible scenario
SID=$(curl -s -XPOST localhost:8000/api/simulate \
      -H 'content-type: application/json' \
      -d '{"seed":42,"size":"small"}' | python -c 'import sys,json;print(json.load(sys.stdin)["id"])')

# 2. Solve it
curl -s -XPOST localhost:8000/api/solve \
     -H 'content-type: application/json' -d "{\"scenario_id\":\"$SID\"}"

# 3. Fetch schedule / KPIs / alerts
curl -s "localhost:8000/api/schedule?scenario_id=$SID"
curl -s "localhost:8000/api/kpis?scenario_id=$SID"
curl -s "localhost:8000/api/alerts?scenario_id=$SID"
```

### With Docker

```bash
docker compose up --build
# http://localhost:8000
```

The SQLite database is stored in the `workshop-data` named volume.

### Tests

```bash
pytest -q
```

---

## Example payloads

**`POST /api/solve` → schedule row (Gantt bar)**

```json
{
  "schedule_id": "sch_451c85154d4d",
  "scenario_id": "scn_522fab044420",
  "solver_status": "optimal",
  "makespan_min": 2364,
  "horizon_start": "2026-06-08T08:00:00",
  "rows": [
    {
      "machine_id": "mch_0001",
      "machine_name": "Laser Cutting #1",
      "machine_type": "laser_cutting",
      "operations": [
        {
          "operation_id": "op_0008",
          "work_order_code": "WO-1002",
          "op_type": "laser_cutting",
          "start_min": 65, "end_min": 282, "setup_min": 30,
          "start": "2026-06-08T09:05:00", "end": "2026-06-08T12:42:00",
          "status": "scheduled"
        }
      ]
    }
  ]
}
```

**`GET /api/kpis`**

```json
{
  "scheduled_orders": 7,
  "total_orders": 7,
  "on_time_rate": 0.8571,
  "avg_lateness_min": 97.14,
  "makespan_min": 2364,
  "overall_utilisation_pct": 25.1,
  "bottleneck_machine_id": "mch_0001",
  "backlog_size": 0,
  "tonnage_scheduled_today_kg": 314.94,
  "num_alerts": 1
}
```

**`GET /api/alerts`**

```json
{
  "scenario_id": "scn_522fab044420",
  "schedule_id": "sch_451c85154d4d",
  "alerts": [
    {
      "severity": "critical",
      "type": "late_order",
      "message": "Work order WO-1004 is late by 312 min (priority=critical).",
      "entity_refs": ["wo_0005"]
    }
  ]
}
```

---

## Edge cases handled

* **No operations** → solver returns `EMPTY` status, empty schedule (no crash).
* **Infeasible / timeout** → status surfaced as `INFEASIBLE`/`UNKNOWN`, empty
  schedule, critical alert raised.
* **Schedule/KPIs before solving** → `404` with a clear "call POST /solve" hint.
* **Unknown `scenario_id`** → `404`.
* **`/schedule` without any id** → `400`.
* **Material shortage** → `material_shortage` alert when required mass exceeds
  available stock.
* **Tight due dates** → produce realistic lateness, on-time-rate < 1, and alerts.

---

## Risks & assumptions

* **Operators** are modelled but not hard-constrained in v1 (informational).
* **Setup time** is folded into operation duration; sequence-dependent setup is
  a next step.
* **Shifts/calendars** are carried in data but not enforced as blocking time in
  the solver v1 (an operation may span a night), to avoid infeasibility from ops
  longer than a single shift. Maintenance and breakdowns *are* enforced.
* **SQLite stores JSON blobs** (prototype-grade), not normalized tables.
* On `large` scenarios the model can grow; the default `time_limit_s` keeps
  solves bounded and may return a feasible-but-not-proven-optimal schedule.

---

## Connecting to real ERP / MES data later

The `Scenario` aggregate is the integration boundary. To go live:

1. Implement adapters that hydrate the **same** domain models:
   * **SAP** → work orders, BOM, routings, due dates, priorities.
   * **MES** → machine states, operation status, actual setup/processing times.
   * **Shop-floor sensors** → live breakdowns and availability.
2. Swap `ScenarioService._generate` to call those adapters instead of the
   synthetic generator.
3. Optionally replace `SqliteScenario/ScheduleRepository` with a production store
   by implementing the ABCs in `app/repository/base.py`.

The solver, KPI, and API layers require **no changes** — they depend only on the
domain models.

---

## Next steps

* Sequence-dependent setup times and tool-change constraints.
* Hard operator/skill and shift-calendar constraints.
* Multi-objective Pareto exploration and warm-starting from the previous solve.
* Incremental re-scheduling on shop-floor events (rush orders, breakdowns).
* Normalized persistence + auth + Kubernetes manifests for production.
```
