"""Decision engine to recommend renting, buying, or a mixed strategy for formwork.

The heuristic compares total rental cost versus purchase + inventory cost, while
considering project duration and reuse opportunities surfaced by the optimizer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class DecisionResult:
    """Structured output for downstream reporting."""

    recommendation: str  # "rent", "buy", or "mixed"
    rental_total: float
    buy_total: float
    project_duration_days: int
    rationale: str
    mixed_plan: Optional[pd.DataFrame] = None  # Optional allocation for mixed


def _peak_sets(plan: pd.DataFrame) -> dict:
    """Return peak counts across clusters for each component."""
    return {
        "column_sets": int(plan["column_sets"].max()),
        "beam_sets": int(plan["beam_sets"].max()),
        "slab_sets": int(plan["slab_sets"].max()),
    }


def _mixed_allocation(plan: pd.DataFrame) -> pd.DataFrame:
    """Suggest buying a base (70%) and renting the remaining 30% for peaks."""
    peaks = _peak_sets(plan)
    rows = []
    for comp, peak in peaks.items():
        base = max(1, round(0.7 * peak))
        rent = max(0, peak - base)
        rows.append({"component": comp, "buy_sets": base, "rent_sets": rent})
    return pd.DataFrame(rows)


def decide_rent_or_buy(
    project_duration_days: int,
    rental_cost_total: float,
    purchase_cost_total: float,
    inventory_cost: float = 0.0,
    optimization_plan: Optional[pd.DataFrame] = None,
    gap_threshold: float = 0.05,
) -> DecisionResult:
    """Recommend rent/buy/mixed given cost inputs and optional optimizer plan.

    Parameters
    ----------
    project_duration_days : int
        Length of the project; short projects favor renting.
    rental_cost_total : float
        Estimated total rental cost for required formwork sets.
    purchase_cost_total : float
        Capital expenditure to purchase formwork sets (excludes logistics).
    inventory_cost : float, optional
        Additional inventory handling/storage derived from the optimizer.
    optimization_plan : DataFrame, optional
        Output from `optimize_formwork` containing per-cluster set sizes; used to
        propose a mixed strategy.
    gap_threshold : float
        Relative gap needed to make a confident rent/buy decision.
    """
    maintenance_factor: float = 0.05   # 5% annual maintenance on purchase
    salvage_factor: float = 0.15       # 15% recovery value after project
    
    # Adjusted costs for practical ROI
    annual_maint = purchase_cost_total * maintenance_factor * (project_duration_days / 365)
    salvage_recovery = purchase_cost_total * salvage_factor
    
    buy_total = purchase_cost_total + inventory_cost + annual_maint - salvage_recovery
    rent_total = rental_cost_total

    # Early lean: very short projects typically rent
    if project_duration_days <= 45 and rent_total <= buy_total * (1 + gap_threshold):
        return DecisionResult(
            recommendation="rent",
            rental_total=rent_total,
            buy_total=buy_total,
            project_duration_days=project_duration_days,
            rationale="Short duration project; rental avoids capex and reuse friction.",
        )

    # Clear economic winner
    if rent_total < buy_total * (1 - gap_threshold):
        return DecisionResult(
            recommendation="rent",
            rental_total=rent_total,
            buy_total=buy_total,
            project_duration_days=project_duration_days,
            rationale="Rental cost meaningfully lower than buy + inventory.",
        )
    if buy_total < rent_total * (1 - gap_threshold):
        return DecisionResult(
            recommendation="buy",
            rental_total=rent_total,
            buy_total=buy_total,
            project_duration_days=project_duration_days,
            rationale="Purchase cost clearly beats rental over project horizon.",
        )

    # Mixed strategy: costs are close or duration is mid/long with peaks
    mixed_plan = _mixed_allocation(optimization_plan) if optimization_plan is not None else None
    rationale = "Costs are within threshold; blend buy for base load and rent for peaks."
    return DecisionResult(
        recommendation="mixed",
        rental_total=rent_total,
        buy_total=buy_total,
        project_duration_days=project_duration_days,
        rationale=rationale,
        mixed_plan=mixed_plan,
    )


if __name__ == "__main__":
    # Example usage with upstream optimizers
    from optiform_ai.data_generation.synthetic_data import generate_synthetic_formwork_data
    from optiform_ai.optimization_engine import get_clusters, optimize_formwork

    data = generate_synthetic_formwork_data()
    labeled, _ = get_clusters(data)
    plan, total_inventory_cost = optimize_formwork(labeled)

    # Assume rental and purchase bids for illustration
    rental_quote = 180_000.0
    purchase_quote = 220_000.0

    decision = decide_rent_or_buy(
        project_duration_days=150,
        rental_cost_total=rental_quote,
        purchase_cost_total=purchase_quote,
        inventory_cost=total_inventory_cost,
        optimization_plan=plan,
    )
    print(decision)
