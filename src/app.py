#!/usr/bin/python
import json
import parser
import psycopg2

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from db import close_db
from flask import Flask
from scraper import flights
from scraper.scraper import scrape_flight_informations

#################################################################

def load_config(path):
    with open(path) as f:
        return json.load(f)

config = load_config('../resources/config.json')

#################################################################

def create_app(config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=config['postgres'])
    app.register_blueprint(flights.bp)
    app.teardown_appcontext(close_db)

    return app

app = create_app(config)

#################################################################

def schedule_jobs(config):
    scheduler = BackgroundScheduler()

    def job(from_date, to_date, departure_station, arrival_station):
        with app.app_context():
            scrape_flight_informations(from_date, 
                                       to_date, 
                                       departure_station, 
                                       arrival_station)

    for fmi in config['flights']:
        print(f'Scheduling job: {fmi["departure_station"]} -> {fmi["arrival_station"]}, between {fmi["from_date"]} and {fmi["to_date"]}...')
        from_date = datetime.strptime(fmi['from_date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(fmi['to_date'], '%Y-%m-%d').date()
        scheduler.add_job(job,
                          trigger='interval',
                          args=[from_date,
                                to_date,
                                fmi['departure_station'],
                                fmi['arrival_station']],
                          minutes=60)

    scheduler.start()

    return scheduler

scheduler = schedule_jobs(config)

#################################################################
