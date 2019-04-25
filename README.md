# travel-scraper

## Scheduled jobs

Retrieves and persists Wizzair and Ryanair flight prices every 30 minutes (will be configurable).

## REST endpoints

**/flights/cheapest/<departure_station>/<arrival_station>** retrieves the cheapest price for flights from <departure_station> to <arrival_station>

**/flights/flights/<departure_station>/<arrival_station>/<date>** retrieves the prices for flights from <departure_station> to <arrival_station> at <date>

  Flight data are retrieved from the flight information persisted by the scheduled jobs.
