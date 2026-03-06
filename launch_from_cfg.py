import json
import sys
from importlib import import_module
from pkgutil import iter_modules


PIPELINE_MODULES = ["DataLoaders", "DataCheckers", "DataAnalyzers", "DataVisualizers"]


def import_from_folder_by_name(folder, name):
    """Import class from python package folder by class name."""
    for _, module_name, _ in iter_modules([folder]):
        module = import_module(f"{folder}.{module_name}")
        if hasattr(module, name):
            return getattr(module, name)
    raise ImportError(f"Class '{name}' was not found in package '{folder}'")


def load_modules_from_config(config, folder):
    modules = []
    for module_cfg in config:
        class_name = module_cfg["Name"]
        params = module_cfg.get("Parameters", {})
        klass = import_from_folder_by_name(folder, class_name)
        modules.append(klass(params))
    return modules


def _normalize_results(results):
    if isinstance(results, tuple):
        return list(results)
    if isinstance(results, list):
        return results
    return [results]


def pipeline_from_config(cfg_total):
    modules = []
    for module in PIPELINE_MODULES:
        if module not in cfg_total:
            raise KeyError(f"Missing '{module}' section in config")
        modules.append(load_modules_from_config(cfg_total[module], module))

    loaders, checkers, analyzers, visualizers = modules
    if len(loaders) != len(checkers):
        raise ValueError("Loaders and checkers counts must match")
    if len(analyzers) != 1:
        raise ValueError("Exactly one analyzer must be configured")

    if len(loaders) == 1:
        loaders = loaders[0]
        checkers = checkers[0]

    results = _normalize_results(analyzers[0].analyze(loaders, checkers))
    if len(visualizers) != len(results):
        raise ValueError(
            f"Visualizers count ({len(visualizers)}) does not match results count ({len(results)})"
        )

    for vis, result in zip(visualizers, results):
        vis.visualize(result)


def main():
    if len(sys.argv) < 2:
        raise ValueError("Usage: python launch_from_cfg.py <path_to_config.json>")
    config_path = sys.argv[1]
    with open(config_path, "r", encoding="utf-8") as f:
        cfg_total = json.load(f)
    pipeline_from_config(cfg_total)


if __name__ == "__main__":
    main()
