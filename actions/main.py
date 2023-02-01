import datetime
from sqlalchemy import create_engine,  MetaData, Table, select, insert, and_, or_, update, bindparam

engine = create_engine("postgresql://postgres:postgres@localhost/restaurant")
metadata = MetaData()


class RestaurantModel():

    # Database tables
    tables =  Table('tables', metadata, autoload=True, autoload_with=engine)
    reservations = Table('reservations', metadata, autoload=True, autoload_with=engine)
    availability = Table('availability', metadata, autoload=True, autoload_with=engine)

    def book_table(self, guests, date, phone_number, time):
        best_table = self.choose_best_tables(date, time, guests)

        same_hour = False
        if len(best_table) == 0: return {"message": f"no available tables for {date}"}
        if len(best_table) == 1 and best_table[0][1] == time: same_hour = True
        if len(best_table) > 1 or len(best_table) == 1 and best_table[0][1] != time:
            available_hours = [table[1] for table in best_table]
            print(available_hours)
            return {"message": f"This hour is not available.\nAvailable hours for {date}: "}


        # try:
        #     query = select(self.availability.c.hours).where(and_(self.availability.c.day == date, self.availability.c.table_id == best_table[0][0]))
        #     hours = engine.execute(query).fetchall()
        # except:
        #     return 'no available tables for this date'
        
        # new_list = hours[0][0]
        # try:
        #     new_list.remove(time)
            
        #     if len(new_list) == 0:
        #         new_list = ['']

        #     new_date = datetime.datetime.strptime(date, '%d.%m.%y').strftime('%y-%m-%d')
            
        #     engine.execute(f"UPDATE availability SET hours = ARRAY {new_list} WHERE availability.day = '20{new_date}' AND availability.table_id = {best_table[0][0]}")

        #     with engine.connect() as conn:
        #         conn.execute(
        #         insert(self.reservations),
        #         {"table_id": best_table[0][0], "guests": guests, "start": date, "phone_number": phone_number, "time": time},
        #     )
        #     return f'successfully booked table at {date} {time} for {guests} guests'
        # except:
        #     return 'could not complete reservation'

    def check_status(self, reservation_id):
        query = select(self.reservations.c.status).where(self.reservations.c.reservation_id == reservation_id)
        results = engine.execute(query).fetchall()
        return results

    def cancel_reservation(self, reservation_id, phone_number):
        pass
    
    def change_reservation(self, reservation_id, phone_number, date, guests):
        pass

    def check_availability(self, date, guests, details = False):
        available_hours = []
        details_list = []
        time = datetime.datetime.strptime(date, "%d.%m.%y")
        query = select(self.availability).join(self.tables).where(and_(self.availability.c.day == time, or_(self.tables.c.max_guests == guests + 1, self.tables.c.max_guests == guests)))
        results = engine.execute(query).fetchall()
        if results == []: return []

        if details == False:
            for table in results:
                for hour in table[2]:
                    available_hours.append(hour)
            # return list of available hours without duplicates
            return list(set(available_hours))

        else:
            for result in results:
                details_list.append({"table_id": result[1], "hours": result[2]})
            return details_list   

    def add_availability(self, day):
        query = self.tables.select()
        tables = engine.execute(query).fetchall()
        records = []
        result = engine.execute(
            select(self.availability)
            .where(self.availability.c.day == day)).fetchall()
        if result == []:
            for table in tables: 
                records.append({
                "day": day, 
                "table_id":table[0], 
                'hours': ['12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
            })
            with engine.connect() as conn:
                conn.execute(
                insert(self.availability),
                records,
            )
            print( f"added availability for {day}")

        else:
            print(f"availability for {day} already exist")
    
    def choose_best_tables(self, day, time, guests):
        availability = self.check_availability(day, guests, True)
        differences_set = []
        differences = []

        # Choosing best tables based on date, hour and number of guests
        try:
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

        except:
            return []


r = RestaurantModel()
# print(r.check_availability('02.02.23', 4))
# r.add_availability('2023-02-02')
# print(r.check_status(1))
# print(r.choose_best_tables('02.02.23', "18:42", 2)) 
print(r.book_table(5, "02.02.23", "530925823", "19:00"))

