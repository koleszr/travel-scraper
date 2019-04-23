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
