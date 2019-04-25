import concurrent.futures
import json
import requests

from datetime import date, datetime, timedelta
from common.flight.flight import Flight, Price

class Wizzair():
    def __init__(self, departure_station, arrival_station, adult_count):
        self.departure_station = departure_station
        self.arrival_station = arrival_station
        self.adult_count = adult_count
    
    def flight_params(self, date):
        return {
            "isFlightChange": False,
            "isSeniorOrStudent": False,
            "flightList": [
                {
                    "departureStation": self.departure_station,
                    "arrivalStation": self.arrival_station,
                    "departureDate": str(date)
                }
            ],
            "adultCount": self.adult_count,
            "childCount": 0,
            "infantCount": 0,
            "wdc": False
        }

    def get_api_url(self):
        with requests.get('https://wizzair.com/static/metadata.json') as r:
            return r.json()['apiUrl']

    def get_flights_at(self, api_url, date):
        url = f'{api_url}/search/search'
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = self.flight_params(date)
        with requests.post(url, data=json.dumps(data), headers=headers) as r:
            return Wizzair.flights_from_json(r.json())

    def get_flights_between(self, start_date, end_date):
        api_url = self.get_api_url()
        days_between = (end_date - start_date).days
        dates = [start_date + timedelta(days=dt) for dt in range(days_between + 1)]
        flights = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=days_between+1) as executor:
            flights_future = [executor.submit(self.get_flights_at, api_url, date) for date in dates]

            for f in concurrent.futures.as_completed(flights_future):
                try:
                    flights.extend(f.result())
                except Exception as e:
                    print(f'Exception was thrown while getting results from Wizzair: {e}')
                    
        return flights

    @staticmethod
    def flights_from_json(json):
        flights = []
        for f in json['outboundFlights']:
            departure_station = f['departureStation']
            arrival_station = f['arrivalStation']
            dt_format = '%Y-%m-%dT%H:%M:%S' # Example: 2019-08-26T06:05:00
            departure_dt = datetime.strptime(f['departureDateTime'], dt_format)
            arrival_dt = datetime.strptime(f['arrivalDateTime'], dt_format)

            prices = []
            for fare in f['fares']:
                p = fare['basePrice']
                prices.append(Price(price = p['amount'], currency = p['currencyCode']))

            flights.append(Flight(departure_station = departure_station,
                                  arrival_station = arrival_station,
                                  departure_dt = departure_dt,
                                  arrival_dt = arrival_dt,
                                  price = min(prices, key=lambda p: p.price)))

        return flights

