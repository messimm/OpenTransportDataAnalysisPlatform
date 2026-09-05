# OpenTransportDataPlatform

**OpenTransportDataPlatform** — открытая модульная Python-платформа для
транспортной аналитики, анализа городской мобильности и открытых транспортных
данных: пассажиропотоки, валидаторные данные, мобильные агрегаты, геоданные,
реестры инфраструктуры, наборы `data.mos.ru` и районные показатели.

*Open-source Python platform for transport data analysis, urban mobility,
public transport analytics, geospatial open data and reproducible research.*

**Кому полезно:** транспортным аналитикам, исследователям городской мобильности, инженерам данных, специалистам по планированию и кодовым агентам, которым нужно быстро воспроизвести расчёты по транспортным данным.

---

## Исследовательский статус и некоммерческое использование

Проект основан на материалах диссертационной работы Марка Валерьевича Булыгина, опубликованных на странице МФТИ: [mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich](https://mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich).

Платформа и примеры предназначены для **некоммерческого исследовательского использования**. Если какой-либо набор данных, пример, ссылка или описание должны быть удалены из репозитория, напишите на почту проекта: `messimm@yandex.ru`.

---

## Что можно делать

| Направление | Примеры задач | Готовые модули |
| --- | --- | --- |
| Подключение транспортных данных | Читать CSV/JSON, API `data.mos.ru`, локальные кэши, районное население | `DataLoaders/*` |
| Контроль качества | Фильтровать пустые районы, невалидные координаты, некорректные значения | `DataCheckers/*` |
| Аналитика потоков | Аномалии, потенциальный фрод, типология районов, использование метро | `DataAnalyzers/*` |
| Обеспеченность районов | Объекты/места на 100 тыс. жителей, TOP/BOTTOM районов, уровни обеспеченности | `DistrictObjectProvisionAnalysis` |
| Отчёты и визуализация | CSV, Excel, текстовые TOP/BOTTOM отчёты, scatter/bar charts, PNG-карты | `DataVisualizers/*` |

---

## Быстрый старт

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. Запустить готовый офлайн-пример

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingDistrictProvision.json
```

По умолчанию демонстрационные конфиги используют fixture-данные из `tests/fixtures/`, поэтому их можно запускать без внешней сети. Для актуальных данных замените `data_path` в конфиге на локальную CSV/JSON-выгрузку или настройте доступ к API `data.mos.ru`.

### 3. Скачать актуальные данные и получить результат одной командой

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingOnline.json
```

Команда обращается к официальному API `data.mos.ru`, скачивает до 1000 строк
набора платных парковок, нормализует данные, выполняет проверку и сохраняет
`outputs/online_street_parking_summary.csv`. Если портал требует ключ API,
передайте его без изменения конфига:

```bash
DATA_MOS_API_KEY="ваш-ключ" python launch_from_cfg.py Configs/DataMosStreetParkingOnline.json
```

Для online-примера необходим доступ к `https://apidata.mos.ru`. При сетевой
ошибке загрузчик выводит понятное сообщение и предлагает использовать локальный
`data_path`. Для технической диагностики добавьте флаг `--debug`.

Посмотреть все доступные конфиги можно без запуска анализа:

```bash
python launch_from_cfg.py --list-configs
```

### 4. Запустить все готовые районные кейсы

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingDistrictProvision.json
python launch_from_cfg.py Configs/DataMosBikeRentalDistrictProvision.json
python launch_from_cfg.py Configs/DataMosTaxiParkingDistrictProvision.json
python launch_from_cfg.py Configs/DataMosTransitStopsDistrictProvision.json
```

Результаты сохраняются в автоматически создаваемую папку `outputs/`: CSV-сводки,
TOP/BOTTOM-10 отчёты и PNG-карты объектов. Папка не отслеживается Git.

---

## Поддерживаемые источники данных

| Источник | Адаптер | Для чего используется |
| --- | --- | --- |
| [Платные парковки на улично-дорожной сети, dataset 623](https://data.mos.ru/opendata/623) | `MoscowStreetParkingLoader` | Геореестр парковок, анализ ёмкости и обеспеченности |
| [Парковки такси, dataset 621](https://data.mos.ru/opendata/621) | `MoscowTaxiParkingLoader` | Обеспеченность районов стоянками такси |
| [Прокат велосипедов, dataset 1777](https://data.mos.ru/opendata/1777) | `MoscowBikeRentalLoader` | Обеспеченность районов пунктами велопроката |
| [Маршруты и остановки НГПТ, dataset 60661](https://data.mos.ru/opendata/60661) | `MoscowTransitStopsRoutesLoader` | Справочные маршрутно-остановочные сценарии |
| CSV/JSON с населением районов | `DistrictPopulationLoader` | Нормировка объектов на 100 тыс. жителей |
| Локальные валидаторные/мобильные данные | `MetroDataLoader`, `MobileOperatorsLoader` | Аномалии, фрод, кластеризация, использование метро |

Подробности: [`DataLoaders/README.md`](DataLoaders/README.md), [`DataLoaders/DATAMOS.md`](DataLoaders/DATAMOS.md).

---

## Решённые кейсы

| Кейc | Конфиг | Что получается | Документация |
| --- | --- | --- | --- |
| Обеспеченность районов платными парковками | `Configs/DataMosStreetParkingDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-платными-парковками) |
| Обеспеченность районов пунктами велопроката | `Configs/DataMosBikeRentalDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-пунктами-велопроката) |
| Обеспеченность районов стоянками такси | `Configs/DataMosTaxiParkingDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-стоянками-такси) |
| Обеспеченность районов остановками/маршрутами НГПТ | `Configs/DataMosTransitStopsDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-остановками-и-маршрутными-записями-нгпт) |
| Сводная проверка набора платных парковок | `Configs/DataMosStreetParking.json` | Табличная проверка структуры и совместимости | [описание](docs/SOLVED_TASKS.md#сводная-проверка-набора-платных-парковок) |
| Online-проверка актуальных парковок | `Configs/DataMosStreetParkingOnline.json` | Автоматическая загрузка из API и CSV-сводка | [описание](docs/SOLVED_TASKS.md#online-проверка-актуального-набора-парковок) |

Полная страница кейсов: [`docs/SOLVED_TASKS.md`](docs/SOLVED_TASKS.md).

---

## Как устроен pipeline

Конфигурация собирает четыре группы модулей:

```json
{
  "DataLoaders": [{"Name": "...", "Parameters": {}}],
  "DataCheckers": [{"Name": "...", "Parameters": {}}],
  "DataAnalyzers": [{"Name": "...", "Parameters": {}}],
  "DataVisualizers": [{"Name": "...", "Parameters": {}}]
}
```

`launch_from_cfg.py` импортирует классы по имени, создаёт загрузчики/проверки/анализатор/визуализаторы и передаёт результат анализа в визуализаторы. Один анализатор может вернуть один результат или список результатов; число визуализаторов должно совпадать с числом результатов.

### Основные принципы

- **Конфигурация вместо склейки кода:** готовый сценарий описывается одним JSON-файлом.
- **Единый табличный контракт:** загрузчики нормализуют источники в `pandas.DataFrame`.
- **Разделение ответственности:** чтение, проверка, анализ и представление результата находятся в разных модулях.
- **Воспроизводимость:** демонстрационные конфиги работают на маленьких локальных fixtures без сети.
- **Расширяемость:** новый источник или отчёт добавляется отдельным классом и подключается по имени в конфиге.

### Проверка установки

```bash
python -m unittest discover -s tests -v
```

---

## Для кодовых агентов: Codex, Claude Code и другие

Если вы специалист по транспорту и хотите использовать кодового агента, можно дать ему ссылку на репозиторий и сформулировать задачу на профессиональном языке. Для агентов добавлены отдельные инструкции:

- [`AGENTS.md`](AGENTS.md) — краткая карта репозитория, правила изменения кода и типовые маршруты работы.
- [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) — как переводить транспортную постановку задачи в модули платформы.

Примеры запросов к агенту:

```text
Добавь кейс обеспеченности районов зарядными станциями: нужен loader для нового CSV, фильтр координат, расчёт объектов на 100 тыс. жителей, TOP-10 отчёт и PNG-карта.
```

```text
Проверь, совместим ли новый набор data.mos.ru с DistrictObjectProvisionAnalysis. Если нет — добавь адаптер и конфиг запуска.
```

```text
Собери pipeline для анализа аномалий пассажиропотока по валидаторным данным и сохрани отчёт в CSV.
```

---

## Документация по модулям

| Раздел | Документ |
| --- | --- |
| Загрузчики данных | [`DataLoaders/README.md`](DataLoaders/README.md) |
| Наборы `data.mos.ru` | [`DataLoaders/DATAMOS.md`](DataLoaders/DATAMOS.md) |
| Проверки и фильтры | [`DataCheckers/README.md`](DataCheckers/README.md) |
| Аналитические модули | [`DataAnalyzers/Readme.md`](DataAnalyzers/Readme.md) |
| Визуализаторы | [`DataVisualizers/README.md`](DataVisualizers/README.md) |
| Решённые задачи | [`docs/SOLVED_TASKS.md`](docs/SOLVED_TASKS.md) |
| Руководство для агентов | [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) |
| Видимость в поиске и GitHub Topics | [`docs/DISCOVERY.md`](docs/DISCOVERY.md) |

---

## English summary

**OpenTransportDataPlatform** is a modular open-source platform for transport data analysis. It supports reusable loaders, checkers, analyzers and visualizers, including adapters for Moscow `data.mos.ru` datasets and district-level provision workflows. The project is intended for non-commercial research use and is based on dissertation materials by Mark Valerievich Bulygin published on the MIPT website.

If any dataset, example, link or description should be removed, please contact `messimm@yandex.ru`.

**License:** MIT  
**Author:** Mark Bulygin  
**Contact:** messimm@yandex.ru

**Search keywords:** transport data analysis, urban mobility, public transport
analytics, mobility analysis, geospatial open data, Moscow transport,
`data.mos.ru`, транспортная аналитика, городская мобильность, транспортные
данные, пассажиропоток, обеспеченность транспортной инфраструктурой.
**OpenTransportDataPlatform** — открытая модульная платформа для анализа городских транспортных данных: валидаторные данные, мобильные агрегаты, статические реестры объектов, открытые наборы `data.mos.ru` и районные показатели. Платформа помогает быстро собирать исследовательские pipeline из загрузчиков, проверок качества, аналитических модулей и визуализаторов.

**Кому полезно:** транспортным аналитикам, исследователям городской мобильности, инженерам данных, специалистам по планированию и кодовым агентам, которым нужно быстро воспроизвести расчёты по транспортным данным.

---

## Исследовательский статус и некоммерческое использование

Проект основан на материалах диссертационной работы Марка Валерьевича Булыгина, опубликованных на странице МФТИ: [mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich](https://mipt.ru/institute/departments/dissertatio/soiskateli/tn/bulygin-mark-valerevich).

Платформа и примеры предназначены для **некоммерческого исследовательского использования**. Если какой-либо набор данных, пример, ссылка или описание должны быть удалены из репозитория, напишите на почту проекта: `messimm@yandex.ru`.

---

## Что можно делать

| Направление | Примеры задач | Готовые модули |
| --- | --- | --- |
| Подключение транспортных данных | Читать CSV/JSON, API `data.mos.ru`, локальные кэши, районное население | `DataLoaders/*` |
| Контроль качества | Фильтровать пустые районы, невалидные координаты, некорректные значения | `DataCheckers/*` |
| Аналитика потоков | Аномалии, потенциальный фрод, типология районов, использование метро | `DataAnalyzers/*` |
| Обеспеченность районов | Объекты/места на 100 тыс. жителей, TOP/BOTTOM районов, уровни обеспеченности | `DistrictObjectProvisionAnalysis` |
| Отчёты и визуализация | CSV, Excel, текстовые TOP/BOTTOM отчёты, scatter/bar charts, PNG-карты | `DataVisualizers/*` |

---

## Быстрый старт

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. Запустить готовый пример обеспеченности районов

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingDistrictProvision.json
```

По умолчанию демонстрационные конфиги используют fixture-данные из `tests/fixtures/`, поэтому их можно запускать без внешней сети. Для актуальных данных замените `data_path` в конфиге на локальную CSV/JSON-выгрузку или настройте доступ к API `data.mos.ru`.

### 3. Запустить все готовые районные кейсы

```bash
python launch_from_cfg.py Configs/DataMosStreetParkingDistrictProvision.json
python launch_from_cfg.py Configs/DataMosBikeRentalDistrictProvision.json
python launch_from_cfg.py Configs/DataMosTaxiParkingDistrictProvision.json
python launch_from_cfg.py Configs/DataMosTransitStopsDistrictProvision.json
```

Результаты: CSV-сводки, TOP/BOTTOM-10 отчёты и PNG-карты объектов.

---

## Поддерживаемые источники данных

| Источник | Адаптер | Для чего используется |
| --- | --- | --- |
| [Платные парковки на улично-дорожной сети, dataset 623](https://data.mos.ru/opendata/623) | `MoscowStreetParkingLoader` | Геореестр парковок, анализ ёмкости и обеспеченности |
| [Парковки такси, dataset 621](https://data.mos.ru/opendata/621) | `MoscowTaxiParkingLoader` | Обеспеченность районов стоянками такси |
| [Прокат велосипедов, dataset 1777](https://data.mos.ru/opendata/1777) | `MoscowBikeRentalLoader` | Обеспеченность районов пунктами велопроката |
| [Маршруты и остановки НГПТ, dataset 60661](https://data.mos.ru/opendata/60661) | `MoscowTransitStopsRoutesLoader` | Справочные маршрутно-остановочные сценарии |
| CSV/JSON с населением районов | `DistrictPopulationLoader` | Нормировка объектов на 100 тыс. жителей |
| Локальные валидаторные/мобильные данные | `MetroDataLoader`, `MobileOperatorsLoader` | Аномалии, фрод, кластеризация, использование метро |

Подробности: [`DataLoaders/README.md`](DataLoaders/README.md), [`DataLoaders/DATAMOS.md`](DataLoaders/DATAMOS.md).

---

## Решённые кейсы

| Кейc | Конфиг | Что получается | Документация |
| --- | --- | --- | --- |
| Обеспеченность районов платными парковками | `Configs/DataMosStreetParkingDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-платными-парковками) |
| Обеспеченность районов пунктами велопроката | `Configs/DataMosBikeRentalDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-пунктами-велопроката) |
| Обеспеченность районов стоянками такси | `Configs/DataMosTaxiParkingDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-стоянками-такси) |
| Обеспеченность районов остановками/маршрутами НГПТ | `Configs/DataMosTransitStopsDistrictProvision.json` | CSV-сводка, TOP/BOTTOM-10, PNG-карта | [описание](docs/SOLVED_TASKS.md#обеспеченность-районов-остановками-и-маршрутными-записями-нгпт) |
| Сводная проверка набора платных парковок | `Configs/DataMosStreetParking.json` | Табличная проверка структуры и совместимости | [описание](docs/SOLVED_TASKS.md#сводная-проверка-набора-платных-парковок) |

Полная страница кейсов: [`docs/SOLVED_TASKS.md`](docs/SOLVED_TASKS.md).

---

## Как устроен pipeline

Конфигурация собирает четыре группы модулей:

```json
{
  "DataLoaders": [{"Name": "...", "Parameters": {}}],
  "DataCheckers": [{"Name": "...", "Parameters": {}}],
  "DataAnalyzers": [{"Name": "...", "Parameters": {}}],
  "DataVisualizers": [{"Name": "...", "Parameters": {}}]
}
```

`launch_from_cfg.py` импортирует классы по имени, создаёт загрузчики/проверки/анализатор/визуализаторы и передаёт результат анализа в визуализаторы. Один анализатор может вернуть один результат или список результатов; число визуализаторов должно совпадать с числом результатов.

---

## Для кодовых агентов: Codex, Claude Code и другие

Если вы специалист по транспорту и хотите использовать кодового агента, можно дать ему ссылку на репозиторий и сформулировать задачу на профессиональном языке. Для агентов добавлены отдельные инструкции:

- [`AGENTS.md`](AGENTS.md) — краткая карта репозитория, правила изменения кода и типовые маршруты работы.
- [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) — как переводить транспортную постановку задачи в модули платформы.

Примеры запросов к агенту:

```text
Добавь кейс обеспеченности районов зарядными станциями: нужен loader для нового CSV, фильтр координат, расчёт объектов на 100 тыс. жителей, TOP-10 отчёт и PNG-карта.
```

```text
Проверь, совместим ли новый набор data.mos.ru с DistrictObjectProvisionAnalysis. Если нет — добавь адаптер и конфиг запуска.
```

```text
Собери pipeline для анализа аномалий пассажиропотока по валидаторным данным и сохрани отчёт в CSV.
```

---

## Документация по модулям

| Раздел | Документ |
| --- | --- |
| Загрузчики данных | [`DataLoaders/README.md`](DataLoaders/README.md) |
| Наборы `data.mos.ru` | [`DataLoaders/DATAMOS.md`](DataLoaders/DATAMOS.md) |
| Проверки и фильтры | [`DataCheckers/README.md`](DataCheckers/README.md) |
| Аналитические модули | [`DataAnalyzers/Readme.md`](DataAnalyzers/Readme.md) |
| Визуализаторы | [`DataVisualizers/README.md`](DataVisualizers/README.md) |
| Решённые задачи | [`docs/SOLVED_TASKS.md`](docs/SOLVED_TASKS.md) |
| Руководство для агентов | [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) |

---

## English summary

**OpenTransportDataPlatform** is a modular open-source platform for transport data analysis. It supports reusable loaders, checkers, analyzers and visualizers, including adapters for Moscow `data.mos.ru` datasets and district-level provision workflows. The project is intended for non-commercial research use and is based on dissertation materials by Mark Valerievich Bulygin published on the MIPT website.

If any dataset, example, link or description should be removed, please contact `messimm@yandex.ru`.

**License:** MIT  
**Author:** Mark Bulygin  
**Contact:** messimm@yandex.ru
