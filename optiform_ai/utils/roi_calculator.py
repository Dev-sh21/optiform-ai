"""ROI calculator comparing optimized plan vs baseline manual planning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ROIResult:
    roi_pct: float
    savings_rupees: float
    baseline_cost_rupees: float
    optimized_cost_rupees: float
    rationale: str


def calculate_roi(
    baseline_cost_rupees: float,
    optimized_cost_rupees: float,
    recommendation: str,
    rental_cost_rupees: float,
    purchase_cost_rupees: float,
) -> ROIResult:
    """Compute ROI vs. manual planning using optimizer and rent/buy decision.

    Parameters
    ----------
    baseline_cost_rupees : float
        Estimated total cost under manual planning (status quo).
    optimized_cost_rupees : float
        Cost from the optimization run (inventory + handling).
    recommendation : str
        Output from rent/buy decision engine: "rent", "buy", or "mixed".
    rental_cost_rupees : float
        Quoted total rental cost (if renting fully).
    purchase_cost_rupees : float
        Quoted total purchase cost (if buying fully).
    """
    # Choose the recommended path's cost to compare against baseline
    if recommendation == "rent":
        recommended_cost = optimized_cost_rupees + rental_cost_rupees
        rationale = "Rental strategy chosen; includes optimized inventory handling."
    elif recommendation == "buy":
        recommended_cost = optimized_cost_rupees + purchase_cost_rupees
        rationale = "Purchase strategy chosen; capex + optimized handling."
    else:  # mixed
        # Simple blend: 50/50 between rent and buy quotes; adjust as needed
        recommended_cost = optimized_cost_rupees + 0.5 * (rental_cost_rupees + purchase_cost_rupees)
        rationale = "Mixed strategy; cost blended between rental and purchase quotes."

    savings = baseline_cost_rupees - recommended_cost
    roi_pct = (savings / baseline_cost_rupees * 100) if baseline_cost_rupees else 0.0

    return ROIResult(
        roi_pct=roi_pct,
        savings_rupees=savings,
        baseline_cost_rupees=baseline_cost_rupees,
        optimized_cost_rupees=recommended_cost,
        rationale=rationale,
    )


if __name__ == "__main__":
    # Example usage
    baseline = 10_000_000  # rupees under manual planning
    optimized_inventory = 6_000_000
    rental_quote = 2_000_000
    purchase_quote = 4_500_000

    result = calculate_roi(
        baseline_cost_rupees=baseline,
        optimized_cost_rupees=optimized_inventory,
        recommendation="mixed",
        rental_cost_rupees=rental_quote,
        purchase_cost_rupees=purchase_quote,
    )
    print(result)
