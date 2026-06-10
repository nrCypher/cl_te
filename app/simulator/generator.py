"""Seeded synthetic scenario generator.

All randomness flows through a single ``random.Random(seed)`` instance so that a
given ``(seed, size, config)`` always yields a byte-identical scenario (modulo
the scenario/created_at metadata, which the determinism test ignores). Scenarios
are feasible by construction: every operation type that appears in a routing is
guaranteed at least one eligible machine.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.models.domain import (
    Breakdown,
    Machine,
    MaintenanceWindow,
    Material,
    Operation,
    OperationTemplate,
    Operator,
    Product,
    Routing,
    Shift,
    WorkOrder,
)
from app.models.enums import (
    ROUTING_FLOW,
    MachineType,
    Priority,
    ScenarioSize,
)
from app.models.scenario import Scenario
from app.simulator.config import SimulatorConfig, config_for_size

_MATERIAL_GRADES = ["DC01", "S235JR", "AISI304", "AISI316", "AlMg3", "DX51D"]
_PRODUCT_NAMES = [
    "Bracket", "Enclosure", "Panel", "Chassis", "Flange", "Cover",
    "Frame", "Mount", "Housing", "Plate", "Rail", "Duct", "Manifold",
    "Hinge", "Gusset", "Skid",
]


class SyntheticDataGenerator:
    """Builds a :class:`Scenario` from a seed and a :class:`SimulatorConfig`."""

    def __init__(
        self,
        seed: int,
        config: SimulatorConfig,
        size: ScenarioSize,
        horizon_start: datetime | None = None,
        name: str | None = None,
    ) -> None:
        self.seed = seed
        self.config = config
        self.size = size
        self.rng = random.Random(seed)
        # Anchor the horizon to a stable, seed-independent start so two runs
        # with the same seed produce identical *time* fields too. Default:
        # 08:00 on a fixed reference Monday.
        self.horizon_start = horizon_start or datetime(2026, 6, 8, 8, 0, 0)
        self.name = name or f"{size.value}-seed{seed}"
        self._counters: dict[str, int] = {}

    # -- id helpers -------------------------------------------------------

    def _next(self, prefix: str) -> str:
        n = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = n
        return f"{prefix}_{n:04d}"

    def _ri(self, bounds: tuple[int, int]) -> int:
        return self.rng.randint(bounds[0], bounds[1])

    def _rf(self, bounds: tuple[float, float]) -> float:
        return round(self.rng.uniform(bounds[0], bounds[1]), 3)

    # -- public API -------------------------------------------------------

    @classmethod
    def for_size(
        cls,
        seed: int,
        size: ScenarioSize,
        horizon_start: datetime | None = None,
        name: str | None = None,
    ) -> "SyntheticDataGenerator":
        return cls(seed, config_for_size(size), size, horizon_start, name)

    def generate(self) -> Scenario:
        horizon_minutes = (
            self.config.horizon_days
            * self.config.shifts_per_day
            * self.config.shift_length_min
        )

        materials = self._gen_materials()
        machines = self._gen_machines()
        machines_by_type = self._index_machines(machines)
        routings, products = self._gen_routings_and_products(materials)
        work_orders = self._gen_work_orders(products, horizon_minutes)
        operations = self._expand_operations(
            work_orders, products, routings, machines_by_type
        )
        operators = self._gen_operators()
        shifts = self._gen_shifts(machines)
        maintenance = self._gen_maintenance(machines, horizon_minutes)
        breakdowns = self._gen_breakdowns(machines, horizon_minutes)

        return Scenario(
            name=self.name,
            seed=self.seed,
            size=self.size,
            horizon_start=self.horizon_start,
            horizon_minutes=horizon_minutes,
            materials=materials,
            machines=machines,
            routings=routings,
            products=products,
            work_orders=work_orders,
            operations=operations,
            operators=operators,
            shifts=shifts,
            maintenance_windows=maintenance,
            breakdowns=breakdowns,
        )

    # -- generators -------------------------------------------------------

    def _gen_materials(self) -> list[Material]:
        out: list[Material] = []
        for _ in range(self._ri(self.config.num_materials)):
            grade = self.rng.choice(_MATERIAL_GRADES)
            out.append(
                Material(
                    id=self._next("mat"),
                    name=f"Sheet {grade}",
                    grade=grade,
                    thickness_mm=self.rng.choice([0.8, 1.0, 1.5, 2.0, 3.0, 4.0]),
                    available_kg=round(self.rng.uniform(500, 8000), 1),
                )
            )
        return out

    def _gen_machines(self) -> list[Machine]:
        out: list[Machine] = []
        for mtype in MachineType:
            count = self._ri(self.config.machines_per_type)
            for i in range(count):
                out.append(
                    Machine(
                        id=self._next("mch"),
                        name=f"{mtype.value.replace('_', ' ').title()} #{i + 1}",
                        type=mtype,
                        capacity=1,
                        cost_per_hour=round(self.rng.uniform(40, 220), 2),
                        speed_factor=self._rf(self.config.speed_factor),
                    )
                )
        return out

    @staticmethod
    def _index_machines(machines: list[Machine]) -> dict[MachineType, list[Machine]]:
        idx: dict[MachineType, list[Machine]] = {}
        for m in machines:
            idx.setdefault(m.type, []).append(m)
        return idx

    def _gen_routings_and_products(
        self, materials: list[Material]
    ) -> tuple[list[Routing], list[Product]]:
        routings: list[Routing] = []
        products: list[Product] = []
        for _ in range(self._ri(self.config.num_products)):
            product_id = self._next("prd")
            routing_id = self._next("rtg")
            op_types = self._sample_routing_flow()

            templates: list[OperationTemplate] = []
            for pos, op_type in enumerate(op_types):
                templates.append(
                    OperationTemplate(
                        id=self._next("opt"),
                        name=f"{op_type.value.replace('_', ' ').title()}",
                        op_type=op_type,
                        position=pos,
                        base_processing_min_per_unit=self._rf(
                            self.config.processing_min_per_unit
                        ),
                        setup_min=self._ri(self.config.setup_min),
                        material_kg_per_unit=self._rf(
                            self.config.material_kg_per_unit
                        )
                        if pos == 0
                        else 0.0,
                        eligible_machine_types=[op_type],
                    )
                )
            routings.append(
                Routing(id=routing_id, product_id=product_id, operations=templates)
            )
            material = self.rng.choice(materials)
            products.append(
                Product(
                    id=product_id,
                    name=f"{self.rng.choice(_PRODUCT_NAMES)} {product_id[-3:]}",
                    material_id=material.id,
                    routing_id=routing_id,
                    unit_weight_kg=round(self.rng.uniform(0.4, 9.0), 2),
                )
            )
        return routings, products

    def _sample_routing_flow(self) -> list[MachineType]:
        """Pick an ordered, realistic subset of the sheet-metal flow.

        Always starts with cutting/stamping and ends with assembly/finishing,
        with a random middle, preserving the natural process order.
        """
        n = self._ri(self.config.ops_per_routing)
        n = min(n, len(ROUTING_FLOW))
        # Always include a cutting-style first op and keep order.
        chosen = [ROUTING_FLOW[0]]
        middle = list(ROUTING_FLOW[1:])
        self.rng.shuffle(middle)
        extras = sorted(
            middle[: n - 1], key=lambda t: ROUTING_FLOW.index(t)
        )
        chosen.extend(extras)
        return chosen

    def _gen_work_orders(
        self, products: list[Product], horizon_minutes: int
    ) -> list[WorkOrder]:
        out: list[WorkOrder] = []
        n = self._ri(self.config.num_work_orders)
        for i in range(n):
            product = self.rng.choice(products)
            release_offset = self.rng.randint(0, max(0, horizon_minutes // 4))
            release = self.horizon_start + timedelta(minutes=release_offset)

            tight = self.rng.random() < self.config.tight_due_fraction
            if tight:
                due_offset = release_offset + self.rng.randint(
                    horizon_minutes // 6, horizon_minutes // 3
                )
            else:
                due_offset = release_offset + self.rng.randint(
                    horizon_minutes // 2, int(horizon_minutes * 1.2)
                )
            due = self.horizon_start + timedelta(minutes=due_offset)

            priority = self.rng.choices(
                list(Priority),
                weights=[0.4, 0.3, 0.2, 0.1],
                k=1,
            )[0]
            out.append(
                WorkOrder(
                    id=self._next("wo"),
                    code=f"WO-{1000 + i}",
                    product_id=product.id,
                    quantity=self._ri(self.config.quantity),
                    release_date=release,
                    due_date=due,
                    priority=priority,
                )
            )
        return out

    def _expand_operations(
        self,
        work_orders: list[WorkOrder],
        products: list[Product],
        routings: list[Routing],
        machines_by_type: dict[MachineType, list[Machine]],
    ) -> list[Operation]:
        product_map = {p.id: p for p in products}
        routing_map = {r.id: r for r in routings}
        operations: list[Operation] = []

        for wo in work_orders:
            product = product_map[wo.product_id]
            routing = routing_map[product.routing_id]
            predecessor_id: str | None = None
            for tmpl in routing.operations:
                eligible = [m.id for m in machines_by_type.get(tmpl.op_type, [])]
                # Feasibility invariant: machines exist for every op type
                # because _gen_machines creates >=1 per MachineType.
                duration = int(
                    round(
                        tmpl.setup_min
                        + tmpl.base_processing_min_per_unit * wo.quantity
                    )
                )
                op = Operation(
                    id=self._next("op"),
                    work_order_id=wo.id,
                    template_id=tmpl.id,
                    name=tmpl.name,
                    op_type=tmpl.op_type,
                    position=tmpl.position,
                    duration_min=max(1, duration),
                    setup_min=int(tmpl.setup_min),
                    material_kg=round(tmpl.material_kg_per_unit * wo.quantity, 2),
                    eligible_machine_ids=eligible,
                    predecessor_id=predecessor_id,
                )
                operations.append(op)
                predecessor_id = op.id
        return operations

    def _gen_operators(self) -> list[Operator]:
        out: list[Operator] = []
        all_types = list(MachineType)
        for _ in range(self._ri(self.config.num_operators)):
            k = self.rng.randint(1, 3)
            out.append(
                Operator(
                    id=self._next("opr"),
                    name=f"Operator {self._counters.get('opr', 0):02d}",
                    skills=self.rng.sample(all_types, k),
                )
            )
        return out

    def _gen_shifts(self, machines: list[Machine]) -> list[Shift]:
        """Working-time windows shared by all machines (machine_id=None)."""
        out: list[Shift] = []
        day_minutes = 24 * 60
        for day in range(self.config.horizon_days):
            for s in range(self.config.shifts_per_day):
                start = day * day_minutes + s * self.config.shift_length_min
                out.append(
                    Shift(
                        id=self._next("shf"),
                        name=f"Day {day + 1} Shift {s + 1}",
                        machine_id=None,
                        start_min=start,
                        end_min=start + self.config.shift_length_min,
                    )
                )
        return out

    def _gen_maintenance(
        self, machines: list[Machine], horizon_minutes: int
    ) -> list[MaintenanceWindow]:
        out: list[MaintenanceWindow] = []
        for m in machines:
            if self.rng.random() < self.config.maintenance_probability:
                start = self.rng.randint(0, max(1, horizon_minutes - 120))
                out.append(
                    MaintenanceWindow(
                        id=self._next("mnt"),
                        machine_id=m.id,
                        start_min=start,
                        end_min=start + self.rng.randint(60, 120),
                    )
                )
        return out

    def _gen_breakdowns(
        self, machines: list[Machine], horizon_minutes: int
    ) -> list[Breakdown]:
        out: list[Breakdown] = []
        for m in machines:
            if self.rng.random() < self.config.breakdown_probability:
                start = self.rng.randint(0, max(1, horizon_minutes - 90))
                out.append(
                    Breakdown(
                        id=self._next("brk"),
                        machine_id=m.id,
                        start_min=start,
                        end_min=start + self.rng.randint(30, 90),
                        cause=self.rng.choice(
                            ["tool_wear", "jam", "sensor_fault", "power"]
                        ),
                    )
                )
        return out
