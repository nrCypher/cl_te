"""Synthetic data simulator.

Generates realistic but fake workshop scenarios. This is the layer an ERP/MES
integration would replace: produce a ``Scenario`` from real data instead of
random sampling, and the solver/KPI/API layers keep working unchanged.
"""

from app.simulator.config import SIZE_PRESETS, SimulatorConfig
from app.simulator.generator import SyntheticDataGenerator

__all__ = ["SIZE_PRESETS", "SimulatorConfig", "SyntheticDataGenerator"]
