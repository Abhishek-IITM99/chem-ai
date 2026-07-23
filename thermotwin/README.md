# Fired-Heater First-Principles Data Generator

Synthetic-but-physical dataset for the **fired-heater digital twin** (roadmap:
Collect → Clean → Label → *foundation model based on first principles* → Train →
Validate → Deploy). Since there is no plant historian yet, this replaces the
"Collect Data" step with a first-principles simulation that is internally
consistent (energy balance closes to machine precision) and reproduces the
KPI formulas defined in `HEATER KPIs.xlsx`.

## Files

| File | Purpose |
|------|---------|
| `fuel_properties.py` | Fuel-gas thermochemistry: LHV/HHV, MW, density, Wobbe, stoichiometric air, full flue-gas combustion balance. Pure first principles from atomic makeup + heats of combustion. |
| `heater_model.py` | Steady-state heater energy balance for one instant → all tags + 4 KPIs. |
| `generate_dataset.py` | Drives the model through a realistic operating history with drift + **labeled faults** → `heater_dataset.csv`. |
| `twin_pipeline.py` | Clean → Label → Train → Validate. Fits the surrogate "twin", reports R²/MAE/MAPE, saves `models/` + `artifacts/metrics.json`. |
| `optimize.py` | Operating-point optimizer: finds the tightest safe excess-air setpoint, reports fuel/CO2 savings → `artifacts/optimization.json`. |
| `make_charts.py` | Renders the validation + optimization charts (`artifacts/chart_*.png`) used in the deck. |
| `dashboard.py` | Streamlit live demo (Deploy step). `streamlit run dashboard.py`. |
| `hub71_deck.html` | Self-contained Hub71 pitch deck (charts embedded), published as an Artifact. |
| `heater_dataset.csv` | The generated historian-style dataset (default 120 days hourly = 2,880 rows). |
| `DATA_DICTIONARY.md` | Every column: meaning, units, source formula. |

## Run the whole project, in order

```bash
python generate_dataset.py     # 1. Collect  -> heater_dataset.csv
python twin_pipeline.py        # 2. Clean/Label/Train/Validate -> models/, artifacts/metrics.json
python optimize.py             # 3. Optimize -> artifacts/optimization.json
python make_charts.py          # 4. Charts   -> artifacts/chart_*.png
streamlit run dashboard.py     # 5. Deploy   -> live demo
```

## Results (seed 42, 120-day hourly set)

- **Twin accuracy** (25 % hold-out): R² 0.96–0.99, MAPE under 1.6 % across efficiency,
  CO2, stack temperature, stack O2, tube-metal temperature and fuel firing.
- **Cleaning**: 2,880 raw rows, 105 sensor-fault rows removed, 2,775 clean
  (126 real process-fault rows kept).
- **Optimization**: 24 % excess air (O2 4.4 %) → 10 % (O2 2.1 %), efficiency
  +2.49 points, fuel −2.71 %, CO2 −2,560 t/yr, ~$376k/yr per heater at
  6 USD/GJ fuel and 40 USD/t CO2.

## Run

```bash
python generate_dataset.py --days 120 --freq-min 60 --seed 42
# larger, minute-resolution set:
python generate_dataset.py --days 60 --freq-min 5 --seed 7 --out heater_5min.csv
```

Dependencies: `numpy`, `pandas` (already installed).

## What makes it "first principles" (not just random numbers)

1. **Heat duty** `Q = ṁ · Cp · ΔT` — process energy demand.
2. **Fuel properties** derived from molar composition + per-component heats of
   combustion and atomic C/H/S (no lookup of bulk LHV).
3. **Combustion balance** — stoichiometric O₂ from `CxHySz + (x+y/4+z)O₂ →
   xCO₂ + (y/2)H₂O + zSO₂`, then excess air sets flue O₂, CO₂, N₂, H₂O.
4. **Efficiency** — indirect stack-loss method, the exact workbook correlation
   (reproduces the sheet's 92.397 % at O₂=2.5, T_stack=150).
5. **Fuel firing** back-solved so `fuel_energy × efficiency = duty` (balance
   closes to ~1e-13 GJ/h).
6. **Flame temperature** from a first-law adiabatic estimate; **thermal NOx**
   from a Zeldovich-style dependence on flame temperature.

## Operating dynamics in the timeline

- Throughput drift + campaign step changes; outlet-temperature grade changes.
- Fuel-gas composition swing (H₂ 12–45 %, CH₄ balancing) — the "dynamic input"
  the workbook flags as most influential.
- Excess-air/O₂-trim control drift; **fouling campaigns** (grow then reset at a
  cleaning/decoke event); diurnal + seasonal ambient.

## Labeled faults (ground truth for Clean + Label steps)

| `fault_type` | Kind | Signature in data |
|--------------|------|-------------------|
| `air_deficiency` | process | CO breaks through (↑↑ `flue_co_ppm`), O₂ ↓ |
| `high_excess_air` | process | efficiency ↓, stack loss ↑ |
| `fouling_spike` | process | `stack_temp_c` ↑, efficiency ↓ |
| `fuel_upset` | process | heavy-gas slug → `fuel_lhv_mjkg` ↓, Wobbe shift |
| `o2_sensor_stuck` | sensor | `stack_o2_pct` frozen (measurement only) |
| `flow_spike` | sensor | `process_flow_kgph` transient spike |
| `stack_temp_bias` | sensor | `stack_temp_c` offset/drift |

`fault_flag` (0/1) and `fault_type` are the labels. **Process** faults are real
physics excursions the twin must learn; **sensor** faults are the bad tags the
"clean / remove fault tags" step should detect and discard.

## Typical value ranges (normal operation)

| Quantity | Range | Sanity target |
|----------|-------|---------------|
| Heat duty | 39–53 MW | mid-size process heater |
| Efficiency | 89–93 % | workbook 85–92 % |
| Stack O₂ | ~1.8–4.0 % | 2–4 % |
| Stack temp | 140–210 °C | 150–250 °C |
| CO₂ | ~9–12 t/h | factor 56.1 kg/GJ |
| NOx | ~40–115 ppm | low-NOx gas firing |
