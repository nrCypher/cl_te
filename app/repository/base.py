"""Abstract repository interfaces.

Services depend on these protocols, never on a concrete database. To integrate a
real ERP/MES, implement these methods against the real system of record.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.scenario import Scenario
from app.models.scheduling import Schedule


class ScenarioRepository(ABC):
    @abstractmethod
    def save(self, scenario: Scenario) -> Scenario: ...

    @abstractmethod
    def get(self, scenario_id: str) -> Scenario | None: ...

    @abstractmethod
    def list(self) -> list[Scenario]: ...

    @abstractmethod
    def delete(self, scenario_id: str) -> bool: ...


class ScheduleRepository(ABC):
    @abstractmethod
    def save(self, schedule: Schedule) -> Schedule: ...

    @abstractmethod
    def get(self, schedule_id: str) -> Schedule | None: ...

    @abstractmethod
    def get_latest_for_scenario(self, scenario_id: str) -> Schedule | None: ...

    @abstractmethod
    def list_for_scenario(self, scenario_id: str) -> list[Schedule]: ...
