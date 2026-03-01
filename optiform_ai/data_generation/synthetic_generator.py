"""Synthetic dataset builder for formwork lifecycle simulations."""
from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class GenerationConfig:
    sample_size: int = 1000
    time_horizon_days: int = 90
    seed: int | None = 42


class SyntheticDataGenerator:
    """Generate reproducible formwork demand, carbon, and cost scenarios."""

    def __init__(self, config: GenerationConfig | None = None) -> None:
        self.config = config or GenerationConfig()
        if self.config.seed is not None:
            np.random.seed(self.config.seed)

    def generate(self) -> pd.DataFrame:
        """Return a synthetic dataset placeholder.

        Replace this with domain-specific logic: project schedules, crew sizes,
        panel requirements, cycle times, weather delays, etc.
        """
        days = np.arange(self.config.time_horizon_days)
        demand = np.random.poisson(lam=20, size=self.config.time_horizon_days)
        carbon_intensity = np.random.normal(loc=35, scale=5, size=self.config.time_horizon_days)
        rental_rate = np.random.uniform(8, 14, size=self.config.time_horizon_days)

        df = pd.DataFrame(
            {
                "day": days,
                "panel_demand": demand,
                "carbon_intensity_kg_co2e": carbon_intensity,
                "rental_rate_usd": rental_rate,
            }
        )
        df["panel_demand"] = df["panel_demand"].clip(lower=0)
        return df

    def describe(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Basic profiling hook; extend with more domain diagnostics."""
        return {
            "rows": len(data),
            "columns": list(data.columns),
            "demand_mean": float(data["panel_demand"].mean()),
        }
