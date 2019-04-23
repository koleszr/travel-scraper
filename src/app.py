#!/usr/bin/python
import psycopg2

from apscheduler.schedulers.background import BackgroundScheduler
from common.config import Config
from common.dal.travel_db import DataAccessLayer
from common.flight.flight_info import FlightInfo
from common.utils import json_utils
from datetime import datetime
from flask import Flask, jsonify
from scraper.scraper import scrape_flight_informations

config = Config('../resources/config.json')
db_config = config.postgres_config

dal = DataAccessLayer(dbname=db_config.dbname,
                      user=db_config.user,
                      password=db_config.password,
                      host=db_config.host,
                      port=db_config.port)

def schedule_jobs(db):
    scheduler = BackgroundScheduler()

    for fmi in config.flight_meta_infos:
        print(f'Scheduling job: {fmi.departure_station}, {fmi.arrival_station}, {fmi.from_date}, {fmi.to_date}...')
        scheduler.add_job(scrape_flight_informations,
                          trigger='interval',
                          args=[db,
                                fmi.from_date,
                                fmi.to_date,
                                fmi.departure_station,
                                fmi.arrival_station],
                          minutes=30)

    scheduler.start()

schedule_jobs(dal)

app = Flask("travel-scraper")

@app.route("/cheapest/<departure_station>/<arrival_station>")
def cheapest(departure_station, arrival_station):
    print('Getting cheapest flights...')
    cheapest_flights = dal.select(
        f'''
        SELECT *
        FROM flight_info
        WHERE 
        price = (SELECT MIN(price) FROM flight_info WHERE departure_station = %s AND arrival_station = %s) AND
        departure_station = %s AND
        arrival_station = %s;
        ''',
        (departure_station, arrival_station, departure_station, arrival_station),
        lambda f: FlightInfo.from_tuple(f)
    )
    return jsonify([json_utils.as_json(f) for f in cheapest_flights])

@app.route("/flights/<departure_station>/<arrival_station>/<date>")
def flights(departure_station, arrival_station, date):
    print(f'Getting flights @ {date}...')
    flights = dal.select(
        f'''
        SELECT * FROM flight_info 
        WHERE
        departure_station = %s AND
        arrival_station = %s AND
        departure_dt BETWEEN %s AND %s;
        ''',
        (departure_station, arrival_station, f'{date} 00:00:00', f'{date} 23:59:59'),
        lambda f: FlightInfo.from_tuple(f)
    )
    x = [json_utils.as_json(f) for f in flights]
    return jsonify(x)
