# DataVisualizers

Визуализаторы получают результат аналитического модуля и сохраняют его в файл или формируют график.

| Файл | Класс | Назначение |
| --- | --- | --- |
| `DataFrameToExcelVisualizer.py` | `DataFrameToExcelVisualizer` | Экспортирует `pandas.DataFrame` в Excel. |
| `ScatterVisualizer.py` | `ScatterPlotVisualizer` | Строит scatter plot для данных с колонками `x`, `y`, `color`. |
| `MetroUsageVisualizer.py` | `TextReportMetroUsageVisualizer` | Формирует текстовый отчёт по использованию метро. |
| `DistrictProvisionVisualizer.py` | `DistrictProvisionBarVisualizer` | Строит столбчатую диаграмму обеспеченности районов объектами. |
| `GeoPointMapVisualizer.py` | `GeoPointMapVisualizer` | Строит универсальную PNG-карту объектов по широте и долготе. |

## `DistrictProvisionBarVisualizer`

Используется вместе с `DistrictObjectProvisionAnalysis`. Поддерживает параметры:

| Параметр | Описание |
| --- | --- |
| `path_to_save` | Путь для сохранения PNG-графика. |
| `metric` | Колонка метрики для построения, например `objects_per_population` или `capacity_per_population`. |
| `title` | Заголовок графика. |
| `xlabel` / `ylabel` | Подписи осей. |
| `top_n` | Необязательное ограничение числа районов на графике. |
| `color_map` | Цвета уровней `low`, `medium`, `high`. |

## Карты и ТОП-10 отчёты обеспеченности

Для расширенных задач обеспеченности добавлены ещё два визуализатора:

| Файл | Класс | Назначение |
| --- | --- | --- |
| `DistrictProvisionMapVisualizer.py` | `DistrictProvisionMapVisualizer` | Сохраняет PNG-карту-точечную схему объектов по `longitude`/`latitude`, окрашивая точки по уровню обеспеченности района. |
| `DistrictProvisionReportVisualizer.py` | `DistrictProvisionTopReportVisualizer` | Формирует текстовый отчёт TOP/BOTTOM районов и, при заданном `csv_prefix`, отдельные CSV-таблицы для самых обеспеченных и наименее обеспеченных районов. |
| `DataFrameToCsvVisualizer.py` | `DataFrameToCsvVisualizer` | Сохраняет сводный `DataFrame` в CSV без зависимости от Excel-библиотек. |

Расширенные конфиги обеспеченности используют три результата анализатора: сводную таблицу, TOP/BOTTOM-отчёт и данные точечной карты. Поэтому в них подключаются три визуализатора в том же порядке.
