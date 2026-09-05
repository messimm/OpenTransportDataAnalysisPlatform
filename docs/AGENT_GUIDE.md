# Руководство для кодовых агентов / Coding agent guide

Этот документ нужен, чтобы специалист по транспорту мог дать ссылку на репозиторий в Codex, Claude Code или другой coding-agent инструмент и описывать задачу обычным профессиональным языком.

## Главная идея

Любую задачу старайтесь разложить на pipeline:

```text
источник данных → проверка/фильтрация → аналитика → визуализация/отчёт → JSON-конфиг запуска
```

В коде это соответствует папкам:

| Этап | Где писать код | Что должен сделать агент |
| --- | --- | --- |
| Источник данных | `DataLoaders/` | Прочитать CSV/JSON/API, нормализовать имена колонок, вернуть `DataFrame`. |
| Проверка качества | `DataCheckers/` | Отфильтровать пустые значения, диапазоны, координаты, неконсистентные строки. |
| Аналитика | `DataAnalyzers/` | Посчитать транспортную метрику, рейтинг, кластер, аномалию или сводку. |
| Визуализация | `DataVisualizers/` | Сохранить CSV/TXT/PNG/Excel результат. |
| Сборка | `Configs/` | Создать JSON, который запускается через `python launch_from_cfg.py <config>`. |
| Документация | `README.md`, `docs/` | Объяснить, что решает кейс, какие входы нужны и какие файлы будут на выходе. |

## Как формулировать задачи агенту

Хорошая постановка на естественном языке:

```text
Нужно оценить обеспеченность районов зарядными станциями. У меня есть CSV с колонками address, district, latitude, longitude, plugs_count. Нужно посчитать станций и разъёмов на 100 тыс. жителей, сделать TOP-10 лучших и худших районов, карту PNG и конфиг запуска.
```

Агент должен понять, что нужны:

1. loader для CSV или настройка существующего loader;
2. `DataFrameColumnFilterChecker` для `district`, `latitude`, `longitude`, `plugs_count`;
3. `DistrictObjectProvisionAnalysis` с `capacity_column="plugs_count"`;
4. `DataFrameToCsvVisualizer`, `DistrictProvisionTopReportVisualizer`, `DistrictProvisionMapVisualizer`;
5. новый config в `Configs/`;
6. обновление `docs/SOLVED_TASKS.md`.

## Типовые маршруты разработки

### Новый набор `data.mos.ru`

1. Найти dataset id и поля источника.
2. Добавить класс-наследник `DataMosDatasetLoader` в `DataLoaders/DataMosLoaders.py`.
3. Настроить `default_columns_map` для `latitude`, `longitude`, `district`, `capacity` или других важных полей.
4. Добавить fixture или пример `data_path`.
5. Добавить config и документацию.

### Новый районный кейс обеспеченности

1. Проверить, есть ли в объектах район (`district`) или возможность предварительно обогатить район по координатам.
2. Подключить `DistrictPopulationLoader`.
3. Использовать `DistrictObjectProvisionAnalysis`.
4. Вернуть outputs `summary`, `top_report`, `map_points`.
5. Подключить CSV, TXT/CSV TOP-10 и PNG-map визуализаторы.

### Новый отчёт или график

1. Добавить визуализатор в `DataVisualizers/`.
2. Визуализатор должен принимать ровно тот объект, который возвращает analyzer.
3. Добавить параметры `path_to_save` и, если нужно, `title`, `metric`, `columns`.
4. Обновить `DataVisualizers/README.md`.

## Что обязательно проверять

```bash
python -m compileall DataLoaders DataCheckers DataAnalyzers DataVisualizers launch_from_cfg.py
python -m unittest discover -s tests -v
```

Если менялись готовые конфиги:

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingDistrictProvision.json
```

Если менялась документация после merge/conflict:

```bash
rg -n "<<<<<<<|=======|>>>>>>>" README.md DataLoaders DataCheckers DataAnalyzers DataVisualizers docs || true
```

## О чём помнить

- Проект исследовательский и некоммерческий.
- Не добавляйте большие реальные данные в репозиторий; используйте маленькие fixtures.
- Для внешних API всегда оставляйте путь через локальный `data_path`, чтобы pipeline запускался без сети.
- Пишите конфиги так, чтобы специалист мог заменить путь к файлу и запустить пример без чтения кода.
- Документация важна так же, как код: человек может найти проект через поиск и должен быстро понять, какие транспортные задачи уже решены.
