"""Detect repeated floor design patterns via clustering.

The detector groups floors with similar formwork quantities (area, columns,
beams, slabs) and returns cluster labels plus counts. It works with either
an in-memory DataFrame or a CSV path to keep demo usage flexible.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

REQUIRED_COLUMNS = [
    "floor_id",
    "design_type",
    "formwork_area",
    "column_count",
    "beam_count",
    "slab_count",
]


@dataclass
class ClusterConfig:
    """Tunables for the clustering run."""

    n_clusters: int | None = None
    random_state: int = 7
    max_clusters: int = 10  # guardrail when auto-selecting


def _load_data(data: Union[str, pd.DataFrame]) -> pd.DataFrame:
    """Load dataset from CSV path or pass-through a DataFrame."""
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, str):
        return pd.read_csv(data)
    raise TypeError("data must be a pandas.DataFrame or a CSV file path")


def _auto_cluster_count(n_rows: int, max_clusters: int) -> int:
    """Heuristic for cluster count when none is provided."""
    # Square-root heuristic bounded to avoid over-fragmentation
    return max(2, min(max_clusters, int(np.sqrt(max(n_rows, 2)))))


def _prepare_features(df: pd.DataFrame) -> np.ndarray:
    """Select and scale numeric features used for clustering."""
    features = df[["formwork_area", "column_count", "beam_count", "slab_count"]].copy()
    # Fill any gaps with column means to keep KMeans happy
    features = features.fillna(features.mean())
    scaler = StandardScaler()
    return scaler.fit_transform(features)


def get_clusters(
    data: Union[str, pd.DataFrame],
    config: ClusterConfig | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Cluster similar floor designs and return labeled data plus cluster counts.

    Returns
    -------
    labeled_df : DataFrame
        Original rows with an added `cluster_id` column.
    cluster_counts : DataFrame
        Two columns: `cluster_id` and `count`.
    """
    cfg = config or ClusterConfig()
    df = _load_data(data)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    n_clusters = cfg.n_clusters or _auto_cluster_count(len(df), cfg.max_clusters)
    X = _prepare_features(df)

    kmeans = KMeans(n_clusters=n_clusters, random_state=cfg.random_state, n_init=10)
    labels = kmeans.fit_predict(X)

    labeled_df = df.copy()
    labeled_df["cluster_id"] = labels

    cluster_counts = (
        labeled_df.groupby("cluster_id").size().rename("count").reset_index()
    )

    return labeled_df, cluster_counts


if __name__ == "__main__":
    # Example usage with the richer synthetic dataset
    from optiform_ai.data_generation.synthetic_data import generate_synthetic_formwork_data

    demo_df = generate_synthetic_formwork_data()
    labeled, counts = get_clusters(demo_df)
    print(labeled.head())
    print("\nCluster sizes:\n", counts)
