from sqlalchemy import create_engine, select, Table, MetaData

engine = create_engine("postgresql://postgres:postgres@localhost/restaurant")
metadata = MetaData(bind=None)


class Restaurant():
    tables = Table(
        'tables', 
        metadata, 
        autoload=True, 
        autoload_with=engine

    )
    reservations = Table(
        'reservations', 
        metadata, 
        autoload=True, 
        autoload_with=engine

    )
    
    def book_table(self, guests, date, phone_number):
        pass
    
    def check_status(self, reservation_id):
        pass
    
    def cancel_reservation(self, reservation_id, phone_number):
        pass
    
    def change_reservation(self, reservation_id, phone_number, date, guests):
        pass

    def check_availability(self, date):
        pass
    