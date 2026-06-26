Реализованы адаптеры для основных московских открытых транспортных наборов данных:

| Адаптер | Dataset | Ссылка `data.mos.ru` | Типовая совместимость с анализом |
| --- | --- | --- | --- |

| `MoscowTaxiParkingLoader` | 621, парковки такси | https://data.mos.ru/opendata/621 | Статический геореестр, фильтрация, предварительная оценка покрытия |
| `MoscowBikeRentalLoader` | 1777, пункты велопроката | https://data.mos.ru/opendata/1777 | Статический геореестр, фильтрация, разделение сетевых/несетевых объектов при наличии поля |
| `MoscowTransitStopsRoutesLoader` | 60661, маршруты и остановки НГПТ | https://data.mos.ru/opendata/60661 | Справочный анализ маршрутов/остановок; не является временным рядом пассажиропотока |

В платформе уже есть анализаторы аномалий, потенциального фрода и типов районов,
которые рассчитаны на временные ряды валидаторных данных или мобильных потоков.
Перечисленные наборы `data.mos.ru` в основном являются статическими реестрами,
поэтому напрямую совместимы со сводками `DataFrame`, колонковой фильтрацией,
гео-сценариями и экспортом. Для применения методов анализа пассажиропотока их
нужно предварительно объединять с операционными данными, где есть временные метки
и значения спроса/потока.

Если публичный API недоступен из окружения, передайте параметр `data_path` с
локальным CSV- или JSON-кэшем, скачанным со страницы набора. Загрузчик сначала
читает локальный кэш и только при его отсутствии обращается к API.

---

# `data.mos.ru` transport adapters

Adapters have been implemented for the main Moscow open transport datasets:

| Adapter | Dataset | `data.mos.ru` URL | Typical analysis compatibility |
| --- | --- | --- | --- |

| `MoscowTaxiParkingLoader` | 621, taxi parking | https://data.mos.ru/opendata/621 | Static geospatial inventory, filtering, coverage previews |
| `MoscowBikeRentalLoader` | 1777, bicycle rental points | https://data.mos.ru/opendata/1777 | Static geospatial inventory, filtering, network/non-network split if the field is available |
| `MoscowTransitStopsRoutesLoader` | 60661, public transport routes/stops schedules | https://data.mos.ru/opendata/60661 | Route/stop reference analysis and filtering; not a passenger-flow time series |

The platform already contains anomaly, fraud and hood-type analyzers aimed at
time-series validator/mobile-flow datasets. The `data.mos.ru` adapters above are
mostly static registries, so they are directly compatible with generic dataframe
summaries, column filters, geospatial workflows and exports. To use passenger-flow
analysis methods, join these registries with operational data that contains
timestamps and demand/flow values.

If the public API is unavailable in the execution environment, pass `data_path`
with a cached CSV or JSON export from the dataset page. The loader reads local
caches first and only calls the API when no local cache is provided.

