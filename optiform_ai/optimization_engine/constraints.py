"""Constraint factory for the optimization engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import pulp


@dataclass
class CarbonBudget:
    max_kg_co2e: float | None = None


@dataclass
class ConstraintSet:
    carbon_budget: CarbonBudget | None = None

    def build(self, model: pulp.LpProblem, rent_vars, data) -> Iterable[pulp.LpConstraint]:
        """Yield pulp constraints based on configured policies."""
        constraints = []
        if self.carbon_budget and self.carbon_budget.max_kg_co2e is not None:
            carbon_expr = pulp.lpSum(
                rent_vars[day] * data.loc[day, "carbon_intensity_kg_co2e"] for day in data.index
            )
            constraints.append(carbon_expr <= self.carbon_budget.max_kg_co2e)
        return constraints
