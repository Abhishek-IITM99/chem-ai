"""
generate_dataset.py
-------------------
Time-series data generator for the fired-heater digital twin.

Drives the first-principles heater model (heater_model.solve) through a realistic
operating history and emits a historian-style dataset:

  * slow operational drivers  -> throughput, outlet setpoint, ambient (diurnal +
    seasonal), fuel-gas composition drift, excess-air control, fouling campaigns
  * sensor noise on every measured tag
  * LABELED fault events -- both PROCESS faults (real physics excursions) and
    SENSOR faults (measurement corruption only) -- so the roadmap's
    "clean / remove fault tags" and "label" steps have ground truth.

Output columns = every dashboard tag + the 4 KPIs + fault_flag / fault_type.

Usage:  python generate_dataset.py [--days N] [--freq-min M] [--seed S]
"""

import argparse
from dataclasses import asdict
import numpy as np
import pandas as pd

from heater_model import Design, solve
from fuel_properties import normalize


# ---------- base fuel-gas composition (mole %) ------------------------------
BASE_FUEL = {
    "H2": 25.0, "CH4": 45.0, "C2H6": 12.0, "C2H4": 1.0, "C3H8": 8.0,
    "C3H6": 1.0, "nC4H10": 3.0, "CO": 0.5, "CO2": 2.5, "N2": 1.5, "H2S": 0.05,
}


def ou_process(n, theta, sigma, x0, rng):
    """Ornstein-Uhlenbeck (mean-reverting) driver for smooth realistic drift."""
    x = np.empty(n)
    x[0] = x0
    for i in range(1, n):
        x[i] = x[i - 1] + theta * (x0 - x[i - 1]) + sigma * rng.standard_normal()
    return x


