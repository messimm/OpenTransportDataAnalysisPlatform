# AGENTS.md — instructions for coding agents

This repository is a modular research platform for transport data analysis. When a user describes a transport-analysis task in domain language, translate it into the platform pipeline:

1. `DataLoaders` — read source data into `pandas.DataFrame`.
2. `DataCheckers` — validate/filter rows before analysis.
3. `DataAnalyzers` — compute metrics or model outputs.
4. `DataVisualizers` — save tables, reports or figures.
5. `Configs` — assemble runnable pipelines for `launch_from_cfg.py`.

## Important project context

- The project is for non-commercial research use.
- It is based on dissertation materials by Mark Valerievich Bulygin published on the MIPT website.
- If datasets/examples/descriptions need removal, documentation points users to `messimm@yandex.ru`.
- Prefer local fixture/cache examples in configs so workflows run without network access.

## Repository map

| Path | Purpose |
| --- | --- |
| `launch_from_cfg.py` | Dynamic pipeline runner. Imports classes by `Name` from module folders. |
| `Configs/` | Runnable JSON pipeline configurations. |
| `DataLoaders/` | Source adapters. Return normalized `DataFrame`s and filtering helpers. |
| `DataCheckers/` | Data quality checks and row filters. |
| `DataAnalyzers/` | Analysis logic. Exactly one analyzer is configured per pipeline. |
| `DataVisualizers/` | Output writers for CSV, Excel, TXT, PNG charts/maps. |
| `docs/SOLVED_TASKS.md` | User-facing solved cases and expected outputs. |
| `docs/AGENT_GUIDE.md` | Agent-facing domain-to-code workflow guide. |
| `tests/fixtures/` | Small local data examples for smoke tests and offline demos. |

## Coding rules

- Keep modules small and compatible with the existing config-driven pipeline.
- Do not put try/except blocks around imports.
- If adding a loader, expose `getAllData`; when possible also expose `getDataByColumnValue`, `getDataByColumnRange`, `getDataByColumnSet`.
- If adding an analyzer that returns multiple outputs, make sure the config has the same number of visualizers.
- If adding a config, prefer fixture-backed defaults and document how to replace `data_path` with real data.
- If adding a visualizer, make it dependency-light unless there is a clear reason.
- Update the relevant README/docs when adding public modules or solved cases.

## Useful validation commands

```bash
python -m compileall DataLoaders DataCheckers DataAnalyzers DataVisualizers launch_from_cfg.py
python launch_from_cfg.py Configs/DataMosStreetParkingDistrictProvision.json
```

For docs-only changes, also check conflict markers:

```bash
rg -n "<<<<<<<|=======|>>>>>>>" README.md DataLoaders DataCheckers DataAnalyzers DataVisualizers docs || true
```
