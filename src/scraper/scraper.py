import time

from common.flight.flight_info import FlightInfo
from datetime import date, datetime
from db import get_db
from scraper.flight_companies.ryanair import Ryanair
from scraper.flight_companies.wizzair import Wizzair

columns = ['company', 'query_dt', 'departure_station', 'arrival_station', 'departure_dt', 'arrival_dt', 'price', 'currency']
insert = f'INSERT INTO flight_info ({", ".join(columns)}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'


def scrape_flight_informations(start_date, end_date, departure_station, arrival_station):
    now = datetime.now()

    print(f'Getting flight information @ {now} from Wizzair and Ryanair. Departure station: {departure_station}, arrival station: {arrival_station}, between {start_date} and {end_date}!')

    ryanair_flight_info = []
    try:
        ryanair = Ryanair(departure_station, arrival_station, 2)
        ryanair_flights = ryanair.get_flights_between(start_date, end_date)
        ryanair_flight_info = [FlightInfo('Ryanair', now, f) for f in ryanair_flights]
    except Exception as e:
        print(f'Error while getting flights from Wizzair: {e}')

    wizzair_flight_info = []
    try:
        wizzair = Wizzair(departure_station, arrival_station, 2)
        wizzair_flights = wizzair.get_flights_between(start_date, end_date)
        wizzair_flight_info = [FlightInfo('Wizzair', now, f) for f in wizzair_flights]    
    except Exception as e:
        print(f'Error while getting flights from Wizzair: {e}')

    flight_info = ryanair_flight_info + wizzair_flight_info

    print(f'Persisting {len(ryanair_flight_info)} Ryanair and {len(wizzair_flight_info)} Wizzair flights!')

    db = get_db()
    cursor = db.cursor()
    cursor.executemany(insert, [f.tupled() for f in flight_info])
    db.commit()
    cursor.close()
