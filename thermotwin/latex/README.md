# ThermoTwin Technical Reference (LaTeX)

A self-contained LaTeX report stating every equation used in the project, the
assumptions behind them, and how the pieces fit together, so a new reader can
follow the work from combustion chemistry to the final fuel and carbon savings.

## Contents

| File | Purpose |
|------|---------|
| `main.tex` | The full source (13 pages). |
| `ThermoTwin_Technical_Reference.pdf` | The compiled report. |
| `figures/` | Charts pulled from `../artifacts` (accuracy, sweep, time series, real-vs-predicted). |

## What the report covers

1. What the project does and the roadmap it follows.
2. Fuel-gas thermochemistry: heating values, molar mass, density, Wobbe index, stoichiometric air, with the per-component data table.
3. Combustion product balance: excess air, flue-gas oxygen, carbon dioxide, carbon monoxide, sulfur dioxide.
4. Steady-state heater model: heat duty, stack temperature, flame temperature, thermal nitrogen oxides, the efficiency correlation, fuel firing, heat split, tube metal temperature, emissions.
5. The four dashboard KPIs and their governing equations.
6. Time-series data generation: drivers, fault classes, measurement noise.
7. The machine-learning twin: clean, label, features, targets, accuracy table.
8. Operating-point optimization: the carbon-monoxide trade-off, objective, constraints, savings and economics.
9. Reproducibility: constants, code map, run order, assumptions and limits.

## Rebuild the PDF

Requires a LaTeX distribution (MiKTeX or TeX Live). Run twice so the table of
contents and cross-references resolve:

```bash
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Or with latexmk:

```bash
latexmk -pdf main.tex
```

If the figures change, regenerate them first with `python ../make_charts.py`,
then copy the four `chart_*.png` files from `../artifacts` into `figures/`.

## Note on numbers

Every value in the report comes from the seed-42 run of the pipeline
(`artifacts/metrics.json`, `artifacts/optimization.json`). Re-run the pipeline
with a different seed and the tables should be updated to match.
