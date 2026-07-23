# Data Dictionary — `heater_dataset.csv`

One row = one timestamp of heater operation. Columns grouped by role. "Source"
notes whether the value is an operating **driver** (independent input), a
first-principles **derived** quantity, or a workbook **KPI**.

| Column | Units | Source | Description |
|--------|-------|--------|-------------|
| `timestamp` | — | index | Hourly (default) time index. |
| **Process side** |||
| `process_flow_kgph` | kg/h | driver | Process-fluid mass flow (what is being heated). |
| `inlet_temp_c` | °C | driver | Process inlet temperature. |
| `outlet_temp_c` | °C | driver | Process outlet (coil outlet) temperature setpoint. |
| `process_pressure_bar` | bar | driver | Process operating pressure. |
| `heat_duty_mw` | MW | derived | `Q = ṁ·Cp·ΔT`, the required heat duty. |
| `heat_duty_gjph` | GJ/h | derived | Same duty in GJ/h (= MW × 3.6). |
| **Fuel side** |||
| `fuel_lhv_mjkg` | MJ/kg | derived | Lower heating value from composition. |
| `fuel_hhv_mjkg` | MJ/kg | derived | Higher heating value (water latent added). |
| `fuel_mw` | g/mol | derived | Fuel-gas molecular weight. |
| `fuel_wobbe` | MJ/Nm³ | derived | Wobbe index (burner interchangeability). |
| `fuel_flow_kgph` | kg/h | derived | Fuel firing rate to meet duty at efficiency. |
| `fuel_energy_gjph` | GJ/h | derived | Fuel energy input = duty / efficiency. |
| `fuel_h2_pct` | mol% | driver | H₂ in the fuel gas (the key dynamic input). |
| **Combustion / air** |||
| `excess_air_pct` | % | driver | Excess air above stoichiometric. |
| `stoich_air_kgph` | kg/h | derived | Stoichiometric combustion-air demand. |
| `combustion_air_kgph` | kg/h | derived | Actual combustion air = stoich × (1+EA). |
| `stack_o2_pct` | %dry | derived | Flue-gas O₂ (dry) — drives the efficiency KPI. |
| `flue_co2_pct` | %dry | derived | Flue-gas CO₂ (dry). |
| `flue_co_ppm` | ppm | derived | CO — spikes on incomplete combustion. |
| `flue_nox_ppm` | ppm | derived | Thermal NOx (flame-temperature driven). |
| `flue_sox_ppm` | ppm | derived | SOx from fuel sulfur (H₂S). |
| **Heat transfer** |||
| `radiant_duty_mw` | MW | derived | Radiant-section duty (~70 % of total). |
| `convection_duty_mw` | MW | derived | Convection-section duty (waste-heat recovery). |
| `flame_temp_c` | °C | derived | Adiabatic-flame-temperature estimate. |
| `tube_metal_temp_c` | °C | derived | Tube skin / metal temperature (constraint). |
| `stack_temp_c` | °C | derived | Flue-gas stack temperature. |
| **KPIs (dashboard targets)** |||
| `kpi_efficiency_pct` | % | KPI | Indirect efficiency (workbook correlation). |
| `kpi_co2_tph` | t/h | KPI | CO₂ = fuel_energy × 56.1 kg/GJ. |
| `kpi_stack_loss_pct` | % | KPI | Stack (flue-gas) heat loss. |
| `kpi_total_loss_pct` | % | KPI | Stack + refractory (2 %) + unaccounted (2.5 %). |
| **Context / labels** |||
| `fouling_index` | 0–1 | driver | Convection-fouling state (0 clean → 1 fouled). |
| `ambient_temp_c` | °C | driver | Ambient air temperature. |
| `fault_flag` | 0/1 | label | 1 during any injected fault window. |
| `fault_type` | text | label | Fault class (see README) or `none`. |

## Notes for the modeling team

- **Targets for the twin**: the 4 `kpi_*` columns (+ `stack_o2_pct`,
  `stack_temp_c`, `tube_metal_temp_c`) are natural prediction targets.
- **Inputs/features**: process-side drivers + fuel composition + excess air +
  fouling + ambient are the independent variables.
- **Clean step**: drop/repair rows where `fault_type` ∈ {sensor faults}
  (`o2_sensor_stuck`, `flow_spike`, `stack_temp_bias`) — these are bad tags, not
  real physics. Keep process faults; they are legitimate operating states.
- **Validate step**: because the generator's energy balance is exact, a trained
  surrogate can be scored on physics residuals (duty vs fuel_energy×η), not just
  point error.
