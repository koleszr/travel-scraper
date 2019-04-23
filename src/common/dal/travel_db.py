import psycopg2
import time
from datetime import datetime

class DataAccessLayer:
    
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = self.try_connect()

    def try_connect(self):
        def go(attempts = 10):
            if attempts == 0:
                raise psycopg2.OperationalError(f'Couldn\'t connect to {self.dbname} after 10 attempts!')
            
            try:
                return psycopg2.connect(dbname=self.dbname,
                                        user=self.user,
                                        password=self.password,
                                        host=self.host,
                                        port=self.port)
            except:
                print(f'Couldn\'t connect to {self.dbname}. Retrying {10 - attempts + 1}/10...')
                time.sleep(10)
                go(attempts - 1)

        return go()

    def try_cursor(self):
        try:
            return self.connection.cursor()
        except psycopg2.InterfaceError:
            self.connection = self.try_connect()
            return self.try_cursor()
        
    def insert_many(self, table, columns, values_placeholder, rows):
        cur = self.try_cursor()
        columns_str = ', '.join(columns)
        cur.executemany(f'INSERT INTO {table} ({columns_str}) VALUES ({values_placeholder});', rows)

        self.connection.commit()
        cur.close()

    def select(self, select_statement, values, fn_to_obj):
        cursor = self.try_cursor()
        cursor.execute(select_statement, values)
        result = cursor.fetchall()
        cursor.close()
        return [fn_to_obj(r) for r in result]

    def close(self):
        self.connection.close()
