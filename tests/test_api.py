"""End-to-end API tests over an in-memory database."""

from __future__ import annotations

from app.models.enums import SolverStatus


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_full_flow_simulate_solve_schedule_kpis_alerts(client):
    # Simulate (deterministic seed).
    r = client.post("/api/simulate", json={"seed": 42, "size": "small"})
    assert r.status_code == 200
    scenario = r.json()
    sid = scenario["id"]
    assert scenario["machines"]
    assert scenario["work_orders"]

    # Machines.
    r = client.get(f"/api/machines?scenario_id={sid}")
    assert r.status_code == 200
    assert len(r.json()) == len(scenario["machines"])

    # Work orders with operations.
    r = client.get(f"/api/work-orders?scenario_id={sid}")
    assert r.status_code == 200
    wos = r.json()
    assert wos and wos[0]["operations"]

    # Solve.
    r = client.post("/api/solve", json={"scenario_id": sid})
    assert r.status_code == 200
    result = r.json()
    assert result["status"] in (
        SolverStatus.OPTIMAL.value,
        SolverStatus.FEASIBLE.value,
    )
    assert result["feasible"]

    # Schedule (Gantt rows).
    r = client.get(f"/api/schedule?scenario_id={sid}")
    assert r.status_code == 200
    schedule = r.json()
    assert schedule["rows"]
    assert schedule["makespan_min"] > 0
    total_ops = sum(len(row["operations"]) for row in schedule["rows"])
    assert total_ops == len(scenario["operations"])

    # KPIs.
    r = client.get(f"/api/kpis?scenario_id={sid}")
    assert r.status_code == 200
    kpi = r.json()
    assert kpi["scheduled_orders"] == len(scenario["work_orders"])
    assert 0.0 <= kpi["on_time_rate"] <= 1.0

    # Alerts.
    r = client.get(f"/api/alerts?scenario_id={sid}")
    assert r.status_code == 200
    assert "alerts" in r.json()


def test_create_and_get_scenario(client):
    r = client.post("/api/scenarios", json={"seed": 1, "size": "small"})
    assert r.status_code == 201
    summary = r.json()
    assert summary["num_machines"] > 0

    r = client.get(f"/api/scenarios/{summary['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == summary["id"]


def test_unknown_scenario_returns_404(client):
    assert client.get("/api/machines?scenario_id=nope").status_code == 404
    assert client.get("/api/scenarios/nope").status_code == 404


def test_schedule_before_solve_returns_404(client):
    r = client.post("/api/scenarios", json={"seed": 5, "size": "small"})
    sid = r.json()["id"]
    assert client.get(f"/api/schedule?scenario_id={sid}").status_code == 404


def test_schedule_requires_an_id(client):
    assert client.get("/api/schedule").status_code == 400


def test_deterministic_api_simulation(client):
    """Fixed seed via the API yields identical structural counts."""
    a = client.post("/api/simulate", json={"seed": 99, "size": "small"}).json()
    b = client.post("/api/simulate", json={"seed": 99, "size": "small"}).json()
    assert len(a["machines"]) == len(b["machines"])
    assert len(a["work_orders"]) == len(b["work_orders"])
    assert len(a["operations"]) == len(b["operations"])
    # Same routing structure (op types in order) for the first work order.
    a_ops = [o["op_type"] for o in a["operations"]]
    b_ops = [o["op_type"] for o in b["operations"]]
    assert a_ops == b_ops
