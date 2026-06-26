# Решённые исследовательские задачи / Solved research tasks

> Проект носит исследовательский и некоммерческий характер. Он основан на материалах диссертационной работы Марка Валерьевича Булыгина, опубликованных на странице МФТИ: https://mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich.
>
> Если правообладатель или представитель источника данных хочет удалить какой-либо набор данных, пример, ссылку или описание из репозитория, достаточно написать на почту проекта: `messimm@yandex.ru`.

## Сводная таблица кейсов

| Кейc | Источники данных | Конфиг запуска | Документация модулей | Результаты и визуализации |
| --- | --- | --- | --- | --- |
| [Обеспеченность районов платными парковками](#обеспеченность-районов-платными-парковками) | `data.mos.ru` dataset 623 + население районов | `Configs/DataMosStreetParkingDistrictProvision.json` | `DataLoaders/README.md`, `DataVisualizers/README.md` | CSV-сводка, TOP/BOTTOM-10 отчёт, PNG-карта объектов |
| [Обеспеченность районов пунктами велопроката](#обеспеченность-районов-пунктами-велопроката) | `data.mos.ru` dataset 1777 + население районов | `Configs/DataMosBikeRentalDistrictProvision.json` | `DataLoaders/README.md`, `DataVisualizers/README.md` | CSV-сводка, TOP/BOTTOM-10 отчёт, PNG-карта объектов |
| [Обеспеченность районов стоянками такси](#обеспеченность-районов-стоянками-такси) | `data.mos.ru` dataset 621 + население районов | `Configs/DataMosTaxiParkingDistrictProvision.json` | `DataLoaders/DATAMOS.md`, `DataCheckers/README.md` | CSV-сводка, TOP/BOTTOM-10 отчёт, PNG-карта объектов |
| [Обеспеченность районов остановками и маршрутными записями НГПТ](#обеспеченность-районов-остановками-и-маршрутными-записями-нгпт) | `data.mos.ru` dataset 60661 + население районов | `Configs/DataMosTransitStopsDistrictProvision.json` | `DataLoaders/DATAMOS.md`, `DataAnalyzers/Readme.md` | CSV-сводка, TOP/BOTTOM-10 отчёт, PNG-карта объектов |
| [Сводная проверка набора платных парковок](#сводная-проверка-набора-платных-парковок) | `data.mos.ru` dataset 623 | `Configs/DataMosStreetParking.json` | `DataAnalyzers/Readme.md` | Табличная сводка качества и совместимости |

## Общий исследовательский pipeline для кейсов обеспеченности

Все задачи обеспеченности районов собраны из одинаковых этапов:

1. **Загрузка объектов** через адаптер `data.mos.ru`.
2. **Загрузка населения районов** через `DistrictPopulationLoader`.
3. **Фильтрация** пустых районов, некорректных координат и некорректного населения через `DataFrameColumnFilterChecker`.
4. **Расчёт обеспеченности** через `DistrictObjectProvisionAnalysis`:
   - `object_count` — количество объектов в районе;
   - `objects_per_population` — объектов на 100 тыс. жителей;
   - `capacity_total` и `capacity_per_population` — суммарная ёмкость и ёмкость на 100 тыс. жителей, если поле ёмкости есть в источнике;
   - `provision_level` — уровень `low`, `medium`, `high`.
5. **Визуализация и отчёты**:
   - `DataFrameToCsvVisualizer` — CSV-сводка;
   - `DistrictProvisionTopReportVisualizer` — текстовый отчёт и TOP/BOTTOM CSV;
   - `DistrictProvisionMapVisualizer` — PNG-точечная карта объектов.

## Обеспеченность районов платными парковками

**Вопрос:** какие районы лучше или хуже обеспечены парковочными местами с учётом численности населения?

**Метрика:** `capacity_per_population` — парковочных мест на 100 тыс. жителей.

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingDistrictProvision.json
```

**Ожидаемые файлы результата:**

- `street_parking_district_provision_summary.csv` — районная сводка;
- `street_parking_district_provision_top10_report.txt` — текстовый TOP/BOTTOM-10;
- `street_parking_district_provision_top10_top.csv` — самые обеспеченные районы;
- `street_parking_district_provision_top10_bottom.csv` — наименее обеспеченные районы;
- `street_parking_district_provision_map.png` — PNG-карта объектов.

## Обеспеченность районов пунктами велопроката

**Вопрос:** насколько равномерно пункты велопроката распределены относительно населения районов?

**Метрика:** `objects_per_population` — пунктов велопроката на 100 тыс. жителей.

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosBikeRentalDistrictProvision.json
```

**Ожидаемые файлы результата:**

- `bike_rental_district_provision_summary.csv`;
- `bike_rental_district_provision_top10_report.txt`;
- `bike_rental_district_provision_top10_top.csv`;
- `bike_rental_district_provision_top10_bottom.csv`;
- `bike_rental_district_provision_map.png`.

## Обеспеченность районов стоянками такси

**Вопрос:** какие районы имеют больше или меньше стоянок такси относительно численности населения?

**Метрика:** `objects_per_population` — стоянок такси на 100 тыс. жителей.

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosTaxiParkingDistrictProvision.json
```

**Ожидаемые файлы результата:**

- `taxi_parking_district_provision_summary.csv`;
- `taxi_parking_district_provision_top10_report.txt`;
- `taxi_parking_district_provision_top10_top.csv`;
- `taxi_parking_district_provision_top10_bottom.csv`;
- `taxi_parking_district_provision_map.png`.

## Обеспеченность районов остановками и маршрутными записями НГПТ

**Вопрос:** какие районы лучше представлены в справочных данных остановок/маршрутов наземного транспорта относительно населения?

**Метрика:** `objects_per_population` — записей остановок/маршрутов на 100 тыс. жителей.

**Важно:** dataset 60661 является справочным набором маршрутно-остановочных записей, а не прямым измерением пассажиропотока. Для интерпретации как доступности транспортной инфраструктуры его желательно дополнительно очищать от дублей и обогащать геометрией остановок.

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosTransitStopsDistrictProvision.json
```

**Ожидаемые файлы результата:**

- `transit_stops_district_provision_summary.csv`;
- `transit_stops_district_provision_top10_report.txt`;
- `transit_stops_district_provision_top10_top.csv`;
- `transit_stops_district_provision_top10_bottom.csv`;
- `transit_stops_district_provision_map.png`.

## Сводная проверка набора платных парковок

**Вопрос:** можно ли быстро проверить структуру, координаты и совместимость статического набора `data.mos.ru` с платформой?

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosStreetParking.json
```

**Результат:** табличная сводка `GenericDatasetSummaryAnalysis`, пригодная для экспорта и первичной проверки качества данных.

---

# English summary

This page documents solved non-commercial research cases based on the project methodology and the dissertation materials published by MIPT for Mark Valerievich Bulygin: https://mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich.

If a rights holder or data-source representative wants any dataset, example, link or description removed from this repository, please contact `messimm@yandex.ru`.

The implemented cases evaluate district provision with street parking, bike rental points, taxi parking and surface public transport stop/route records. Each workflow combines `data.mos.ru` object loaders, district population data, reusable filters, provision metrics, CSV reports, TOP/BOTTOM-10 text reports and PNG point-map visualizations.
