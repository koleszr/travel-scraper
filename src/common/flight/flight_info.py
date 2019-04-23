from common.flight.flight import Flight, Price

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
