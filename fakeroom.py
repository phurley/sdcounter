import sys
import random
from random import randint
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import psycopg2
import psycopg2.extras

# args - 
#      roomname
#      start date
#      [stop date]
#      [mode - random, _regular_]
#      [start time: 8am]
#      [end time: 10pm]
#      [max count: 25]

if len(sys.argv) < 3:
    print("""args: python fakeroom.py  
      roomname
      start datetime
      [stop datetime]
      [mode - random, _regular_]
      [max count: 25]""")
    sys.exit(-1)

roomname = sys.argv[1]
start = parse(sys.argv[2])
stop = parse(sys.argv[3]) if len(sys.argv) > 3 else (start + timedelta(days=1))
mode = sys.argv[4] if len(sys.argv) > 4 else "regular"
maxcount = int(sys.argv[5] if len(sys.argv) > 5 else 25)

if start > stop:
    tmp = start
    start = stop
    stop = start

print(roomname)
print(start)
print(stop)
print(mode)
print(maxcount)
half = (stop - start).total_seconds() / 2
half = start + timedelta(seconds=half)

connection = psycopg2.connect(database = "ahurley", user = "ahurley")
with connection:
    with connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cursor:
        try:
            cursor.execute("insert into rooms (name) values (%s)", (roomname, ))
        except psycopg2.Error:
            1 # ignore

with connection:
    with connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("select * from rooms where name = %s", (roomname, ))
        result = cursor.fetchone()
        if result == None:
            print(f"Error inserting {roomname}")
            sys.exit(-2)
        room_id = result["id"]
        cursor.execute("update journal SET applied_at = %s WHERE room_id = %s AND previous_count IS NULL AND applied_at > %s", (start, room_id, start)) 

        count = 0
        now = start
        while now < stop:
            now = now + timedelta(minutes=randint(1, 30))
            if mode == "regular":
                if now < half:
                    delta = randint(-2, 4)
                    delta = 1 if delta == 0 else delta
                else:
                    delta = randint(-4, 2)
                    delta = -1 if delta == 0 else delta
            else:
                print("going down")
                delta = randint(-4,4)
                delta = 1 if delta == 0 else delta

            delta = 0 if (count + delta) > maxcount else delta
            delta = 0 if (count + delta) < 0 else delta

            if delta != 0:
                print(f"{now}: {count}")
                cursor.execute("INSERT INTO journal (room_id, previous_count, count, applied_at) VALUES(%s,%s,%s,%s)",
                        (room_id, count, count + delta, now))
                count = count + delta

        cursor.execute("INSERT INTO journal (room_id, previous_count, count, applied_at) VALUES(%s,%s,%s,%s)",
                (room_id, count, -count, stop))
            
