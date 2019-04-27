#!/usr/bin/python
import json
import parser
import psycopg2

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from travel.db import close_db
from travel.flights import bp as flights_blueprint
from travel.scraper import scrape_flight_informations

#################################################################

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_json(filename="db_config.json", silent=False)
    app.config.from_json(filename="flights_config.json", silent=False)
    app.register_blueprint(flights_blueprint)
    app.teardown_appcontext(close_db)

    CORS(app)

    return app

app = create_app()

#################################################################

def schedule_jobs():
    scheduler = BackgroundScheduler()

    def job(from_date, to_date, departure_station, arrival_station):
        with app.app_context():
            scrape_flight_informations(from_date, 
                                       to_date, 
                                       departure_station, 
                                       arrival_station)

    for fmi in app.config['FLIGHTS']:
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

scheduler = schedule_jobs()

#################################################################
