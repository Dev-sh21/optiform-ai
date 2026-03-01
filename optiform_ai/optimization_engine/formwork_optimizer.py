"""Inventory sizing optimizer for reusable formwork sets.

Assumptions (lightweight but practical for early scoping):
- Floors are built sequentially within a repetition cluster; formwork can be
  reused across floors in the same cluster.
- To size inventory, we need at least the peak quantity among floors in that
  cluster for each component type (columns, beams, slabs).
- Each redeployment (move between floors) incurs a reuse / handling cost.

The model minimizes:
    total_cost = inventory_cost + reuse_cost

Where:
- inventory_cost is linear in set sizes (per-component unit costs)
- reuse_cost is proportional to the number of moves (floors_in_cluster - 1)
  times the total set count.

This is intentionally simple and transparent; swap out costs or constraints
with project-specific data (cycle times, crane limits, concurrency) as needed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Union

import pandas as pd
import pulp

REQUIRED_COLUMNS = [
    "cluster_id",
    "formwork_area",
    "column_count",
    "beam_count",
    "slab_count",
]


@dataclass
class CostModel:
    """Per-unit inventory costs and reuse handling cost."""

    column_set_cost: float = 25000.0   # Per Mivan-equivalent kit
    beam_set_cost: float = 18000.0
    slab_set_cost: float = 12000.0
    reuse_move_cost: float = 3000.0   # Refined: lower handling per move for bulk scaling


def optimize_formwork(
    data: Union[str, pd.DataFrame],
    cost_model: CostModel | None = None,
    solver: pulp.LpSolver | None = None,
) -> Tuple[pd.DataFrame, float]:
    """Optimize formwork inventory per repetition cluster.

    Parameters
    ----------
    data : DataFrame or CSV path
        Must contain cluster_id and the quantity columns.
    cost_model : CostModel, optional
        Override costs if desired.
    solver : pulp solver, optional
        Custom solver instance (e.g., PULP_CBC_CMD).

    Returns
    -------
    plan_df : DataFrame
        One row per cluster with optimal set counts and costs.
    total_material_cost : float
        Material value based on BoQ.
    total_reuse_cost : float
        Handling and logistics cost for repetition.
    """
    cost_model = cost_model or CostModel()
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError("data must be a pandas.DataFrame or CSV file path")

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Aggregate stats per cluster
    agg = (
        df.groupby("cluster_id")
        .agg(
            floors=("cluster_id", "size"),
            max_columns=("column_count", "max"),
            max_beams=("beam_count", "max"),
            max_slabs=("slab_count", "max"),
        )
        .reset_index()
    )

    model = pulp.LpProblem("formwork_inventory", pulp.LpMinimize)

    # Decision variables: integer set counts per cluster and component
    col_sets = {
        cid: pulp.LpVariable(f"col_sets_{cid}", lowBound=0, cat="Integer")
        for cid in agg["cluster_id"]
    }
    beam_sets = {
        cid: pulp.LpVariable(f"beam_sets_{cid}", lowBound=0, cat="Integer")
        for cid in agg["cluster_id"]
    }
    slab_sets = {
        cid: pulp.LpVariable(f"slab_sets_{cid}", lowBound=0, cat="Integer")
        for cid in agg["cluster_id"]
    }

    # Constraints: inventory must cover the peak requirement in the cluster
    for _, row in agg.iterrows():
        cid = row["cluster_id"]
        model += col_sets[cid] >= row["max_columns"], f"col_peak_{cid}"
        model += beam_sets[cid] >= row["max_beams"], f"beam_peak_{cid}"
        model += slab_sets[cid] >= row["max_slabs"], f"slab_peak_{cid}"

    # Objective: inventory cost + reuse (handling) cost
    inventory_cost = pulp.lpSum(
        cost_model.column_set_cost * col_sets[cid]
        + cost_model.beam_set_cost * beam_sets[cid]
        + cost_model.slab_set_cost * slab_sets[cid]
        for cid in agg["cluster_id"]
    )

    reuse_cost = pulp.lpSum(
        cost_model.reuse_move_cost
        * (row["floors"] - 1)
        * (col_sets[row["cluster_id"]] + beam_sets[row["cluster_id"]] + slab_sets[row["cluster_id"]])
        for _, row in agg.iterrows()
    )

    model += inventory_cost + reuse_cost

    model.solve(solver or pulp.PULP_CBC_CMD(msg=False))

    plan_rows = []
    total_material_cost = 0.0
    total_reuse_cost_agg = 0.0

    for _, row in agg.iterrows():
        cid = row["cluster_id"]
        cols = int(pulp.value(col_sets[cid]))
        beams = int(pulp.value(beam_sets[cid]))
        slabs = int(pulp.value(slab_sets[cid]))
        moves = int(max(row["floors"] - 1, 0))
        
        m_cost = (cols * cost_model.column_set_cost + 
                  beams * cost_model.beam_set_cost + 
                  slabs * cost_model.slab_set_cost)
        r_cost = moves * (cols + beams + slabs) * cost_model.reuse_move_cost
        
        total_material_cost += m_cost
        total_reuse_cost_agg += r_cost

        plan_rows.append(
            {
                "cluster_id": cid,
                "floors": int(row["floors"]),
                "column_sets": cols,
                "beam_sets": beams,
                "slab_sets": slabs,
                "reuse_moves": moves,
                "cluster_cost": m_cost + r_cost
            }
        )

    plan_df = pd.DataFrame(plan_rows)
    return plan_df, total_material_cost, total_reuse_cost_agg


if __name__ == "__main__":
    # Example usage with synthetic data + clustering
    from optiform_ai.data_generation.synthetic_data import generate_synthetic_formwork_data
    from optiform_ai.optimization_engine import get_clusters

    df = generate_synthetic_formwork_data()
    labeled, counts = get_clusters(df)
    plan, cost = optimize_formwork(labeled)
    print(plan)
    print(f"Total cost: {cost:,.2f}")
