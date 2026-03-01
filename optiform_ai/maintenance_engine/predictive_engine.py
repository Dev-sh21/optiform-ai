"""Predictive Fatigue & Maintenance Engine for Formwork.

Calculates the 'Health Index' of formwork kits based on reuse cycles
and provides maintenance alerts to improve on-site safety.
"""
from __future__ import annotations
import pandas as pd
import numpy as np

class MaintenanceEngine:
    def __init__(self, cycle_limit: int = 50):
        self.cycle_limit = cycle_limit

    def predict_health(self, optimization_plan: pd.DataFrame) -> pd.DataFrame:
        """
        Estimates health based on 'reuse_moves'.
        In a real scenario, this would use sensor data (load, weather).
        """
        health_data = []
        for _, row in optimization_plan.iterrows():
            cid = row['cluster_id']
            moves = row['reuse_moves']
            
            # Logic: More moves = Lower health
            # Base wear + per-move wear
            health_score = max(0, 100 - (moves * 1.5))
            
            status = "Healthy"
            if health_score < 40:
                status = "Critical (Replace)"
            elif health_score < 70:
                status = "Maintenance Required"
                
            health_data.append({
                "Cluster": cid,
                "Health Index": f"{health_score:.1f}%",
                "Status": status,
                "Est. Remaining Cycles": max(0, self.cycle_limit - moves)
            })
            
        return pd.DataFrame(health_data)

def get_maintenance_forecast(plan: pd.DataFrame) -> pd.DataFrame:
    engine = MaintenanceEngine()
    return engine.predict_health(plan)
