import datetime
from sqlalchemy import create_engine,  MetaData, Table, select, insert, and_, or_

engine = create_engine("postgresql://postgres:postgres@localhost/restaurant")
metadata = MetaData()


class RestaurantModel():


    tables =  Table(
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
    availability = Table(
        'availability', 
        metadata, 
        autoload=True, 
        autoload_with=engine
    )

    def book_table(self, guests, date, phone_number, time):
        best_table = self.choose_best_table(date, time, guests)
        with engine.connect() as conn:
            conn.execute(
            insert(self.reservations),
            {"table_id": best_table[0][0], "guests": guests, "start": date, "phone_number": phone_number, "time": time},
        )
        
        
    
    def check_status(self, reservation_id):
        query = select(self.reservations.c).where(self.reservations.c.reservation_id == reservation_id)
        results = engine.execute(query).fetchall()
        return results

    def cancel_reservation(self, reservation_id, phone_number):
        pass
    
    def change_reservation(self, reservation_id, phone_number, date, guests):
        pass

    def check_availability(self, date, guests):

        time = datetime.datetime.strptime(date, "%d.%m.%y")
        query = select(self.availability).join(self.tables).where(and_(self.availability.c.day == time, or_(self.tables.c.max_guests == guests + 1, self.tables.c.max_guests == guests)))
       
        results = engine.execute(query).fetchall()
        list_ = []
        for result in results:
            list_.append({"table_id": result[1], "hours": result[2]})
        
        return list_

    def add_availability(self, day):
        query = self.tables.select()
        tables = engine.execute(query).fetchall()
        records = []
        for table in tables:
            records.append({"day": day, "table_id":table[0], 'hours': ['12:00', '14:00', '16:00', '18:00', '20:00', '22:00']})
            
        with engine.connect() as conn:
            conn.execute(
            insert(self.availability),
            records,
        )
        
        print( f"added availability for {day}" )
    
    def choose_best_table(self, day, time, guests):
        availability = self.check_availability(day, guests)
        differences_set = []
        differences = []

        # Choosing best tables based on date, hour and number of guests
        for table in availability:
            for hour in table['hours']:
                hour_list = hour.split(":")         
                hour_int = int(hour_list[0]) * 3600 + int(hour_list[1]) * 60
                time_int = int(time.split(':')[0]) * 3600 + int(time.split(':')[1]) * 60
                difference = abs(hour_int - time_int)
                differences_set.append([table['table_id'], hour, difference])
                differences.append(difference)
            
        try:
            min_value = min(differences)
        except:
            return []
        mins = [i for i, x in enumerate(differences) if x == min_value]
        k = differences_set[mins[0]][0]
        best_tables = []
        for i in mins:
            if differences_set[i][0] != k:
                break
            best_tables.append(differences_set[i])

        return best_tables


r = RestaurantModel()
# print(r.check_availability('31.01.23', 3))
# r.add_availability('2023-01-31')
# print(r.check_status(1))
# print(r.choose_best_table('31.01.23', "18:42", 4)) 
r.book_table(2, "31.01.23", "530925823", "20:00")