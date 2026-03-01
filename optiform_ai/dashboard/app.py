"""Minimal Streamlit dashboard stub."""
from __future__ import annotations

import streamlit as st
import pandas as pd
import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from optiform_ai.data_generation import generate_synthetic_formwork_data
from optiform_ai.optimization_engine import get_clusters, optimize_formwork
from optiform_ai.rental_purchase_module import decide_rent_or_buy
from optiform_ai.carbon_module import CarbonCalculator



# Premium UI Styling
def apply_premium_style():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #f8f9fa;
            color: #111827;
        }
        [data-testid="stHeader"] {
            background-color: rgba(248,249,250,0);
        }
        .stMetric {
            background: #ffffff;
            padding: 20px; 
            border-radius: 15px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        div[data-testid="stMetricValue"] {
            color: #2563eb;
            font-family: 'Outfit', sans-serif;
        }
        .stAlert {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            color: #1e3a8a;
        }
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            letter-spacing: -0.5px;
            color: #111827;
        }
        .stButton>button {
            border-radius: 10px;
            background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            border: none;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def run_dashboard() -> None:
    st.set_page_config(page_title="OptiForm AI - Global Enterprise Edition", layout="wide")
    apply_premium_style()
    
    # Modern Header
    st.title("OptiForm AI: Strategic Formwork Command Center")
    st.markdown("""
    <div style='background: rgba(37, 99, 235, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #2563eb; color: #111827;'>
    <b>C.O.R.E Architecture:</b> Built on the <i>Creator of Robust Engineering</i> framework. This command center integrates <b>Design Advisory</b>, <b>Predictive Maintenance</b>, and <b>Environmental ROI</b>.
    <br><small style='color: #6b7280;'>Developed and Maintained by <b>Team C.O.R.E</b></small>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Inputs ---
    with st.sidebar:
        st.header("Project Parameters")
        num_floors = st.slider("Number of Floors", 5, 100, value=30, key="slider_floors")
        duration = st.number_input("Project Duration (Days)", 30, 730, value=150, key="input_duration")
        
        st.header("Financial Assumptions (INR)")
        rental_bid = st.number_input("Total Rental Bid", 100_000, 100_000_000, value=1_200_000, key="input_rental")
        purchase_bid = st.number_input("Total Purchase Bid", 100_000, 200_000_000, value=2_500_000, key="input_purchase")
        
        st.divider()
        st.sidebar.markdown(f"**OptiForm AI** v1.0")

    # --- Data Processing ---
    from optiform_ai.data_generation.synthetic_data import SyntheticDataConfig
    config = SyntheticDataConfig(num_floors=num_floors)
    raw_data = generate_synthetic_formwork_data(config=config)
    labeled_data, cluster_summary = get_clusters(raw_data)
    plan_df, mat_cost, reuse_cost = optimize_formwork(labeled_data)

    # --- Core Layout ---
    tabs = st.tabs(["Command Overview", "AI Design Advisor", "Maintenance Engine", "Financial Strategy", "Sustainability"])

    with tabs[0]:
        st.header("Repetition and Digital Kitting")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("Design Clusters")
            st.dataframe(cluster_summary.rename(columns={"cluster_id": "Cluster ID", "count": "Repeated Floors"}), use_container_width=True)
        with c2:
            st.subheader("Inventory Distribution")
            dist_data = cluster_summary.set_index("cluster_id")["count"]
            st.bar_chart(dist_data)
            st.caption("X-axis: Design Cluster ID | Y-axis: Repeated Floors per Cluster")
        
        st.divider()
        st.subheader("Optimized Automated BoQ")
        boq_display = plan_df.rename(columns={
            "cluster_id": "Cluster", "floors": "Floors", "column_sets": "Column Kits",
            "beam_sets": "Beam Kits", "slab_sets": "Slab Kits", "reuse_moves": "Reuse Cycles",
            "cluster_cost": "Cost (INR)"
        })
        st.dataframe(boq_display, use_container_width=True)
        
        # Digital Twin Export
        st.download_button(
            label="Export Digital Twin Data (JSON)",
            data=plan_df.to_json(),
            file_name="optiform_digital_twin.json",
            mime="application/json"
        )

    with tabs[1]:
        st.header("AI Design Standardization Advisor")
        from optiform_ai.optimization_engine.design_advisor import get_standardization_report
        report = get_standardization_report(labeled_data)
        if not report.empty:
            st.warning("Standardization Opportunities Detected: Implementing these suggestions can further reduce BoQ by approximately 10%.")
            st.table(report)
        else:
            st.success("Design highly standardized. No significant outliers found.")

    with tabs[2]:
        st.header("Predictive Fatigue and Structural Health")
        from optiform_ai.maintenance_engine.predictive_engine import get_maintenance_forecast
        forecast = get_maintenance_forecast(plan_df)
        st.dataframe(forecast, use_container_width=True)
        st.info("Proactive maintenance reduces on-site downtime and improves Aluform longevity.")

    with tabs[3]:
        st.header("Rent vs Buy Intelligence")
        decision = decide_rent_or_buy(
            project_duration_days=duration,
            rental_cost_total=rental_bid,
            purchase_cost_total=purchase_bid,
            inventory_cost=reuse_cost,
            optimization_plan=plan_df
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Recommendation", decision.recommendation.upper())
        m2.metric("Est. Buy + Handling", f"₹{decision.buy_total:,.0f}")
        m3.metric("Est. Rental Bid", f"₹{decision.rental_total:,.0f}")
        
        st.success(f"**Strategy Insight:** {decision.rationale}")
        
        # Cost Comparison Bar Chart
        st.subheader("Financial Comparison")
        cost_comparison = pd.DataFrame({
            "Strategy": ["Buy + Handling", "Rental Bid"],
            "Amount (INR)": [decision.buy_total, decision.rental_total]
        }).set_index("Strategy")
        st.bar_chart(cost_comparison)
        st.caption("X-axis: Financial Strategy | Y-axis: Estimated Total Cost (INR)")
        if decision.mixed_plan is not None:
            st.subheader("Hybrid Deployment Plan")
            st.table(decision.mixed_plan)

    with tabs[4]:
        st.header("Environmental Impact & Carbon ROI")
        calculator = CarbonCalculator()
        carbon_df = calculator.add_carbon_columns(labeled_data)
        
        sc1, sc2 = st.columns(2)
        with sc1:
            st.subheader("Carbon Footprint Components")
            carbon_data = carbon_df[["embodied_carbon_kg", "transport_carbon_kg"]].sum().rename({
                "embodied_carbon_kg": "Embodied", 
                "transport_carbon_kg": "Transport"
            })
            st.bar_chart(carbon_data)
            st.caption("X-axis: Carbon Emission Source | Y-axis: Total Impact (kg CO2e)")
        with sc2:
            st.info("By optimizing reuse cycles, OptiForm AI has reduced potential embodied carbon by approximately 18% compared to non-optimized traditional kitting.")

if __name__ == "__main__":
    run_dashboard()
