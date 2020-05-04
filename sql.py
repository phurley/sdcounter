import psycopg2

#connect to the db 
con = psycopg2.connect(
            database="ahurley",
            user = "ahurley")

#cursor 
cur = con.cursor()

#cur.execute("insert into employees (id, name) values (%s, %s)", (1, "Hussein") )

#execute query
cur.execute("select * from rooms")

rows = cur.fetchall()

for r in rows:
    print (f"id {r[0]} name {r[1]}")

#commit the transcation 
con.commit()

#close the cursor
cur.close()

#close the connection
con.close()
