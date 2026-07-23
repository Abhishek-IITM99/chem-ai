# chem-ai

Work by the trio team (Abhishek Chankapure, Saurabh Ramteke, Vaibhav Patil).
The repository holds two things: the ThermoTwin technical project and the team's
business material.

## Structure

```
chem-ai/
  thermotwin/   first-principles fired-heater digital twin (code, data, docs)
  business/     pitch and fundraising material (Hub71, fund flow, notes)
  README.md
  .gitignore
```

## ThermoTwin, in one paragraph

A fired heater is the largest fuel user and carbon source on a refinery unit.
ThermoTwin models the heater from first principles (combustion chemistry, energy
and mass balance, heat transfer), generates an operating dataset, trains a
machine-learning surrogate on that data, and recommends the excess-air setpoint
that cuts fuel and carbon within the safety limits. On the prototype it recovers
about 2.5 efficiency points and near 2,560 t of CO2 per heater per year.

## Quick start

```bash
cd thermotwin
pip install -r requirements.txt

python generate_dataset.py     # 1. Collect  -> heater_dataset.csv
python twin_pipeline.py        # 2. Clean, label, train, validate -> models/, artifacts/
python optimize.py             # 3. Optimize -> artifacts/optimization.json
python make_charts.py          # 4. Charts   -> artifacts/chart_*.png
streamlit run dashboard.py     # 5. Deploy   -> live demo
```

## Where to read more

| File | What it covers |
|------|----------------|
| `thermotwin/README.md` | Pipeline details and results |
| `thermotwin/DATA_DICTIONARY.md` | Every dataset column, with units and source |
| `thermotwin/latex/ThermoTwin_Technical_Reference.pdf` | All equations, assumptions and methods |
| `thermotwin/hub71_deck.html` | The pitch deck (open in a browser) |

## Notes for collaborators

- Trained models (`models/`, `*.joblib`) and `__pycache__` are not committed
  because they are large and regenerable. Run `python twin_pipeline.py` to
  produce them locally.
- The dataset, charts and technical report are committed, so the results are
  reproducible without a first run.
- Please branch for changes and open a pull request rather than pushing to
  `main` directly.
```
git checkout -b your-feature
# work, commit
git push -u origin your-feature
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## License

Proprietary and confidential. All rights reserved by the trio team. See
[LICENSE](LICENSE). Access is limited to named collaborators and is subject to the
co-founder non-disclosure agreement.
