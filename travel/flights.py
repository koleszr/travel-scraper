import datetime
import json

from travel.db import get_db
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor

bp = Blueprint('flights', __name__, url_prefix='/flights')

DAILY_CHEAPEST_AT_QUERY = f'''
SELECT *
FROM flight_info
WHERE
departure_dt::date = %s AND
price = (SELECT MIN(price) FROM flight_info WHERE departure_dt::date = %s AND departure_station = %s AND arrival_station = %s) AND
departure_station = %s AND
arrival_station = %s;
'''

DAILY_CHEAPEST_BETWEEN_QUERY = f'''
SELECT f.company, f.departure_dt, f.arrival_dt, f.price, f.currency FROM flight_info AS f
INNER JOIN (
SELECT departure_dt::date as ddt, min(price) as mp
FROM flight_info
WHERE departure_station = %s AND arrival_station = %s AND departure_dt::date BETWEEN %s AND %s
GROUP BY departure_dt::date
) cheapest
ON f.departure_dt::date = cheapest.ddt AND f.price = cheapest.mp
WHERE f.departure_station = %s AND f.arrival_station = %s AND f.departure_dt::date BETWEEN %s AND %s
GROUP BY f.price, f.departure_dt, f.arrival_dt, f.company, f.currency
ORDER BY f.departure_dt;
'''

FLIGHTS_QUERY = f'''
SELECT * FROM flight_info
WHERE departure_station = %s AND arrival_station = %s AND departure_dt::date = %s;
'''

def converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
    return o.__dict__

@bp.route('/cheapest/<departure_station>/<arrival_station>/<from_date>')
@bp.route('/cheapest/<departure_station>/<arrival_station>/<from_date>/<to_date>')
def cheapest(departure_station, arrival_station, from_date, to_date=None):
    if to_date is None:
        return daily_cheapest_at(departure_station, arrival_station, from_date)
    else:
        return daily_cheapest_between(departure_station, arrival_station, from_date, to_date)

def daily_cheapest_at(departure_station, arrival_station, date):
    print(f'Getting cheapest flight on {date}...')

    params = (date, date, departure_station, arrival_station, departure_station, arrival_station)

    db = get_db()

    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(DAILY_CHEAPEST_AT_QUERY, params)
    flights = cursor.fetchall()
    cursor.close()

    return jsonify(flights)

def daily_cheapest_between(departure_station, arrival_station, from_date, to_date):
    print(f'Getting cheapest flights between {from_date} and {to_date}...')

    params = (departure_station, arrival_station, from_date, to_date, departure_station, arrival_station, from_date, to_date)

    db = get_db()

    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(DAILY_CHEAPEST_BETWEEN_QUERY, params)
    flights = cursor.fetchall()
    cursor.close()

    return jsonify(flights)

@bp.route('/flights/<departure_station>/<arrival_station>/<date>')
def flights(departure_station, arrival_station, date):
    print(f'Getting flights @ {date}...')

    params = (departure_station, arrival_station, date)

    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(FLIGHTS_QUERY, params)

    flights = cursor.fetchall()
    cursor.close()

    return jsonify(flights)
