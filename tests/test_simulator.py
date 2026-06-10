"""Simulator unit tests, including a deterministic fixed-seed contract."""

from __future__ import annotations

from app.models.enums import MachineType, ScenarioSize
from app.simulator.config import SIZE_PRESETS
from app.simulator.generator import SyntheticDataGenerator


def _gen(seed: int, size: ScenarioSize):
    return SyntheticDataGenerator.for_size(seed=seed, size=size).generate()


def test_determinism_same_seed_identical_scenario():
    """Same (seed, size) -> byte-identical scenario, ignoring id/created_at."""
    a = _gen(123, ScenarioSize.SMALL)
    b = _gen(123, ScenarioSize.SMALL)
    exclude = {"id", "created_at"}
    assert a.model_dump(exclude=exclude) == b.model_dump(exclude=exclude)


def test_different_seed_differs():
    a = _gen(1, ScenarioSize.SMALL)
    b = _gen(2, ScenarioSize.SMALL)
    assert a.model_dump(exclude={"id", "created_at"}) != b.model_dump(
        exclude={"id", "created_at"}
    )


def test_size_presets_scale_counts():
    small = _gen(5, ScenarioSize.SMALL)
    large = _gen(5, ScenarioSize.LARGE)
    assert len(large.work_orders) > len(small.work_orders)
    assert len(large.machines) >= len(small.machines)


def test_every_op_type_has_eligible_machine():
    """Feasibility invariant: each operation has >=1 eligible machine."""
    scenario = _gen(9, ScenarioSize.MEDIUM)
    machine_types = {m.type for m in scenario.machines}
    for op in scenario.operations:
        assert op.eligible_machine_ids, f"{op.id} has no eligible machine"
        assert MachineType(op.op_type) in machine_types


def test_due_dates_after_release():
    scenario = _gen(11, ScenarioSize.MEDIUM)
    for wo in scenario.work_orders:
        assert wo.due_date >= wo.release_date


def test_operations_expanded_per_work_order():
    scenario = _gen(3, ScenarioSize.SMALL)
    for wo in scenario.work_orders:
        ops = scenario.operations_for(wo.id)
        assert ops, f"{wo.code} has no operations"
        # Precedence chain is linear and ordered by position.
        positions = [o.position for o in ops]
        assert positions == sorted(positions)
        assert ops[0].predecessor_id is None
        for prev, cur in zip(ops, ops[1:]):
            assert cur.predecessor_id == prev.id


def test_horizon_is_positive():
    for size in ScenarioSize:
        scenario = _gen(2, size)
        assert scenario.horizon_minutes > 0
        assert scenario.horizon_end > scenario.horizon_start


def test_presets_cover_all_sizes():
    assert set(SIZE_PRESETS) == set(ScenarioSize)
