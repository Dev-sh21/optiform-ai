"""AI Design Advisor for Formwork Standardization.

This module analyzes floor designs and identifies "Near-Standard" opportunities.
If a floor's requirements are close to an existing cluster's peak, we suggest
standardizing that floor to merge it into the cluster, reducing total BoQ.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import List, Dict

class DesignAdvisor:
    def __init__(self, cluster_data: pd.DataFrame, behavior_threshold: float = 0.10):
        """
        Args:
            cluster_data: DataFrame with cluster_id and counts.
            behavior_threshold: % difference to consider as "near-standard".
        """
        self.df = cluster_data
        self.threshold = behavior_threshold

    def analyze_standardization_opportunities(self) -> pd.DataFrame:
        """Finds floors that could be merged into clusters with minor design changes."""
        # Calculate cluster peaks
        peaks = self.df.groupby('cluster_id').agg({
            'column_count': 'max',
            'beam_count': 'max',
            'slab_count': 'max'
        }).rename(columns=lambda x: f'peak_{x}')

        merged = self.df.merge(peaks, on='cluster_id')
        
        # Calculate deviation from peak
        merged['col_diff'] = (merged['peak_column_count'] - merged['column_count']) / merged['peak_column_count']
        merged['beam_diff'] = (merged['peak_beam_count'] - merged['beam_count']) / merged['peak_beam_count']
        
        # Floors with significant variance within their own cluster are "Sub-Optimal"
        # We look for "Outliers" in the cluster that could be standardized to the cluster mean
        opportunities = []
        
        for cid in self.df['cluster_id'].unique():
            cluster_subset = self.df[self.df['cluster_id'] == cid]
            avg_area = cluster_subset['formwork_area'].mean()
            
            # Suggesting area standardization
            for _, floor in cluster_subset.iterrows():
                area_dev = abs(floor['formwork_area'] - avg_area) / avg_area
                if area_dev > 0.02 and area_dev < self.threshold:
                    opportunities.append({
                        "floor_id": floor['floor_id'],
                        "current_cluster": cid,
                        "suggestion": "Standardize Floor Plate",
                        "impact": f"Reduce area variance by {area_dev:.1%}",
                        "potential_saving": "Estimated 5% Kit Optimization"
                    })
                    
        return pd.DataFrame(opportunities)

def get_standardization_report(df: pd.DataFrame) -> pd.DataFrame:
    advisor = DesignAdvisor(df)
    return advisor.analyze_standardization_opportunities()
