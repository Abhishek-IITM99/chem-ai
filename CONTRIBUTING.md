# Contributing to chem-ai

Guidelines for the trio team (Abhishek Chankapure, Saurabh Ramteke, Vaibhav Patil)
working on this repository.

## Set up once

```bash
git clone https://github.com/Abhishek-IITM99/chem-ai.git
cd chem-ai/thermotwin
pip install -r requirements.txt
```

Read `thermotwin/README.md` and the technical report in `thermotwin/latex` before
changing the physics.

## Branching

- Do not commit to `main` directly. `main` stays clean and runnable.
- Create one branch per piece of work: `git checkout -b area-short-description`.
  Examples: `twin-gradient-boosting`, `dashboard-emissions-tab`, `docs-fix-nox`.
- Keep a branch focused on a single change.

## Commits

- Write present-tense, specific messages, for example "add SOx to dashboard KPI row".
- Commit small and often. Do not mix unrelated changes in one commit.
- Never commit generated files (trained models, `__pycache__`, data you can
  regenerate) or secrets. The `.gitignore` covers the common cases.

## Pull requests

```bash
git push -u origin your-branch
```

- Open a pull request against `main`.
- Describe what changed and why. Link a result (a number or a chart) where it helps.
- At least one other founder reviews before merge.
- Keep `main` runnable: the five-step pipeline in the README should work after
  every merge.

To stay current with the team:

```bash
git checkout main
git pull
```

## Running the pipeline

```bash
cd thermotwin
python generate_dataset.py     # Collect  -> heater_dataset.csv
python twin_pipeline.py        # Clean, label, train, validate -> models/, artifacts/
python optimize.py             # Optimize -> artifacts/optimization.json
python make_charts.py          # Charts   -> artifacts/chart_*.png
streamlit run dashboard.py     # Deploy   -> live demo
```

## Code and writing style

- Python: match the existing style. Clear names, short functions, and a comment
  where the physics is not obvious.
- Keep units SI, and state the assumption next to any new correlation.
- Documentation and report text follow the writing rules in the team style guide
  (plain English, no em-dashes, specific over vague).

## Data and models

- The dataset and charts are committed, so results reproduce without a first run.
- Trained models are not committed. Run `python twin_pipeline.py` to build them.
- If you change the physics or the generator, regenerate the dataset, retrain the
  twin, refresh the charts, and update the numbers in the docs and the report.

## Questions

Open an issue on GitHub or raise it in the team channel.
