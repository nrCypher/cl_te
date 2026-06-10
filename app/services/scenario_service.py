"""Scenario generation and retrieval.

Wraps the synthetic simulator and the scenario repository. This is the single
place to swap synthetic generation for a real ERP/MES feed: replace
``_generate`` with an adapter that returns a ``Scenario``.
"""

from __future__ import annotations

from datetime import datetime

from app.models.enums import ScenarioSize
from app.models.scenario import Scenario
from app.repository.base import ScenarioRepository
from app.simulator.generator import SyntheticDataGenerator


class ScenarioService:
    def __init__(self, repository: ScenarioRepository) -> None:
        self._repo = repository

    def create_scenario(
        self,
        seed: int,
        size: ScenarioSize,
        name: str | None = None,
        horizon_start: datetime | None = None,
    ) -> Scenario:
        """Generate a synthetic scenario and persist it."""
        scenario = self._generate(seed, size, name, horizon_start)
        return self._repo.save(scenario)

    def _generate(
        self,
        seed: int,
        size: ScenarioSize,
        name: str | None,
        horizon_start: datetime | None,
    ) -> Scenario:
        generator = SyntheticDataGenerator.for_size(
            seed=seed, size=size, horizon_start=horizon_start, name=name
        )
        return generator.generate()

    def get_scenario(self, scenario_id: str) -> Scenario | None:
        return self._repo.get(scenario_id)

    def list_scenarios(self) -> list[Scenario]:
        return self._repo.list()
