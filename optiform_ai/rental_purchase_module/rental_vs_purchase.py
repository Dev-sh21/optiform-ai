"""Compare rental and purchase options for formwork portfolios."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
import numpy as np


@dataclass
class RentalPurchaseConfig:
    purchase_cost_per_panel: float = 120.0
    discount_rate: float = 0.08
    rental_markup: float = 0.0  # optional uplift over provided rental_rate_usd


class RentalPurchaseAnalyzer:
    """NPV-based economic comparison helper."""

    def __init__(self, config: RentalPurchaseConfig | None = None) -> None:
        self.config = config or RentalPurchaseConfig()

    def evaluate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Return high-level economics for rental vs purchase baselines."""
        rental_cost = float(((1 + self.config.rental_markup) * data["rental_rate_usd"] * data["panel_demand"]).sum())

        purchase_panels = data["panel_demand"].max()
        purchase_cost = float(purchase_panels * self.config.purchase_cost_per_panel)

        # Simple NPV placeholder (assumes daily cash flows)
        discount_factors = 1 / (1 + self.config.discount_rate / 365) ** data["day"]
        rental_npv = float((rental_cost * discount_factors.mean()))
        purchase_npv = float(purchase_cost * discount_factors.mean())

        return {
            "rental_cost_total": rental_cost,
            "purchase_cost_total": purchase_cost,
            "rental_npv": rental_npv,
            "purchase_npv": purchase_npv,
            "preferred_option": "rental" if rental_npv < purchase_npv else "purchase",
        }
