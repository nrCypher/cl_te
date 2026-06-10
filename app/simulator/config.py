"""Simulator configuration and size presets.

A ``SimulatorConfig`` holds the *ranges* the generator samples from. Presets for
small/medium/large scenarios make it trivial to dial complexity up or down while
keeping a single code path. Override any field to craft bespoke scenarios.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import ScenarioSize


class SimulatorConfig(BaseModel):
    """Sampling ranges for one synthetic scenario.

    Ranges are inclusive ``(min, max)`` tuples sampled with the seeded RNG.
    """

    # Resource counts
    machines_per_type: tuple[int, int] = (1, 1)
    num_materials: tuple[int, int] = (3, 5)
    num_products: tuple[int, int] = (3, 5)
    num_work_orders: tuple[int, int] = (6, 10)
    num_operators: tuple[int, int] = (3, 5)

    # Routing shape
    ops_per_routing: tuple[int, int] = (3, 5)

    # Work-order parameters
    quantity: tuple[int, int] = (5, 40)
    processing_min_per_unit: tuple[float, float] = (2.0, 12.0)
    setup_min: tuple[int, int] = (10, 45)
    material_kg_per_unit: tuple[float, float] = (0.5, 6.0)

    # Time horizon (working days) and shift pattern
    horizon_days: int = Field(default=5, ge=1)
    shifts_per_day: int = Field(default=2, ge=1)
    shift_length_min: int = Field(default=480, gt=0)  # 8h

    # Disruptions
    maintenance_probability: float = Field(default=0.25, ge=0, le=1)
    breakdown_probability: float = Field(default=0.15, ge=0, le=1)

    # Fraction of work orders deliberately given a tight due date (drives
    # realistic lateness / alerts).
    tight_due_fraction: float = Field(default=0.25, ge=0, le=1)

    # Machine speed spread
    speed_factor: tuple[float, float] = (0.85, 1.15)


SIZE_PRESETS: dict[ScenarioSize, SimulatorConfig] = {
    ScenarioSize.SMALL: SimulatorConfig(
        machines_per_type=(1, 1),
        num_materials=(3, 4),
        num_products=(3, 4),
        num_work_orders=(6, 8),
        num_operators=(3, 4),
        ops_per_routing=(3, 4),
        horizon_days=4,
    ),
    ScenarioSize.MEDIUM: SimulatorConfig(
        machines_per_type=(1, 2),
        num_materials=(4, 6),
        num_products=(5, 8),
        num_work_orders=(18, 28),
        num_operators=(6, 10),
        ops_per_routing=(3, 5),
        horizon_days=7,
    ),
    ScenarioSize.LARGE: SimulatorConfig(
        machines_per_type=(2, 4),
        num_materials=(6, 10),
        num_products=(10, 16),
        num_work_orders=(70, 120),
        num_operators=(12, 20),
        ops_per_routing=(4, 6),
        horizon_days=10,
    ),
}


def config_for_size(size: ScenarioSize) -> SimulatorConfig:
    """Return a *copy* of the preset so callers can mutate safely."""
    return SIZE_PRESETS[size].model_copy(deep=True)
