"""
optimize.py
-----------
Operating-point optimizer for the fired heater. This is the value layer: for a
fixed heat demand and fuel, it finds the excess-air setpoint that minimises fuel
firing (and therefore CO2) without crossing the combustion or corrosion limits.

The trade-off is physical:
  * too much excess air -> extra flue-gas mass carries heat up the stack -> loss
  * too little excess air -> incomplete combustion -> CO breakthrough, lost fuel

Most heaters run rich in air for a safety margin (measured O2 ~4-5 %). The twin
recommends the tightest safe air rate (O2 ~2 %), which recovers that margin as
fuel and CO2 savings.

Combustion-efficiency vs excess-air model
-----------------------------------------
Below the knee, a small carbon fraction escapes as CO:
    unburned_fraction = 0.03 * exp(-(EA - 0.03) / 0.025)
which reproduces negligible CO above ~12 % air and a sharp CO rise below ~8 %.
"""

import json
import math
from pathlib import Path

import numpy as np

from heater_model import Design, solve

HERE = Path(__file__).parent
ART = HERE / "artifacts"
ART.mkdir(exist_ok=True)

# constraints / economics
CO_LIMIT_PPM = 200.0        # combustion / safety limit
STACK_DEWPOINT_C = 130.0    # acid dew-point floor (corrosion)
TUBE_METAL_LIMIT_C = 620.0  # metallurgical limit
FUEL_PRICE_PER_GJ = 6.0     # USD/GJ (refinery fuel gas, indicative)
CO2_PRICE_PER_T = 40.0      # USD/t CO2 (carbon cost, indicative)
HOURS_PER_YEAR = 8400.0     # ~96 % availability


def combustion_eff_from_excess_air(ea: float) -> float:
    unburned = 0.03 * math.exp(-(ea - 0.03) / 0.025)
    return 1.0 - min(unburned, 0.05)


def evaluate(design, base, ea):
    """Solve the heater at excess-air fraction `ea` for a base operating point."""
    return solve(design,
                 process_flow_kgph=base["flow"],
                 inlet_temp_c=base["inlet"],
                 outlet_temp_c=base["outlet"],
                 process_pressure_bar=base["pressure"],
                 fuel_comp=base["fuel"],
                 excess_air_frac=ea,
                 fouling=base["fouling"],
                 ambient_c=base["ambient"],
                 combustion_eff=combustion_eff_from_excess_air(ea))


def feasible(st):
    return (st.flue_co_ppm <= CO_LIMIT_PPM
            and st.stack_temp_c >= STACK_DEWPOINT_C
            and st.tube_metal_temp_c <= TUBE_METAL_LIMIT_C)


def optimize_point(design, base, ea_grid=None):
    """Return the feasible excess air that minimises fuel firing."""
    if ea_grid is None:
        ea_grid = np.arange(0.04, 0.301, 0.002)
    sweep = []
    best = None
    for ea in ea_grid:
        st = evaluate(design, base, ea)
        ok = feasible(st)
        sweep.append((float(ea), st, ok))
        if ok and (best is None or st.fuel_energy_gjph < best[1].fuel_energy_gjph):
            best = (float(ea), st)
    return best, sweep


def savings(base_state, opt_state):
    fuel_gjph_saved = base_state.fuel_energy_gjph - opt_state.fuel_energy_gjph
    co2_tph_saved = base_state.kpi_co2_tph - opt_state.kpi_co2_tph
    return {
        "eff_gain_pts": opt_state.kpi_efficiency_pct - base_state.kpi_efficiency_pct,
        "fuel_gjph_saved": fuel_gjph_saved,
        "fuel_pct_saved": 100.0 * fuel_gjph_saved / base_state.fuel_energy_gjph,
        "co2_tph_saved": co2_tph_saved,
        "co2_tpy_saved": co2_tph_saved * HOURS_PER_YEAR,
        "fuel_usd_per_year": fuel_gjph_saved * HOURS_PER_YEAR * FUEL_PRICE_PER_GJ,
        "co2_usd_per_year": co2_tph_saved * HOURS_PER_YEAR * CO2_PRICE_PER_T,
    }


