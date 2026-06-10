"""KPI and alert orchestration over stored scenarios and schedules."""

from __future__ import annotations

from app.kpi.calculator import build_alerts, compute_kpis
from app.models.kpi import Alert, KPI
from app.models.scenario import Scenario
from app.models.scheduling import Schedule


class AnalyticsService:
    """Stateless: combines a scenario and schedule into KPIs/alerts."""

    def kpis(self, scenario: Scenario, schedule: Schedule) -> KPI:
        return compute_kpis(scenario, schedule)

    def alerts(self, scenario: Scenario, schedule: Schedule) -> list[Alert]:
        return build_alerts(scenario, schedule)
