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
        
        t = date
        t = t.split('.')
        t[2] = "20" + t[2] 
        today = datetime.datetime.now().date()
        t = datetime.datetime(int(t[2]), int(t[1]), int(t[0])).date()

        if today > t: return{"message": "date cannot be in the past"}
        if len(best_table) == 0: return {"message": f"no available tables for {date}"}
        if len(best_table) > 1 or len(best_table) == 1 and best_table[0][1] != time:
            available_hours = [table[1] for table in best_table]
            return {"message": f"This hour is not available.\nBest option for you at {date}: {available_hours}"}

        if len(best_table) == 1 and best_table[0][1] == time: 
                query = select(self.availability.c.hours).where(
                    and_(self.availability.c.day == date, self.availability.c.table_id == best_table[0][0]))

                hours = engine.execute(query).fetchall()
                new_list = hours[0][0]
                new_list.remove(time)
                new_date = datetime.datetime.strptime(date, '%d.%m.%y').strftime('%y-%m-%d')
                if len(new_list) == 0:  
                    engine.execute(f"UPDATE availability SET hours = ARRAY {['']} WHERE availability.day = '20{new_date}' AND availability.table_id = {best_table[0][0]}")
                else:
                    engine.execute(f"UPDATE availability SET hours = ARRAY {new_list} WHERE availability.day = '20{new_date}' AND availability.table_id = {best_table[0][0]}")

                with engine.connect() as conn:
                    conn.execute(
                    insert(self.reservations),
                    {"table_id": best_table[0][0], "guests": guests, "start": date, "phone_number": phone_number, "time": time},
                )
                reservation_number = engine.execute(select(self.reservations.c.reservation_id).where(
                    and_(self.reservations.c.table_id == best_table[0][0], self.reservations.c.guests == guests, self.reservations.c.start == date, self.reservations.c.phone_number  == phone_number, self.reservations.c.time == time, self.reservations.c.status == 'active')
                )).fetchall()
                
                return f'successfully booked table at {date} {time} for {guests} guests. Reservation number: {reservation_number[0][0]} '

    def check_status(self, reservation_id):

        query = select(self.reservations.c.status).where(self.reservations.c.reservation_id == reservation_id)
        results = engine.execute(query).fetchall()
        if len(results) == 0: return {"message": "Wrong reservation number"}

        return results[0][0]

    def cancel_reservation(self, reservation_id, phone_number):

        reservation = engine.execute(select(self.reservations).where(and_(self.reservations.c.reservation_id == reservation_id, 
        self.reservations.c.phone_number == phone_number,  
        self.reservations.c.status == 'active'))
        ).fetchall()
        
        if len(reservation) == 0: return {"message": "couldn't find your reservation"}
        engine.execute(f"UPDATE reservations SET status = 'cancelled' WHERE reservations.reservation_id = {reservation_id}")

        reservation_time = reservation[0][6]
        reservation_date = reservation[0][3]
        reservation_table = reservation[0][1]

        availability = engine.execute(select(self.availability).where(and_(self.availability.c.day == reservation_date, 
        self.availability.c.table_id == reservation_table))
        ).fetchall()

        available_hours = availability[0][2]
        
        if available_hours[0] == '': available_hours.remove('')
        if reservation_time not in available_hours: available_hours.append(reservation_time)

        engine.execute(f"UPDATE availability SET hours = ARRAY {available_hours} WHERE availability.day = '{reservation_date}' AND availability.table_id = {reservation_table}")

        return f"Successfully cancelled reservation"

    def change_reservation(self, reservation_id, phone_number, new_date, new_time, new_guests):

        reservation = engine.execute(select(self.reservations).where(and_(self.reservations.c.reservation_id == reservation_id, 
        self.reservations.c.phone_number == phone_number,  
        self.reservations.c.status == 'active'))
        ).fetchall()

        if len(reservation) == 0: return {"message": "couldn't find your reservation"}
        
        best_table = self.choose_best_tables(new_date, new_time, new_guests)
        
        if len(best_table) == 0: return {"message": f"no available tables for {new_date}"}
        if len(best_table) > 1 or len(best_table) == 1 and best_table[0][1] != new_time:
            available_hours = [table[1] for table in best_table]
            return {"message": f"This hour is not available.\nBest option on the selected day: {available_hours}"}

        if len(best_table) == 1 and best_table[0][1] == new_time: 
                hours_old = engine.execute(select(self.availability.c.hours).where(
                    and_(self.availability.c.day == reservation[0][3], self.availability.c.table_id == reservation[0][1]))).fetchall()[0][0]
                hours_new =  engine.execute(select(self.availability.c.hours).where(
                    and_(self.availability.c.day == new_date, self.availability.c.table_id == best_table[0][0]))).fetchall()[0][0]

                new_old_hours = hours_old[:]
                new_old_hours.append(reservation[0][6])
                new_hours_new = hours_new[:]
                new_hours_new.remove(new_time)
                
                new_date = datetime.datetime.strptime(new_date, '%d.%m.%y').strftime('%y-%m-%d')
                
                engine.execute(f"UPDATE availability SET hours = ARRAY {new_old_hours} WHERE availability.day = '{reservation[0][3]}' AND availability.table_id = {reservation[0][1]}")
                if len(new_hours_new) == 0:
                    engine.execute(f"UPDATE availability SET hours = ARRAY {['']} WHERE availability.day = '20{new_date}' AND availability.table_id = {best_table[0][0]}")
                else:
                    engine.execute(f"UPDATE availability SET hours = ARRAY {new_hours_new}  WHERE availability.day = '20{new_date}' AND availability.table_id = {best_table[0][0]}")

                engine.execute(f"UPDATE reservations SET table_id = {best_table[0][0]}, guests = {new_guests}, start = '20{new_date}', time = '{new_time}' WHERE reservations.reservation_id = {reservation_id}")

                return {"message": "Succesfully changed reservation"}

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


# r = RestaurantModel()
# print(r.check_availability('03.02.23', 2))
# r.add_availability('2023-02-08')
# print(r.check_status(49))
# print(r.book_table(2, "03.02.23", "530925823", "20:00"))
# print(r.cancel_reservation(49, "530925823"))
# print(r.change_reservation(50, "530925823", "03.02.23", "22:00", 2))