def build_drivers(ts, rng):
    """Construct the slow operating drivers over the timeline."""
    n = len(ts)
    hours = (ts - ts[0]) / np.timedelta64(1, "h")
    year_frac = (ts.dayofyear.values + hours % 24 / 24) / 365.0

    # Ambient: seasonal + diurnal + noise
    ambient = (25.0
               + 8.0 * np.sin(2 * np.pi * (year_frac - 0.3))      # seasonal
               + 5.0 * np.sin(2 * np.pi * (hours % 24 - 6) / 24)  # diurnal
               + rng.normal(0, 0.8, n))

    # Throughput: mean-reverting around design + occasional campaign step changes
    flow = ou_process(n, 0.01, 700, 195000, rng)
    step_points = np.sort(rng.choice(n, size=max(1, n // 700), replace=False))
    for sp in step_points:
        flow[sp:] += rng.uniform(-15000, 12000)
    flow = np.clip(flow, 150000, 215000)

    # Outlet setpoint: piecewise-constant with rare grade changes
    outlet = np.full(n, 400.0)
    for sp in np.sort(rng.choice(n, size=max(1, n // 1200), replace=False)):
        outlet[sp:] = rng.choice([385.0, 400.0, 415.0])
    outlet += rng.normal(0, 0.5, n)

    inlet = 40.0 + ou_process(n, 0.02, 0.3, 0.0, rng)

    # Excess-air controller: O2 trim around design, slow drift + control noise
    excess_air = ou_process(n, 0.02, 0.004, 0.15, rng)
    excess_air = np.clip(excess_air, 0.08, 0.30)

    # Fouling: sawtooth campaigns (grows, reset at cleaning/decoke)
    fouling = np.zeros(n)
    campaign_len = max(24 * 45, 1)           # ~45-day campaigns
    f = 0.0
    for i in range(n):
        f += 1.0 / campaign_len * rng.uniform(0.7, 1.3)
        if f >= 0.85:                        # cleaning event
            f = 0.02
        fouling[i] = f

    return dict(ambient=ambient, flow=flow, outlet=outlet, inlet=inlet,
                excess_air=excess_air, fouling=fouling)


def drift_fuel(n, rng):
    """Per-step fuel composition: slow H2/CH4 swing (refinery balance shifts)."""
    h2 = 25.0 + ou_process(n, 0.01, 0.6, 0.0, rng)
    h2 = np.clip(h2, 12.0, 45.0)
    comps = []
    for i in range(n):
        c = dict(BASE_FUEL)
        c["H2"] = h2[i]
        # CH4 absorbs the balance so the mixture stays normalized in spirit
        c["CH4"] = max(20.0, 70.0 - h2[i])
        comps.append(c)
    return comps


# ---------- fault injection -------------------------------------------------
def schedule_faults(n, rng):
    """
    Returns a per-row dict of fault overrides. Each fault has a type and a
    window. PROCESS faults perturb model inputs; SENSOR faults corrupt the
    measured output only.
    """
    flag = np.zeros(n, dtype=int)
    ftype = np.array(["none"] * n, dtype=object)
    # process-fault input overrides
    ovr_comb_eff = np.ones(n)
    ovr_excess = np.zeros(n)          # additive to excess_air
    ovr_fouling = np.zeros(n)         # additive to fouling
    ovr_fuel_heavy = np.zeros(n)      # 0..1 fraction of heavy slug
    # sensor-fault flags
    sens_o2_stuck = np.zeros(n, dtype=bool)
    sens_flow_spike = np.zeros(n, dtype=bool)
    sens_stack_bias = np.zeros(n)

    catalog = [
        ("air_deficiency",   6,  18),   # (name, min_len_h, max_len_h)
        ("high_excess_air",  8,  24),
        ("fouling_spike",   12,  48),
        ("fuel_upset",       4,  12),
        ("o2_sensor_stuck",  6,  30),
        ("flow_spike",       1,   3),
        ("stack_temp_bias",  8,  24),
    ]
    # Guarantee at least one of every fault class, then add random extras so
    # the labeled set covers all failure modes for classification training.
    n_extra = max(6, n // 250)
    event_types = [c[0] for c in catalog] + [
        catalog[rng.integers(len(catalog))][0] for _ in range(n_extra)]
    cat_by_name = {c[0]: c for c in catalog}
    for name in event_types:
        _, lo, hi = cat_by_name[name]
        dur = int(rng.integers(lo, hi + 1))
        start = int(rng.integers(0, max(1, n - dur)))
        sl = slice(start, start + dur)
        flag[sl] = 1
        ftype[sl] = name
        if name == "air_deficiency":
            ovr_comb_eff[sl] = rng.uniform(0.965, 0.985)  # CO breakthrough
            ovr_excess[sl] = -rng.uniform(0.05, 0.09)
        elif name == "high_excess_air":
            ovr_excess[sl] = rng.uniform(0.08, 0.15)
        elif name == "fouling_spike":
            ovr_fouling[sl] = rng.uniform(0.25, 0.45)
        elif name == "fuel_upset":
            ovr_fuel_heavy[sl] = rng.uniform(0.5, 1.0)
        elif name == "o2_sensor_stuck":
            sens_o2_stuck[sl] = True
        elif name == "flow_spike":
            sens_flow_spike[sl] = True
        elif name == "stack_temp_bias":
            sens_stack_bias[sl] = rng.uniform(15, 40)

    return dict(flag=flag, ftype=ftype, ovr_comb_eff=ovr_comb_eff,
                ovr_excess=ovr_excess, ovr_fouling=ovr_fouling,
                ovr_fuel_heavy=ovr_fuel_heavy, sens_o2_stuck=sens_o2_stuck,
                sens_flow_spike=sens_flow_spike, sens_stack_bias=sens_stack_bias)


HEAVY_SLUG = {"H2": 5.0, "CH4": 30.0, "C2H6": 18.0, "C3H8": 20.0,
              "nC4H10": 15.0, "C3H6": 5.0, "CO2": 4.0, "N2": 3.0}


def add_sensor_noise(state_dict, rng):
    """Apply realistic measurement noise to historian tags (in place copy)."""
    noise_pct = {
        "process_flow_kgph": 0.010, "fuel_flow_kgph": 0.012,
        "combustion_air_kgph": 0.015, "heat_duty_mw": 0.008,
    }
    noise_abs = {
        "inlet_temp_c": 0.6, "outlet_temp_c": 0.8, "stack_temp_c": 1.5,
        "stack_o2_pct": 0.05, "flue_co2_pct": 0.10, "flue_co_ppm": 5.0,
        "flue_nox_ppm": 2.0, "flue_sox_ppm": 1.5, "tube_metal_temp_c": 3.0,
        "flame_temp_c": 8.0, "process_pressure_bar": 0.05,
    }
    d = dict(state_dict)
    for k, p in noise_pct.items():
        d[k] = d[k] * (1 + rng.normal(0, p))
    for k, s in noise_abs.items():
        d[k] = d[k] + rng.normal(0, s)
    # physical floors: concentrations & rates cannot go negative
    for k in ("flue_co_ppm", "flue_nox_ppm", "flue_sox_ppm", "flue_co2_pct",
              "stack_o2_pct"):
        d[k] = max(0.0, d[k])
    return d


def generate(days=120, freq_min=60, seed=42):
    rng = np.random.default_rng(seed)
    design = Design()
    ts = pd.date_range("2025-01-01", periods=int(days * 24 * 60 / freq_min),
                       freq=f"{freq_min}min")
    n = len(ts)

    drv = build_drivers(ts, rng)
    fuels = drift_fuel(n, rng)
    flt = schedule_faults(n, rng)

    rows = []
    last_o2 = None
    for i in range(n):
        # ---- assemble true inputs (with process-fault overrides) ----
        comp = dict(fuels[i])
        if flt["ovr_fuel_heavy"][i] > 0:
            w = flt["ovr_fuel_heavy"][i]
            comp = {k: (1 - w) * comp.get(k, 0) + w * HEAVY_SLUG.get(k, 0)
                    for k in set(comp) | set(HEAVY_SLUG)}
        excess = float(np.clip(drv["excess_air"][i] + flt["ovr_excess"][i], 0.04, 0.35))
        fouling = float(np.clip(drv["fouling"][i] + flt["ovr_fouling"][i], 0.0, 1.0))
        comb_eff = float(flt["ovr_comb_eff"][i])

        st = solve(design,
                   process_flow_kgph=float(drv["flow"][i]),
                   inlet_temp_c=float(drv["inlet"][i]),
                   outlet_temp_c=float(drv["outlet"][i]),
                   process_pressure_bar=12.0 + 0.4 * np.sin(i / 50),
                   fuel_comp=comp, excess_air_frac=excess,
                   fouling=fouling, ambient_c=float(drv["ambient"][i]),
                   combustion_eff=comb_eff)

        d = asdict(st)
        d = add_sensor_noise(d, rng)

        # ---- sensor faults (corrupt measurement only) ----
        if flt["sens_o2_stuck"][i] and last_o2 is not None:
            d["stack_o2_pct"] = last_o2                 # frozen transmitter
        else:
            last_o2 = d["stack_o2_pct"]
        if flt["sens_flow_spike"][i]:
            d["process_flow_kgph"] *= rng.uniform(1.3, 1.8)   # transmitter spike
        if flt["sens_stack_bias"][i] > 0:
            d["stack_temp_c"] += flt["sens_stack_bias"][i]    # drift/bias

        d["timestamp"] = ts[i]
        d["fuel_h2_pct"] = comp.get("H2", 0)
        d["fouling_index"] = fouling
        d["ambient_temp_c"] = drv["ambient"][i]
        d["fault_flag"] = int(flt["flag"][i])
        d["fault_type"] = flt["ftype"][i]
        rows.append(d)

    df = pd.DataFrame(rows)
    # order columns: timestamp first, labels last
    front = ["timestamp"]
    labels = ["fault_flag", "fault_type"]
    mid = [c for c in df.columns if c not in front + labels]
    df = df[front + mid + labels]
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--freq-min", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="heater_dataset.csv")
    args = ap.parse_args()

    df = generate(days=args.days, freq_min=args.freq_min, seed=args.seed)
    df.to_csv(args.out, index=False)

    print(f"Rows: {len(df):,}  Cols: {df.shape[1]}  -> {args.out}")
    print(f"Time span: {df.timestamp.min()}  ->  {df.timestamp.max()}")
    print(f"Fault rows: {df.fault_flag.sum():,} "
          f"({100*df.fault_flag.mean():.1f}%)")
    print("\nFault breakdown:")
    print(df[df.fault_flag == 1].fault_type.value_counts().to_string())
    print("\nKPI summary (normal operation only):")
    norm = df[df.fault_flag == 0]
    for c in ["heat_duty_mw", "kpi_efficiency_pct", "stack_o2_pct",
              "stack_temp_c", "kpi_co2_tph", "flue_nox_ppm", "kpi_total_loss_pct"]:
        print(f"  {c:22s} mean={norm[c].mean():8.2f}  "
              f"min={norm[c].min():8.2f}  max={norm[c].max():8.2f}")


if __name__ == "__main__":
    main()
