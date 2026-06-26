# data.mos.ru transport adapters

Implemented adapters for primary Moscow transport-related open datasets:

| Adapter | Dataset | data.mos.ru URL | Typical analysis compatibility |
| --- | --- | --- | --- |
| `MoscowStreetParkingLoader` | 623, paid street parking | https://data.mos.ru/opendata/623 | Static geospatial inventory, capacity summaries, filtering, Excel export |
| `MoscowTaxiParkingLoader` | 621, taxi parking | https://data.mos.ru/opendata/621 | Static geospatial inventory, filtering, coverage previews |
| `MoscowBikeRentalLoader` | 1777, bicycle rental points | https://data.mos.ru/opendata/1777 | Static geospatial inventory, filtering, network/non-network split if field is available |
| `MoscowTransitStopsRoutesLoader` | 60661, public transport routes/stops schedules | https://data.mos.ru/opendata/60661 | Route/stop reference analysis and filtering; not a time-series passenger-flow source |

The platform already contains anomaly, fraud and hood-type analyzers aimed at
time-series validator/mobile-flow datasets. The data.mos.ru adapters above are
mostly static registries, so they are directly compatible with generic dataframe
summaries, column filters and geospatial visualisation/export workflows. They are
not directly compatible with passenger-flow anomaly/fraud methods unless joined
with operational counts that provide timestamps and demand values.

If the public API is unavailable in the execution environment, pass `data_path`
with a cached CSV or JSON export from the dataset page. The loader first reads
local caches and only then calls the API.
