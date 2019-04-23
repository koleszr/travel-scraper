import time

from common.dal.travel_db import DataAccessLayer
from common.flight.flight import Flight
from common.flight.flight_info import FlightInfo
from datetime import date, datetime
from scraper.flight_companies.ryanair import Ryanair
from scraper.flight_companies.wizzair import Wizzair


def scrape_flight_informations(db, start_date, end_date, departure_station, arrival_station):
    now = datetime.now()
    print(f'Getting flight information @ {now} from Wizzair and Ryanair. Departure station: {departure_station}, arrival station: {arrival_station}, between {start_date} and {end_date}!')
    
    ryanair = Ryanair(departure_station, arrival_station, 2)
    ryanair_flights = ryanair.get_flights_between(start_date, end_date)
    ryanair_flight_info = [FlightInfo('Ryanair', now, f) for f in ryanair_flights]

    wizzair = Wizzair(departure_station, arrival_station, 2)
    wizzair_flights = wizzair.get_flights_between(start_date, end_date)
    wizzair_flight_info = [FlightInfo('Wizzair', now, f) for f in wizzair_flights]    

    flight_info = ryanair_flight_info + wizzair_flight_info

    for f in flight_info:
        print(f)

    print('Persisting flight information')
    columns = ['company', 'query_dt', 'departure_station', 'arrival_station', 'departure_dt', 'arrival_dt', 'price', 'currency']

    db.insert_many('flight_info', columns, '%s, %s, %s, %s, %s, %s, %s, %s', [f.tupled() for f in flight_info])
