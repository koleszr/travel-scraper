class Flight():
    def __init__(self, departure_station, arrival_station, departure_dt, arrival_dt, price):
        self.departure_station = departure_station
        self.arrival_station = arrival_station
        self.departure_dt = departure_dt
        self.arrival_dt = arrival_dt
        self.price = price

    def __str__(self):
        return 'From: {} @ {}, to: {} @ {}, price: {}'.format(self.departure_station,
                                                               self.departure_dt,
                                                               self.arrival_station,
                                                               self.arrival_dt,
                                                               str(self.price))
    
class Price():
    def __init__(self, price, currency):
        self.price = price
        self.currency = currency

    def __str__(self):
        return '{} {}'.format(self.price, self.currency)

class FlightInfo:
    def __init__(self, company, query_dt, flight):
        self.company = company
        self.query_dt = query_dt
        self.flight = flight

    def tupled(self):
        return (self.company,
                self.query_dt,
                self.flight.departure_station,
                self.flight.arrival_station,
                self.flight.departure_dt,
                self.flight.arrival_dt,
                self.flight.price.price,
                self.flight.price.currency)

    def __str__(self):
        return f'{self.company}, {self.query_dt}, {str(self.flight)}'

    @staticmethod
    def from_tuple(f):
        price = Price(price=f[7], currency=f[8])
        flight = Flight(departure_station=f[3],
                        arrival_station=f[4],
                        departure_dt=f[5],
                        arrival_dt=f[6],
                        price=price)
        return FlightInfo(company=f[1],
                          query_dt=f[2],
                          flight=flight)
