import argparse
import json
from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules


PIPELINE_MODULES = ["DataLoaders", "DataCheckers", "DataAnalyzers", "DataVisualizers"]
REPOSITORY_ROOT = Path(__file__).resolve().parent


def import_from_folder_by_name(folder, name):
    """Import class from python package folder by class name."""
    module_path = REPOSITORY_ROOT / folder
    for _, module_name, _ in iter_modules([str(module_path)]):
        module = import_module(f"{folder}.{module_name}")
        if hasattr(module, name):
            return getattr(module, name)
    raise ImportError(f"Class '{name}' was not found in package '{folder}'")


def load_modules_from_config(config, folder):
    if not isinstance(config, list):
        raise TypeError(f"'{folder}' must be a list")
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
    if not loaders:
        raise ValueError("At least one loader and checker must be configured")

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


def load_config(config_path):
    path = Path(config_path).expanduser().resolve()
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_configs():
    for path in sorted((REPOSITORY_ROOT / "Configs").glob("*.json")):
        print(path.relative_to(REPOSITORY_ROOT))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Запуск модульного pipeline анализа транспортных данных"
    )
    parser.add_argument("config", nargs="?", help="Путь к JSON-конфигурации")
    parser.add_argument("--list-configs", action="store_true", help="Показать готовые конфиги")
    parser.add_argument("--debug", action="store_true", help="Показать полный traceback при ошибке")
    args = parser.parse_args(argv)

    if args.list_configs:
        list_configs()
        return
    if not args.config:
        parser.error("укажите config или используйте --list-configs")

    try:
        cfg_total = load_config(args.config)
        pipeline_from_config(cfg_total)
    except Exception as exc:
        if args.debug:
            raise
        parser.exit(1, f"Ошибка запуска pipeline: {exc}\nИспользуйте --debug для полного traceback.\n")


if __name__ == "__main__":
    main()
