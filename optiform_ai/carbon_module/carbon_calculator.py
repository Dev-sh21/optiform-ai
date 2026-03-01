"""Carbon calculator for steel formwork and plywood with reuse adjustments.

Simple factors are used to keep the model transparent and easy to tune:
- Steel formwork: ~1.9 tCO2e per metric tonne manufactured (world steel avg).
- Plywood: ~0.45 tCO2e per m³ (cradle-to-gate, softwood ply).
- Reuse cycles: embodied emissions are amortized across expected uses.

These values are placeholders; replace with project- or EPD-specific factors
when available.
"""
from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from typing import Dict


@dataclass
class EmissionFactors:
    """Default emission factors (embodied only)."""

    steel_kg_co2e_per_ton: float = 1900.0  # Comment: tCO2e/ton -> kgCO2e/ton
    plywood_kg_co2e_per_m3: float = 450.0  # Comment: kgCO2e per cubic meter


def calculate_carbon(
    steel_tons: float,
    plywood_m3: float,
    steel_reuse_cycles: int = 50,
    plywood_reuse_cycles: int = 10,
    factors: EmissionFactors | None = None,
) -> Dict[str, float]:
    """Estimate carbon for steel formwork + plywood, adjusted for reuse.

    Parameters
    ----------
    steel_tons : float
        Mass of steel formwork procured (metric tonnes).
    plywood_m3 : float
        Volume of plywood procured (cubic meters).
    steel_reuse_cycles : int
        Expected number of reuses for steel sets.
    plywood_reuse_cycles : int
        Expected number of reuses for plywood sheets.
    factors : EmissionFactors, optional
        Override default emission factors.

    Returns
    -------
    dict with component and total emissions (kg CO2e).
    """
    f = factors or EmissionFactors()

    # Embodied emissions (one-time manufacturing)
    steel_embodied = steel_tons * f.steel_kg_co2e_per_ton
    plywood_embodied = plywood_m3 * f.plywood_kg_co2e_per_m3

    # Effective per-use emissions after amortizing across reuse cycles
    steel_per_use = steel_embodied / max(steel_reuse_cycles, 1)
    plywood_per_use = plywood_embodied / max(plywood_reuse_cycles, 1)

    total = steel_per_use + plywood_per_use
    return {
        "steel_embodied_kg": steel_embodied,
        "plywood_embodied_kg": plywood_embodied,
        "steel_per_use_kg": steel_per_use,
        "plywood_per_use_kg": plywood_per_use,
        "total_per_use_kg": total,
    }


class CarbonCalculator:
    """Class wrapper for carbon calculations as expected by the dashboard."""

    def __init__(self, factors: EmissionFactors | None = None) -> None:
        self.factors = factors or EmissionFactors()

    def add_carbon_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add carbon-related columns to a dataset."""
        df = df.copy()
        # Use slab_count as a proxy for panel demand if available
        demand_col = "slab_count" if "slab_count" in df.columns else "panel_demand"
        
        # Assume 1 panel/unit = 0.5 tons of steel and 0.2 m3 of plywood for scale
        df["embodied_carbon_kg"] = df[demand_col] * (
            0.5 * self.factors.steel_kg_co2e_per_ton + 0.2 * self.factors.plywood_kg_co2e_per_m3
        )
        # Add a transport carbon mock
        df["transport_carbon_kg"] = df[demand_col] * 5.5  # 5.5 kg CO2e per unit
        return df


if __name__ == "__main__":
    # Example usage
    results = calculate_carbon(
        steel_tons=25,            # 25 t of steel formwork
        plywood_m3=12,            # 12 m3 of plywood
        steel_reuse_cycles=60,    # durable steel sets
        plywood_reuse_cycles=8,   # plywood degrades faster
    )
    for k, v in results.items():
        print(f"{k}: {v:,.1f} kg CO2e")
