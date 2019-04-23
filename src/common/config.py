import json

from datetime import datetime

class Config:
    def __init__(self, path='../../resources/config.json'):
        with open(path) as f:
            config = json.load(f)
            self.postgres_config = PostgresConfig(config['postgres'])
            self.flight_meta_infos = [FlightMetaInfo(c) for c in config['flights']]
            

class PostgresConfig:
    def __init__(self, config):
        self.dbname = config['dbname']
        self.user = config['user']
        self.password = config['password']
        self.host = config['host']
        self.port = config['port']

class FlightMetaInfo:
    def __init__(self, config):
        self.departure_station = config['departure_station']
        self.arrival_station = config['arrival_station']
        self.from_date = datetime.strptime(config['from_date'], '%Y-%m-%d').date()
        self.to_date = datetime.strptime(config['to_date'], '%Y-%m-%d').date()
        print(self.from_date)
