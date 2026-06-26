# OpenTransportDataPlatform

**OpenTransportDataPlatform** — модульная программная платформа с открытым исходным кодом, предназначенная для анализа транспортных данных. Платформа реализует архитектурный подход, ориентированный на повторное использование компонентов и ускоренное прототипирование аналитических решений. Основное внимание уделяется решению прикладных задач в области городской мобильности, интеллектуального транспортного планирования и обработки больших транспортных потоков.

**OpenTransportDataPlatform** is a modular open-source software platform designed for the analysis of transportation data. The platform implements an architectural approach focused on component reuse and rapid prototyping of analytical solutions. The project emphasizes solving practical problems in urban mobility, intelligent transportation planning, and large-scale traffic analysis.


## Исследовательский статус и некоммерческое использование / Research and non-commercial use

Проект основан на материалах диссертационной работы Марка Валерьевича Булыгина, опубликованных на странице МФТИ: [mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich](https://mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich). Платформа и примеры предназначены для некоммерческого использования и выполняются в исследовательских целях.

Если какой-либо набор данных, пример, ссылка или описание должны быть удалены из репозитория, напишите на почту проекта: `messimm@yandex.ru`.

The project is based on dissertation materials by Mark Valerievich Bulygin published on the MIPT website. The platform and examples are intended for non-commercial research use. If any dataset, example, link or description should be removed from the repository, please contact `messimm@yandex.ru`.

---

## Основные возможности / Key Features:

- Унифицированная модель представления транспортных данных различных типов (GPS-треки, данные валидаторов, сетевые графы и др.)
- Гибкая архитектура, позволяющая конструировать решения из готовых модулей
- Поддержка задач кластеризации, обнаружения аномалий и выявления мошенничества
- Расширяемая система API для интеграции с внешними источниками данных
- Возможность локального и облачного развёртывания
- Реализация на Python с использованием стандартных аналитических и инфраструктурных библиотек

---

- Unified model for various types of transportation data (e.g., GPS traces, validator logs, network graphs)
- Flexible architecture for assembling solutions from reusable modules
- Built-in support for clustering, anomaly detection, and fraud identification
- Extensible API system for integration with external data sources
- Supports both local and cloud-based deployment
- Implemented in Python using standard analytical and infrastructure libraries

## Назначение / Purpose:

Платформа предназначена для исследователей, инженеров и специалистов в области транспортного анализа, которым требуется инструмент для построения, тестирования и внедрения аналитических решений с минимальными затратами на программную реализацию.

The platform is designed for researchers, engineers, and professionals in transportation analytics who need a tool for building, testing, and deploying analytical solutions with minimal software development overhead.


## Поддерживаемые источники данных / Supported Data Sources

Платформа поддерживает подключение локальных файлов и внешних открытых источников через модульные загрузчики данных. Для московских открытых транспортных данных добавлены адаптеры `data.mos.ru`, которые можно использовать как через API портала, так и через локальный CSV/JSON-кэш, если прямой сетевой доступ ограничен.

### Наборы `data.mos.ru` / `data.mos.ru` datasets

| Набор данных | Адаптер | Назначение в платформе |
| --- | --- | --- |
| [Платные парковки на улично-дорожной сети, dataset 623](https://data.mos.ru/opendata/623) | `MoscowStreetParkingLoader` | Статический геореестр парковок, анализ ёмкости, фильтрация и экспорт |
| [Парковки такси, dataset 621](https://data.mos.ru/opendata/621) | `MoscowTaxiParkingLoader` | Геореестр стоянок такси, проверка покрытия и пространственная фильтрация |
| [Прокат велосипедов, dataset 1777](https://data.mos.ru/opendata/1777) | `MoscowBikeRentalLoader` | Реестр пунктов велопроката, геоанализ и фильтрация объектов |
| [Маршруты и остановки наземного городского пассажирского транспорта, dataset 60661](https://data.mos.ru/opendata/60661) | `MoscowTransitStopsRoutesLoader` | Справочные данные по маршрутам/остановкам для маршрутизационных и справочных сценариев |

Подробная документация по параметрам загрузчиков, примеру конфигурации и совместимости с анализаторами находится в [`DataLoaders/README.md`](DataLoaders/README.md) и [`DataLoaders/DATAMOS.md`](DataLoaders/DATAMOS.md).

---


## Решённые задачи и визуализации / Solved cases and visualizations

| Кейc / Case | Конфиг / Config | Визуализации и отчёты / Visualizations and reports | Документация / Docs |
| --- | --- | --- | --- |
| Обеспеченность районов платными парковками | `Configs/DataMosStreetParkingDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание кейса](docs/SOLVED_TASKS.md#обеспеченность-районов-платными-парковками) |
| Обеспеченность районов пунктами велопроката | `Configs/DataMosBikeRentalDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание кейса](docs/SOLVED_TASKS.md#обеспеченность-районов-пунктами-велопроката) |
| Обеспеченность районов стоянками такси | `Configs/DataMosTaxiParkingDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание кейса](docs/SOLVED_TASKS.md#обеспеченность-районов-стоянками-такси) |
| Обеспеченность районов остановками/маршрутами НГПТ | `Configs/DataMosTransitStopsDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание кейса](docs/SOLVED_TASKS.md#обеспеченность-районов-остановками-и-маршрутными-записями-нгпт) |
| Сводная проверка набора платных парковок | `Configs/DataMosStreetParking.json` | Табличная проверка качества и совместимости | [описание кейса](docs/SOLVED_TASKS.md#сводная-проверка-набора-платных-парковок) |

Полная страница с решёнными задачами, ожидаемыми файлами результатов и ссылками на документацию: [`docs/SOLVED_TASKS.md`](docs/SOLVED_TASKS.md).

---

## Примеры использования / Example Use Cases:

- Кластеризация городских районов по паттернам передвижения
- Обнаружение аномалий в транспортных потоках
- Выявление подозрительных транзакций в системе оплаты проезда
- Логистическая оптимизация размещения транспортных хабов
- Оценка обеспеченности районов парковками, пунктами велопроката и другими транспортными объектами с учётом населения

---

- Clustering of urban districts based on mobility patterns
- Anomaly detection in transportation flows
- Fraud detection in fare collection systems
- Logistic optimization for transport hub placement
- District provision analysis for parking, bike rental and other transport objects using population data


**License:** MIT

**Author:** [Mark Bulygin]

**Contact:** [messimm@yandex.ru]
