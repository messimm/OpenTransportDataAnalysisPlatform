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
| [Online-проверка актуального набора парковок](#online-проверка-актуального-набора-парковок) | API `data.mos.ru`, dataset 623 | `Configs/DataMosStreetParkingOnline.json` | `DataLoaders/README.md` | Автоматическая загрузка и CSV-сводка |
| [Международный online-пример GBFS](#международный-online-пример-gbfs) | Публичный GBFS Citi Bike | `Configs/WorldGBFSBikeStationsOnline.json` | `DataLoaders/README.md` | CSV станций и PNG-карта |
| [Поиск дисбаланса велошеринга](#поиск-дисбаланса-велошеринга) | GBFS station information + status | `Configs/WorldGBFSBikeAvailabilityOnline.json` | `DataAnalyzers/Readme.md` | Рейтинг станций, CSV и PNG-карта |
| [Мониторинг нарушений движения TfL](#мониторинг-нарушений-движения-tfl) | TfL Unified API | `Configs/WorldTfLTubeStatusOnline.json` | `DataLoaders/README.md` | CSV линий и текстовая сводка |
| [Анализ предложения по GTFS](#анализ-предложения-по-gtfs) | Публичный MBTA GTFS ZIP | `Configs/WorldGTFSServiceSupplyOnline.json` | `DataAnalyzers/Readme.md` | Рейтинг маршрутов, CSV и TXT |
| [Пунктуальность ближайших отправлений](#пунктуальность-ближайших-отправлений) | transport.opendata.ch | `Configs/WorldSwissDeparturePunctualityOnline.json` | `DataLoaders/README.md` | Рейтинг задержек, CSV и TXT |
| [Кластеризация аэропортов](#кластеризация-аэропортов) | OurAirports | `Configs/WorldAirportClusteringOnline.json` | `DataAnalyzers/Readme.md` | CSV кластеров и PNG-карта |
| [Предложение пригородных поездов](#предложение-пригородных-поездов) | GTFS route type 2 | `Configs/WorldGTFSCommuterRailSupplyOnline.json` | `DataAnalyzers/Readme.md` | Рейтинг маршрутов, CSV и TXT |
| [Кластеризация станций GTFS](#кластеризация-станций-gtfs) | GTFS stops + stop times | `Configs/WorldGTFSStationClusteringOnline.json` | `DataAnalyzers/Readme.md` | CSV кластеров и PNG-карта |
| [Аномалии задержек](#аномалии-задержек) | Swiss stationboard | `Configs/WorldSwissDelayAnomaliesOnline.json` | `DataAnalyzers/Readme.md` | Робастные anomaly scores, CSV и TXT |

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

- `outputs/street_parking_district_provision_summary.csv` — районная сводка;
- `outputs/street_parking_district_provision_top10_report.txt` — текстовый TOP/BOTTOM-10;
- `outputs/street_parking_district_provision_top10_top.csv` — самые обеспеченные районы;
- `outputs/street_parking_district_provision_top10_bottom.csv` — наименее обеспеченные районы;
- `outputs/street_parking_district_provision_map.png` — PNG-карта объектов.

## Обеспеченность районов пунктами велопроката

**Вопрос:** насколько равномерно пункты велопроката распределены относительно населения районов?

**Метрика:** `objects_per_population` — пунктов велопроката на 100 тыс. жителей.

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosBikeRentalDistrictProvision.json
```

**Ожидаемые файлы результата:**

- `outputs/bike_rental_district_provision_summary.csv`;
- `outputs/bike_rental_district_provision_top10_report.txt`;
- `outputs/bike_rental_district_provision_top10_top.csv`;
- `outputs/bike_rental_district_provision_top10_bottom.csv`;
- `outputs/bike_rental_district_provision_map.png`.

## Обеспеченность районов стоянками такси

**Вопрос:** какие районы имеют больше или меньше стоянок такси относительно численности населения?

**Метрика:** `objects_per_population` — стоянок такси на 100 тыс. жителей.

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosTaxiParkingDistrictProvision.json
```

**Ожидаемые файлы результата:**

- `outputs/taxi_parking_district_provision_summary.csv`;
- `outputs/taxi_parking_district_provision_top10_report.txt`;
- `outputs/taxi_parking_district_provision_top10_top.csv`;
- `outputs/taxi_parking_district_provision_top10_bottom.csv`;
- `outputs/taxi_parking_district_provision_map.png`.

## Обеспеченность районов остановками и маршрутными записями НГПТ

**Вопрос:** какие районы лучше представлены в справочных данных остановок/маршрутов наземного транспорта относительно населения?

**Метрика:** `objects_per_population` — записей остановок/маршрутов на 100 тыс. жителей.

**Важно:** dataset 60661 является справочным набором маршрутно-остановочных записей, а не прямым измерением пассажиропотока. Для интерпретации как доступности транспортной инфраструктуры его желательно дополнительно очищать от дублей и обогащать геометрией остановок.

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosTransitStopsDistrictProvision.json
```

**Ожидаемые файлы результата:**

- `outputs/transit_stops_district_provision_summary.csv`;
- `outputs/transit_stops_district_provision_top10_report.txt`;
- `outputs/transit_stops_district_provision_top10_top.csv`;
- `outputs/transit_stops_district_provision_top10_bottom.csv`;
- `outputs/transit_stops_district_provision_map.png`.

## Сводная проверка набора платных парковок

**Вопрос:** можно ли быстро проверить структуру, координаты и совместимость статического набора `data.mos.ru` с платформой?

**Запуск:**

```bash
python launch_from_cfg.py Configs/DataMosStreetParking.json
```

**Результат:** табличная сводка `GenericDatasetSummaryAnalysis`, пригодная для экспорта и первичной проверки качества данных.

## Online-проверка актуального набора парковок

Этот пример предназначен для самого короткого сценария «скачать → проверить →
сохранить» без ручной подготовки файла:

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingOnline.json
```

Результат сохраняется в `outputs/online_street_parking_summary.csv`. Источник —
официальный API `data.mos.ru`, dataset 623. Если API требует ключ:

```bash
DATA_MOS_API_KEY="ваш-ключ" python launch_from_cfg.py Configs/DataMosStreetParkingOnline.json
```

При недоступности внешнего портала пример автоматически переключается на
`tests/fixtures/datamos_rows.json`. В поле `_source` будет указано
`fallback_cache`, а при успешной загрузке — `data.mos.ru_api`.

## Международный online-пример GBFS

Для пользователей за пределами России добавлен пример на международном открытом
стандарте GBFS (General Bikeshare Feed Specification):

```bash
python launch_from_cfg.py Configs/WorldGBFSBikeStationsOnline.json
```

Pipeline загружает справочник станций Citi Bike, проверяет обязательные поля и
диапазоны координат, а затем сохраняет таблицу и PNG-карту:

- `outputs/world_gbfs_bike_stations.csv`;
- `outputs/world_gbfs_bike_stations_map.png`.

Если endpoint заблокирован proxy или временно недоступен, используется небольшой
локальный GBFS fixture. Значение `_source=gbfs_api` означает успешную загрузку из
Интернета, `_source=fallback_cache` — использование локального примера.

## Поиск дисбаланса велошеринга

**Задача:** оперативно найти станции, на которых пользователь не сможет взять
велосипед или вернуть его из-за отсутствия свободного дока.

```bash
python launch_from_cfg.py Configs/WorldGBFSBikeAvailabilityOnline.json
```

Алгоритм объединяет GBFS-ленты `station_information` и `station_status` по
`station_id`, проверяет эксплуатационные флаги, вычисляет
`availability_ratio` и `imbalance_score = |availability_ratio - target_ratio|`.
Станции классифицируются как `empty`, `near_full`, `unavailable` или `balanced`.
На выходе создаются CSV-рейтинг и PNG-карта.

## Мониторинг нарушений движения TfL

**Задача:** получить воспроизводимую оперативную сводку по линиям метро и быстро
выделить линии с нарушениями движения.

```bash
python launch_from_cfg.py Configs/WorldTfLTubeStatusOnline.json
```

`ServiceStatusAnalysis` сравнивает severity каждой линии со значением нормальной
работы, ранжирует нарушения и считает количество затронутых линий. Результаты:

- `outputs/world_tfl_tube_status.csv`;
- `outputs/world_tfl_tube_status_report.txt`.

## Анализ предложения по GTFS

**Задача:** сравнить запланированный объём транспортного предложения разных
маршрутов без привязки к проприетарному API перевозчика.

```bash
python launch_from_cfg.py Configs/WorldGTFSServiceSupplyOnline.json
```

`GTFSServiceSupplyAnalysis` связывает `routes.txt`, `trips.txt` и
`stop_times.txt`, после чего рассчитывает:

- число уникальных рейсов маршрута;
- число обслуживаемых остановок;
- число остановочных событий;
- первое и последнее отправление;
- простой `supply_score = trips_count × stops_count` для первичного сравнения.

Результаты сохраняются в `outputs/world_gtfs_service_supply.csv` и
`outputs/world_gtfs_service_supply_report.txt`. В качестве online-источника
используется MBTA GTFS, при недоступности — маленькая распакованная GTFS fixture
из обычных текстовых файлов. Бинарные архивы в репозиторий не добавляются.

## Пунктуальность ближайших отправлений

**Задача:** оценить текущую пунктуальность отправлений по данным расписания и
оперативного прогноза.

```bash
python launch_from_cfg.py Configs/WorldSwissDeparturePunctualityOnline.json
```

`DeparturePunctualityAnalysis` использует готовое поле задержки либо вычисляет
разницу между `predicted_departure` и `scheduled_departure`. Затем отправления
получают состояние `on_time`, `delayed` или `unknown`. Порог задержки задаётся в
конфиге через `delay_threshold_minutes`.

Результаты: `outputs/world_swiss_departure_punctuality.csv` и
`outputs/world_swiss_departure_punctuality_report.txt`.

## Кластеризация аэропортов

**Задача:** автоматически разделить крупные и средние аэропорты на устойчивые
географические группы для макрорегионального сравнения, построения выборок и
последующего подключения показателей пассажиропотока.

```bash
python launch_from_cfg.py Configs/WorldAirportClusteringOnline.json
```

`OurAirportsLoader` загружает мировой CSV-реестр, а `GeoKMeansAnalysis`
нормализует координаты и выполняет воспроизводимую KMeans-кластеризацию.
Результаты: `outputs/world_airport_clusters.csv` и PNG-карта кластеров.

## Предложение пригородных поездов

**Задача:** сравнить объём запланированного движения пригородных поездов по
маршрутам.

```bash
python launch_from_cfg.py Configs/WorldGTFSCommuterRailSupplyOnline.json
```

Используется стандартный GTFS `route_type=2`: анализатор оставляет железнодорожные
маршруты и рассчитывает число рейсов, остановок, остановочных событий и
`supply_score`. На выходе создаются CSV и текстовый отчёт.

## Кластеризация станций GTFS

**Задача:** выделить типы станций не только по положению, но и по интенсивности
запланированного обслуживания.

```bash
python launch_from_cfg.py Configs/WorldGTFSStationClusteringOnline.json
```

Признаки: широта, долгота и `log(1 + stop_events)`. Перед KMeans признаки
стандартизируются. Результаты сохраняются в CSV и PNG-карту с цветом кластера.

## Аномалии задержек

**Задача:** обнаружить единичные экстремальные задержки, не позволяя самим
выбросам сильно смещать оценку нормального уровня.

```bash
python launch_from_cfg.py Configs/WorldSwissDelayAnomaliesOnline.json
```

Используется робастный score на основе медианы и median absolute deviation (MAD).
Порог задаётся параметром `threshold`; результат содержит
`robust_anomaly_score` и `is_anomaly`, а также CSV и текстовую сводку.

---

# English summary

This page documents solved non-commercial research cases based on the project methodology and the dissertation materials published by MIPT for Mark Valerievich Bulygin: https://mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich.

If a rights holder or data-source representative wants any dataset, example, link or description removed from this repository, please contact `messimm@yandex.ru`.

The implemented cases evaluate district provision with street parking, bike rental points, taxi parking and surface public transport stop/route records. Each workflow combines `data.mos.ru` object loaders, district population data, reusable filters, provision metrics, CSV reports, TOP/BOTTOM-10 text reports and PNG point-map visualizations.
