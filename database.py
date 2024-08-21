import sqlite3
conn = sqlite3.connect('codes.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS access_codes(
   code INT PRIMARY KEY
   );
""")


#codes_to_add = [('1488',), ('5555',),('6789',),('2345',), ('7654',)]
#cur.executemany("INSERT INTO access_codes VALUES(?);", codes_to_add)
#conn.commit()


#cur.execute("SELECT * FROM access_codes;")
#all_results = cur.fetchall()
#print(all_results)