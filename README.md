# OptiForm AI – Intelligent Formwork Lifecycle Optimization Platform

Enterprise-grade scaffold for simulating, optimizing, and deciding rental vs. purchase strategies for formwork systems, with carbon and ROI visibility and a Streamlit dashboard front-end.

---

## Overview
OptiForm AI combines synthetic data generation, repetition detection, inventory optimization, rent/buy decisioning, carbon estimation, and ROI calculation into a modular Python package. It is designed for contractors, EPCs, and owners to prototype digital workflows before wiring into production ERP/BIM stacks.

Core capabilities:
- Generate realistic multi-floor datasets with vertical repetition patterns.
- Detect repeating floor designs to maximize formwork reuse.
- Optimize inventory sizing (columns, beams, slabs) with PuLP/OR-Tools.
- Compare rental vs. purchase (or mixed) strategies with economic and carbon signals.
- Visualize scenarios in a Streamlit dashboard; export results for downstream systems.

---

## Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage
### 1) Run the dashboard
```bash
streamlit run optiform_ai/dashboard/app.py
```
Workflow in the UI:
1. Upload a CSV or generate synthetic data.
2. Run repetition detection (clustering).
3. Optimize inventory.
4. Get rent/buy recommendation.
5. Review carbon and ROI metrics.

### 2) Programmatic example
```python
from optiform_ai.data_generation.synthetic_data import generate_synthetic_formwork_data
from optiform_ai.optimization_engine import get_clusters, optimize_formwork
from optiform_ai.rental_purchase_module import decide_rent_or_buy
from optiform_ai.carbon_module.carbon_calculator import calculate_carbon
from optiform_ai.utils import calculate_roi

data = generate_synthetic_formwork_data()
labeled, _ = get_clusters(data)
plan, inventory_cost = optimize_formwork(labeled)

decision = decide_rent_or_buy(
    project_duration_days=150,
    rental_cost_total=2_000_000,
    purchase_cost_total=4_500_000,
    inventory_cost=inventory_cost,
    optimization_plan=plan,
)

carbon = calculate_carbon(steel_tons=25, plywood_m3=12, steel_reuse_cycles=60, plywood_reuse_cycles=8)
roi = calculate_roi(
    baseline_cost_rupees=10_000_000,
    optimized_cost_rupees=inventory_cost,
    recommendation=decision.recommendation,
    rental_cost_rupees=2_000_000,
    purchase_cost_rupees=4_500_000,
)
print(decision, carbon, roi)
```

---

## Module Descriptions
- `optiform_ai/data_generation`: synthetic floor datasets with repetition patterns and quantities.
- `optiform_ai/optimization_engine`: repetition clustering, inventory sizing optimizer, core LP/MIP hooks.
- `optiform_ai/rental_purchase_module`: rent vs. purchase economics and decision engine.
- `optiform_ai/carbon_module`: reuse-aware carbon estimation for steel formwork and plywood.
- `optiform_ai/utils`: configuration, logging, ROI calculator.
- `optiform_ai/dashboard`: Streamlit UI pipeline.

---

## Folder Structure
```
optiform_ai/
  data_generation/
  optimization_engine/
  rental_purchase_module/
  carbon_module/
  dashboard/
  utils/
requirements.txt
README.md
```

---

## Expected Outputs
- **Cluster summary**: floors per cluster for repetition leverage.
- **Optimization plan**: per-cluster set counts, reuse moves, and inventory cost.
- **Recommendation**: rent / buy / mixed, with rationale.
- **Financials**: baseline vs. optimized cost, ROI %, rupees saved.
- **Carbon**: per-use steel/plywood emissions and reduction from higher reuse.

---

## Integration Guidance (SAP / ERP / BIM)
- **Data ingress**: accept CSV exports from SAP/ERP (project WBS, floor takeoffs) or BIM schedules; map columns to `floor_id`, `design_type`, `formwork_area`, `column_count`, `beam_count`, `slab_count`, `pattern_id`.
- **APIs**: wrap `get_clusters`, `optimize_formwork`, and `decide_rent_or_buy` behind a lightweight REST service (FastAPI/Flask) to be called from SAP PI/PO or SAP BTP integrations.
- **Master data**: store emission factors, rental/purchase price lists, and reuse assumptions in ERP master data tables; inject into cost/carbon calls via configuration.
- **BIM sync**: export optimized set counts per cluster to IFC/BCF or schedule tables; use GUIDs to align `floor_id` with BIM elements for 4D/5D workflows.
- **Events**: trigger recalculation on schedule changes or RFQ price updates via message bus (SAP Event Mesh/Kafka).

---

## Example Run (Screenshots)
Place screenshots under `docs/screenshots/` and reference them here:
- Dashboard overview: `![Dashboard Overview](docs/screenshots/dashboard_overview.png)`
- Cluster summary: `![Repetition Clusters](docs/screenshots/cluster_summary.png)`
- Optimization plan: `![Optimization Plan](docs/screenshots/optimization_plan.png)`
- ROI & Carbon: `![ROI and Carbon](docs/screenshots/roi_carbon.png)`

---

## Support & Next Steps
- Calibrate emission factors and price lists to project geography and vendors.
- Swap PuLP with OR-Tools CP-SAT for advanced constraints (concurrency, crane limits).
- Harden integrations with authenticated REST endpoints and audit logging.
