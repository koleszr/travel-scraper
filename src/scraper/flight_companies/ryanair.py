import concurrent.futures
import json
import re
import requests

from datetime import date, datetime, timedelta
from common.flight.flight import Flight, Price

'''
Prices between start date and start date + FlexDaysOut
https://desktopapps.ryanair.com/v4/hu-hu/availability?ADT=1&CHD=0&DateOut=2019-07-31&Destination=BCN&FlexDaysOut=4&INF=0&IncludeConnectingFlights=true&Origin=BUD&RoundTrip=false&TEEN=0&ToUs=AGREED&exists=false&pretty=true

Cheapest in a range
https://services-api.ryanair.com/farfnd/3/oneWayFares?&arrivalAirportIataCode=BCN&departureAirportIataCode=BUD&language=hu&limit=16&market=hu-hu&offset=0&outboundDepartureDateFrom=2019-08-01&outboundDepartureDateTo=2019-08-31

Cheapest per day in a month
https://services-api.ryanair.com/farfnd/3/oneWayFares/BUD/BCN/cheapestPerDay?market=hu-hu&outboundMonthOfDate=2019-06-01
'''

class Ryanair():
    def __init__(self, departure_station, arrival_station, adult_count):
        self.departure_station = departure_station
        self.arrival_station = arrival_station
        self.adult_count = adult_count

    def flight_params(self, *args, **kwargs):
        return {
            "ADT": self.adult_count,
            "CHD": 0,
            "INF": 0,
            "TEEN": 0,
            "DateOut": str(kwargs['start_date']),
            "Origin": self.departure_station,
            "Destination": self.arrival_station,
            "FlexDaysOut": kwargs['flex_days_out'],
            "IncludeConnectingFlights": False,
            "RoundTrip": False,
            "ToUs": "AGREED",
            "exists": False
        }

    def get_flight(self, params=None):
        with requests.get('https://desktopapps.ryanair.com/v4/hu-hu/availability', params=params) as r:
            return Ryanair.flights_from_json(r.json())
        
    def get_flights_between(self, start_date, end_date):
        def dates_to_flex_days(start_date, days_left, acc = []):
            if days_left == 0:
                return acc
            else:
                acc.append((start_date, days_left if days_left < 6 else 6))
                return dates_to_flex_days(start_date + timedelta(days=7),
                                          0 if days_left < 7 else days_left - 7,
                                          acc)

        days_between = (end_date - start_date).days # max 6 at a time
        dts = dates_to_flex_days(start_date, days_between)

        with concurrent.futures.ThreadPoolExecutor(max_workers=days_between + 1) as executor:            
            dts = dates_to_flex_days(start_date, days_between, [])
            params = [self.flight_params(start_date=dt[0], flex_days_out=dt[1]) for dt in dts]
            flights_future = [executor.submit(self.get_flight, param) for param in params]
            
            flights = []

            for f in concurrent.futures.as_completed(flights_future):
                try:
                    flights.extend(f.result())
                except Exception as e:
                    print(f'Exception was thrown while getting results from Ryanair: {e}')

            return flights

    @staticmethod
    def flights_from_json(json):
        flights = []
        
        trip = json['trips'][0]
        departure_station = trip['origin']
        arrival_station = trip['destination']

        for date in trip['dates']:
            for flight in date['flights']:
                flight_key = flight['flightKey']
                date_format = '[0-9]{2}/[0-9]{2}/[0-9]{4} [0-9]{2}:[0-9]{2}'
                regex = re.search('.*~(?P<d_dt>{})~.*~(?P<a_dt>{})'.format(date_format, date_format), flight_key)
                dt_format = '%m/%d/%Y %H:%M'  # Example: 08/20/2019 20:15
                departure_dt = datetime.strptime(regex.group('d_dt'), dt_format)
                arrival_dt = datetime.strptime(regex.group('a_dt'), dt_format)

                prices = []
                for fare in flight['regularFare']['fares']:
                    prices.append(Price(price=fare['amount'], currency=json['currency']))

                flights.append(Flight(departure_station=departure_station,
                                      arrival_station=arrival_station,
                                      departure_dt=departure_dt,
                                      arrival_dt=arrival_dt,
                                      price=min(prices, key=lambda p: p.price)))

        return flights
                
