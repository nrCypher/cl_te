"""KPI and alert computation (pure functions over Scenario + Schedule)."""

from app.kpi.calculator import build_alerts, compute_kpis

__all__ = ["build_alerts", "compute_kpis"]
