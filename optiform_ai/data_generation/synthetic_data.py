"""Generate realistic synthetic formwork usage data with vertical repetition patterns.

The goal is to provide a richer demo dataset than the simple Poisson noise in
`synthetic_generator.py`. We model common high‑rise composition:

- Podium floors (heavier, larger grids)
- Typical stack (repeating pattern)
- Penthouse/setback levels (lighter grids)

Each floor is tagged with a `pattern_id` so downstream modules can reason about
repetitions (e.g., batching formwork reuse or crane picks).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PatternSpec:
    """Metadata describing a repeating vertical pattern."""

    pattern_id: str
    design_type: str
    area_factor: float  # Multiplier on base floor plate area
    column_density: Tuple[float, float]  # min/max columns per 100 m²
    beam_density: Tuple[float, float]  # min/max beams per 100 m²
    slab_panels_per_100m2: Tuple[float, float]  # min/max panels per 100 m²


@dataclass
class SyntheticDataConfig:
    """Configuration knobs for synthetic dataset generation."""

    num_floors: int = 28
    base_floor_area_m2: float = 1050.0
    base_floor_area_std: float = 80.0
    podium_floors: int = 3
    penthouse_floors: int = 2
    seed: int | None = 7


class SyntheticFormworkDataset:
    """Create a vertically consistent, pattern‑aware synthetic dataset."""

    def __init__(self, config: SyntheticDataConfig | None = None) -> None:
        self.config = config or SyntheticDataConfig()
        if self.config.seed is not None:
            np.random.seed(self.config.seed)
        self.patterns = self._build_pattern_specs()

    def _build_pattern_specs(self) -> List[PatternSpec]:
        """Define canonical pattern families."""
        return [
            PatternSpec(
                pattern_id="POD",
                design_type="podium",
                area_factor=1.20,
                column_density=(0.15, 0.20),  # Heavier grids for podiums
                beam_density=(0.20, 0.25),
                slab_panels_per_100m2=(2.5, 3.0),
            ),
            PatternSpec(
                pattern_id="TYP",
                design_type="typical",
                area_factor=1.0,
                column_density=(0.10, 0.12),  # Standard high-rise density
                beam_density=(0.15, 0.18),
                slab_panels_per_100m2=(2.0, 2.4),
            ),
            PatternSpec(
                pattern_id="PH",
                design_type="penthouse",
                area_factor=0.85,
                column_density=(0.08, 0.10),  # Lighter grids for setbacks
                beam_density=(0.12, 0.15),
                slab_panels_per_100m2=(1.5, 2.0),
            ),
        ]

    def _select_pattern_for_floor(self, floor: int) -> PatternSpec:
        """Pick pattern by vertical zone; keep deterministic mapping."""
        cfg = self.config
        if floor <= cfg.podium_floors:
            return self.patterns[0]  # POD
        if floor > cfg.num_floors - cfg.penthouse_floors:
            return self.patterns[2]  # PH
        return self.patterns[1]  # TYP

    def _sample_counts(
        self, area_m2: float, density_range: Tuple[float, float]
    ) -> int:
        """Convert density (per 100 m²) into integer counts with noise."""
        density = np.random.uniform(*density_range)
        mean_count = density * (area_m2 / 100)
        # Use Poisson around the mean to keep integers and some variance
        return int(np.random.poisson(lam=max(mean_count, 0.1)))

    def generate(self) -> pd.DataFrame:
        """Return a synthetic dataset with pattern labels and quantities."""
        cfg = self.config
        floors: List[int] = list(range(1, cfg.num_floors + 1))
        rows: List[dict] = []

        for floor in floors:
            pattern = self._select_pattern_for_floor(floor)

            # Draw floor plate area
            base_area = np.random.normal(cfg.base_floor_area_m2, cfg.base_floor_area_std)
            floor_area = max(base_area * pattern.area_factor, 400)  # avoid degenerate

            column_count = self._sample_counts(floor_area, pattern.column_density)
            beam_count = self._sample_counts(floor_area, pattern.beam_density)
            slab_count = self._sample_counts(floor_area, pattern.slab_panels_per_100m2)

            rows.append(
                {
                    "floor_id": floor,
                    "design_type": pattern.design_type,
                    "formwork_area": round(floor_area, 2),
                    "column_count": column_count,
                    "beam_count": beam_count,
                    "slab_count": slab_count,
                    "pattern_id": pattern.pattern_id,
                }
            )

        return pd.DataFrame(rows)


# Convenience factory for one‑liner usage
def generate_synthetic_formwork_data(config: SyntheticDataConfig | None = None) -> pd.DataFrame:
    """Public helper to generate the dataset."""
    return SyntheticFormworkDataset(config).generate()
