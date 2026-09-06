Описание аналитических модулей / Description of Analytical Modules
| Файл / File             | Назначение (RU)                                                   | Purpose (EN)                                                 |
| ----------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------ |
| `BasicAnalyzer.py`      | Базовый класс для всех аналитических модулей                      | Base class for all analytical modules                        |
| `MetroUsageAnalyzer.py` | Анализ степени использования метрополитена                        | Analysis of subway usage intensity                           |
| `AnomalyDetector.py`    | Детекция аномалий в транспортных потоках                          | Detection of anomalies in transportation flows               |
| `HoodTypeAnalyzer.py`   | Кластеризация районов по типам транспортного поведения            | Clustering of urban areas by transportation usage patterns   |
| `FraudAnalyzer.py`      | Поиск потенциальных случаев мошенничества в транспортных системах | Detection of potential fraud cases in transportation systems |
| `GenericDatasetSummaryAnalyzer.py` | Сводная проверка статических наборов данных и совместимости с фильтрами | Summary check for static datasets and filter compatibility |
| `DistrictProvisionAnalyzer.py` | Оценка обеспеченности районов транспортными объектами на основе населения | District provision analysis for transport objects using population data |
| `GeoObjectInventoryAnalyzer.py` | Подготовка очищенного геореестра и точек для карты | Clean geospatial inventory and map-point preparation |
| `BikeShareAvailabilityAnalyzer.py` | Поиск пустых, почти заполненных и недоступных станций велошеринга | Detection of empty, near-full and unavailable bike-share stations |
| `ServiceStatusAnalyzer.py` | Ранжирование линий общественного транспорта и сводка нарушений | Public transport line status ranking and disruption summary |
| `GTFSServiceSupplyAnalyzer.py` | Анализ числа рейсов, остановок и предложения по маршрутам GTFS | GTFS route trip, stop coverage and service supply analysis |
| `DeparturePunctualityAnalyzer.py` | Расчёт прогнозной задержки и классификация ближайших отправлений | Predicted delay calculation and upcoming departure classification |
| `GeoClusteringAnalyzer.py` | Универсальная KMeans-кластеризация транспортных объектов по геопризнакам | Generic KMeans clustering of transport objects by geospatial features |
| `GTFSStopClusterAnalyzer.py` | Кластеризация остановок по географии и интенсивности обслуживания | Stop clustering by geography and scheduled service intensity |
| `RobustAnomalyAnalyzer.py` | Робастная детекция числовых аномалий на основе медианы и MAD | Median/MAD-based robust numeric anomaly detection |
