"""
dashboard.py
------------
ThermoTwin live demo (roadmap step: Deploy). Streamlit app that runs the
first-principles heater twin in real time, shows the KPI dashboard defined in
HEATER KPIs.xlsx, and recommends the optimal excess-air setpoint with the fuel
and CO2 savings it unlocks.

Run:  streamlit run dashboard.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from heater_model import Design, solve
from optimize import (optimize_point, evaluate, savings,
                      combustion_eff_from_excess_air)

HERE = Path(__file__).parent
st.set_page_config(page_title="ThermoTwin | Fired-Heater Digital Twin",
                   layout="wide", page_icon="🔥")

BLUE, ORANGE = "#1D4ED8", "#EA580C"

st.title("ThermoTwin — Fired-Heater Digital Twin")
st.caption("First-principles twin + optimizer. Move an input and every KPI, "
           "emission and setpoint recommendation updates live.")

# ---------------- sidebar: operating inputs ----------------
st.sidebar.header("Operating conditions")
flow = st.sidebar.slider("Process flow (kg/h)", 150000, 215000, 195000, 1000)
inlet = st.sidebar.slider("Inlet temperature (°C)", 20, 120, 40, 1)
outlet = st.sidebar.slider("Outlet temperature (°C)", 350, 450, 400, 1)
pressure = st.sidebar.slider("Process pressure (bar)", 5, 30, 12, 1)
st.sidebar.header("Fuel gas")
h2 = st.sidebar.slider("Hydrogen H₂ (mol %)", 12, 45, 25, 1)
st.sidebar.header("Combustion & condition")
excess_air = st.sidebar.slider("Excess air (%)", 4, 30, 24, 1) / 100.0
fouling = st.sidebar.slider("Fouling index (0 clean → 1 fouled)",
                            0.0, 1.0, 0.25, 0.05)
ambient = st.sidebar.slider("Ambient (°C)", 0, 50, 25, 1)

fuel = {"H2": h2, "CH4": max(20.0, 70.0 - h2), "C2H6": 12, "C3H8": 8,
        "nC4H10": 3, "CO2": 2.5, "N2": 1.5, "H2S": 0.05}
design = Design()
base = {"flow": flow, "inlet": inlet, "outlet": outlet, "pressure": pressure,
        "fuel": fuel, "fouling": fouling, "ambient": ambient}

st_now = evaluate(design, base, excess_air)      # uses CO-vs-air physics
(opt_ea, opt_state), sweep = optimize_point(design, base)
sav = savings(st_now, opt_state)

# ---------------- KPI row ----------------
st.subheader("Live KPIs")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Heat duty", f"{st_now.heat_duty_mw:.1f} MW")
c2.metric("Efficiency", f"{st_now.kpi_efficiency_pct:.2f} %")
c3.metric("Fuel firing", f"{st_now.fuel_flow_kgph:,.0f} kg/h")
c4.metric("CO₂", f"{st_now.kpi_co2_tph:.2f} t/h")
c5.metric("Stack O₂", f"{st_now.stack_o2_pct:.2f} %")
c6.metric("Stack temp", f"{st_now.stack_temp_c:.0f} °C")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tube metal temp", f"{st_now.tube_metal_temp_c:.0f} °C")
c2.metric("Flue CO", f"{st_now.flue_co_ppm:.0f} ppm")
c3.metric("NOx", f"{st_now.flue_nox_ppm:.0f} ppm")
c4.metric("Total losses", f"{st_now.kpi_total_loss_pct:.2f} %")

# ---------------- optimizer recommendation ----------------
st.subheader("Optimizer recommendation")
oc1, oc2 = st.columns([1, 1])
with oc1:
    st.markdown(
        f"**Current:** {excess_air*100:.0f}% excess air "
        f"(O₂ {st_now.stack_o2_pct:.2f}%), efficiency "
        f"{st_now.kpi_efficiency_pct:.2f}%")
    st.markdown(
        f"**Recommended:** {opt_ea*100:.0f}% excess air "
        f"(O₂ {opt_state.stack_o2_pct:.2f}%), efficiency "
        f"{opt_state.kpi_efficiency_pct:.2f}%")
    if sav["fuel_pct_saved"] > 0.05:
        st.success(
            f"Cut excess air to save {sav['fuel_pct_saved']:.1f}% fuel "
            f"({sav['fuel_gjph_saved']:.2f} GJ/h) and avoid "
            f"{sav['co2_tph_saved']:.2f} t/h CO₂ "
            f"(~{sav['co2_tpy_saved']:,.0f} t/yr). Combined value "
            f"~${sav['fuel_usd_per_year']+sav['co2_usd_per_year']:,.0f}/yr "
            f"for this one heater.")
    else:
        st.info("Already at or near the safe optimum for these conditions.")
with oc2:
    sw = pd.DataFrame([
        {"Excess air (%)": ea * 100, "Efficiency (%)": s.kpi_efficiency_pct}
        for ea, s, ok in sweep])
    st.line_chart(sw, x="Excess air (%)", y="Efficiency (%)", height=260)

# ---------------- historical view ----------------
st.subheader("Historian view (generated first-principles data)")
csv = HERE / "heater_dataset.csv"
if csv.exists():
    df = pd.read_csv(csv, parse_dates=["timestamp"])
    tag = st.selectbox("Tag", ["kpi_efficiency_pct", "stack_temp_c",
                               "kpi_co2_tph", "stack_o2_pct", "flue_co_ppm",
                               "fuel_flow_kgph", "tube_metal_temp_c"])
    show = df.set_index("timestamp")[[tag]]
    st.line_chart(show, height=260)
    faults = df[df.fault_flag == 1]["fault_type"].value_counts()
    st.caption(f"{len(df):,} rows · {int(df.fault_flag.sum())} labelled "
               f"fault rows across {faults.size} classes: "
               f"{', '.join(faults.index)}")
else:
    st.info("Run generate_dataset.py to populate the historian view.")

st.divider()
st.caption("ThermoTwin · physics-first cold start, self-learning once plant "
           "data is connected · trio team")