def main():
    design = Design()
    # A representative operating point currently run with a generous air margin.
    base = {
        "flow": 195000.0, "inlet": 40.0, "outlet": 400.0, "pressure": 12.0,
        "fuel": {"H2": 25, "CH4": 45, "C2H6": 12, "C3H8": 8, "nC4H10": 3,
                 "CO2": 2.5, "N2": 1.5, "H2S": 0.05},
        "fouling": 0.25, "ambient": 25.0,
    }
    # Baseline: operator runs at 24 % excess air (measured O2 ~4.3 %)
    baseline_ea = 0.24
    base_state = evaluate(design, base, baseline_ea)

    (opt_ea, opt_state), sweep = optimize_point(design, base)
    sav = savings(base_state, opt_state)

    # persist sweep + result for the deck / dashboard
    sweep_out = [{"excess_air_pct": ea * 100,
                  "efficiency_pct": st.kpi_efficiency_pct,
                  "fuel_gjph": st.fuel_energy_gjph,
                  "co_ppm": st.flue_co_ppm,
                  "stack_o2_pct": st.stack_o2_pct,
                  "feasible": bool(ok)}
                 for ea, st, ok in sweep]
    result = {
        "baseline": {"excess_air_pct": baseline_ea * 100,
                     "stack_o2_pct": base_state.stack_o2_pct,
                     "efficiency_pct": base_state.kpi_efficiency_pct,
                     "fuel_gjph": base_state.fuel_energy_gjph,
                     "co2_tph": base_state.kpi_co2_tph,
                     "co_ppm": base_state.flue_co_ppm},
        "optimized": {"excess_air_pct": opt_ea * 100,
                      "stack_o2_pct": opt_state.stack_o2_pct,
                      "efficiency_pct": opt_state.kpi_efficiency_pct,
                      "fuel_gjph": opt_state.fuel_energy_gjph,
                      "co2_tph": opt_state.kpi_co2_tph,
                      "co_ppm": opt_state.flue_co_ppm},
        "savings": sav,
        "assumptions": {"fuel_price_usd_per_gj": FUEL_PRICE_PER_GJ,
                        "co2_price_usd_per_t": CO2_PRICE_PER_T,
                        "hours_per_year": HOURS_PER_YEAR,
                        "co_limit_ppm": CO_LIMIT_PPM},
        "sweep": sweep_out,
    }
    with open(ART / "optimization.json", "w") as f:
        json.dump(result, f, indent=2)

    print("OPTIMIZATION  (single fired heater, one operating point)")
    print(f"  baseline : {baseline_ea*100:4.1f}% excess air  "
          f"O2={base_state.stack_o2_pct:4.2f}%  "
          f"eff={base_state.kpi_efficiency_pct:5.2f}%  "
          f"fuel={base_state.fuel_energy_gjph:6.2f} GJ/h")
    print(f"  optimal  : {opt_ea*100:4.1f}% excess air  "
          f"O2={opt_state.stack_o2_pct:4.2f}%  "
          f"eff={opt_state.kpi_efficiency_pct:5.2f}%  "
          f"fuel={opt_state.fuel_energy_gjph:6.2f} GJ/h")
    print(f"\n  efficiency gain   : {sav['eff_gain_pts']:+.2f} points")
    print(f"  fuel saved        : {sav['fuel_pct_saved']:.2f}%  "
          f"({sav['fuel_gjph_saved']:.2f} GJ/h)")
    print(f"  CO2 avoided       : {sav['co2_tph_saved']:.3f} t/h  "
          f"= {sav['co2_tpy_saved']:,.0f} t/yr")
    print(f"  fuel value/yr     : ${sav['fuel_usd_per_year']:,.0f}")
    print(f"  carbon value/yr   : ${sav['co2_usd_per_year']:,.0f}")
    print(f"  combined /yr/heater: "
          f"${sav['fuel_usd_per_year']+sav['co2_usd_per_year']:,.0f}")
    print(f"\nSaved -> {ART/'optimization.json'}")


if __name__ == "__main__":
    main()
