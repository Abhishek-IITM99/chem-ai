"""
twin_pipeline.py
----------------
Roadmap steps Clean -> Label -> Train -> Validate for the fired-heater twin.

Takes the first-principles dataset (heater_dataset.csv) and:
  1. CLEAN  : drop rows whose measurements are corrupted by SENSOR faults
              (o2_sensor_stuck, flow_spike, stack_temp_bias). Process faults
              are kept because they are real operating states.
  2. LABEL  : keep fault_flag / fault_type as supervised labels.
  3. TRAIN  : fit a surrogate ("digital twin") that predicts heater response
              (efficiency, stack temperature, stack O2, CO2, tube-metal temp,
              fuel firing) from the controllable + disturbance inputs.
  4. VALIDATE: hold-out test set, report R2 / MAE / RMSE per target, save
              real-vs-predicted charts and a metrics file for the deck.

Outputs land in ./artifacts and ./models.
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

HERE = Path(__file__).parent
ART = HERE / "artifacts"
MODELS = HERE / "models"
ART.mkdir(exist_ok=True)
MODELS.mkdir(exist_ok=True)

SENSOR_FAULTS = {"o2_sensor_stuck", "flow_spike", "stack_temp_bias"}

# Inputs the operator sets or the plant imposes (controls + disturbances)
FEATURES = [
    "process_flow_kgph", "inlet_temp_c", "outlet_temp_c", "process_pressure_bar",
    "excess_air_pct", "fuel_h2_pct", "fuel_lhv_mjkg", "fouling_index",
    "ambient_temp_c",
]
# Heater response the twin learns to predict
TARGETS = [
    "kpi_efficiency_pct", "stack_temp_c", "stack_o2_pct", "kpi_co2_tph",
    "tube_metal_temp_c", "fuel_flow_kgph",
]

TARGET_LABELS = {
    "kpi_efficiency_pct": "Efficiency (%)",
    "stack_temp_c": "Stack temperature (C)",
    "stack_o2_pct": "Stack O2 (%)",
    "kpi_co2_tph": "CO2 (t/h)",
    "tube_metal_temp_c": "Tube metal temp (C)",
    "fuel_flow_kgph": "Fuel firing (kg/h)",
}


def clean(df: pd.DataFrame):
    """Remove sensor-fault rows; return cleaned frame and a cleaning report."""
    n0 = len(df)
    is_sensor = df["fault_type"].isin(SENSOR_FAULTS)
    cleaned = df.loc[~is_sensor].copy()
    report = {
        "rows_raw": int(n0),
        "rows_removed_sensor_faults": int(is_sensor.sum()),
        "rows_clean": int(len(cleaned)),
        "process_fault_rows_kept": int(
            ((cleaned["fault_flag"] == 1)).sum()),
        "removed_by_type": df.loc[is_sensor, "fault_type"]
            .value_counts().to_dict(),
    }
    return cleaned, report


def train_validate(df: pd.DataFrame, seed: int = 42):
    X = df[FEATURES].values
    results = {}
    preds = {}
    models = {}
    idx_train, idx_test = train_test_split(
        np.arange(len(df)), test_size=0.25, random_state=seed, shuffle=True)

    for tgt in TARGETS:
        y = df[tgt].values
        model = RandomForestRegressor(
            n_estimators=250, max_depth=None, min_samples_leaf=2,
            n_jobs=-1, random_state=seed)
        model.fit(X[idx_train], y[idx_train])
        yhat = model.predict(X[idx_test])
        rmse = float(np.sqrt(mean_squared_error(y[idx_test], yhat)))
        results[tgt] = {
            "r2": float(r2_score(y[idx_test], yhat)),
            "mae": float(mean_absolute_error(y[idx_test], yhat)),
            "rmse": rmse,
            "target_mean": float(np.mean(y[idx_test])),
            "mape_pct": float(np.mean(np.abs((y[idx_test] - yhat)
                              / np.clip(np.abs(y[idx_test]), 1e-6, None))) * 100),
            "importances": dict(sorted(
                zip(FEATURES, model.feature_importances_.tolist()),
                key=lambda kv: kv[1], reverse=True)),
        }
        preds[tgt] = {"y": y[idx_test], "yhat": yhat}
        models[tgt] = model
        joblib.dump(model, MODELS / f"twin_{tgt}.joblib")

    return results, preds, models, (idx_train, idx_test)


def main():
    df = pd.read_csv(HERE / "heater_dataset.csv", parse_dates=["timestamp"])
    cleaned, report = clean(df)
    results, preds, models, split = train_validate(cleaned)

    # persist predictions for the charting script
    np.savez(ART / "test_predictions.npz",
             **{f"{t}_y": preds[t]["y"] for t in TARGETS},
             **{f"{t}_yhat": preds[t]["yhat"] for t in TARGETS})

    out = {"cleaning": report,
           "features": FEATURES,
           "targets": TARGETS,
           "metrics": results,
           "n_train": int(len(split[0])),
           "n_test": int(len(split[1]))}
    with open(ART / "metrics.json", "w") as f:
        json.dump(out, f, indent=2)

    # console summary
    print("CLEAN / LABEL")
    print(f"  raw rows           : {report['rows_raw']:,}")
    print(f"  sensor-fault rows  : {report['rows_removed_sensor_faults']:,} "
          f"removed  {report['removed_by_type']}")
    print(f"  clean rows         : {report['rows_clean']:,} "
          f"(process-fault rows kept: {report['process_fault_rows_kept']})")
    print(f"\nTRAIN / VALIDATE  (train={out['n_train']}, test={out['n_test']})")
    print(f"  {'target':22s} {'R2':>7s} {'MAE':>10s} {'MAPE%':>8s}")
    for t in TARGETS:
        m = results[t]
        print(f"  {TARGET_LABELS[t]:22s} {m['r2']:7.4f} "
              f"{m['mae']:10.3f} {m['mape_pct']:7.2f}%")
    print(f"\nSaved -> {ART/'metrics.json'}, models in {MODELS}/")


if __name__ == "__main__":
    main()
