import datetime
import json

from db import get_db
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor

bp = Blueprint('flights', __name__, url_prefix='/flights')

def converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
    return o.__dict__

@bp.route('/cheapest/<departure_station>/<arrival_station>/<date>')
def cheapest(departure_station, arrival_station, date):
    print('Getting cheapest flights...')

    from_dt = f'{date} 00:00:00'
    to_dt = f'{date} 23:59:59'

    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        f'''
        SELECT *
        FROM flight_info
        WHERE 
        departure_dt BETWEEN %s AND %s AND
        price = (SELECT MIN(price) FROM flight_info WHERE departure_dt BETWEEN %s AND %s AND departure_station = %s AND arrival_station = %s) AND
        departure_station = %s AND
        arrival_station = %s;
        ''',
        (from_dt, to_dt, from_dt, to_dt, departure_station, arrival_station, departure_station, arrival_station)
    )

    flights = cursor.fetchall()
    cursor.close()

    return jsonify(flights)

@bp.route('/flights/<departure_station>/<arrival_station>/<date>')
def flights(departure_station, arrival_station, date):
    print(f'Getting flights @ {date}...')

    from_dt = f'{date} 00:00:00'
    to_dt = f'{date} 23:59:59'

    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        f'''
        SELECT * FROM flight_info 
        WHERE
        departure_station = %s AND
        arrival_station = %s AND
        departure_dt BETWEEN %s AND %s;
        ''',
        (departure_station, arrival_station, from_dt, to_dt)
    )

    flights = cursor.fetchall()
    cursor.close()

    return jsonify(flights)
