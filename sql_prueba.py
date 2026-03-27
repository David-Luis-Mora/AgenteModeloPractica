import sqlite3

conn = sqlite3.connect('sports_league.sqlite')
cur = conn.cursor()
cur.execute('SELECT * FROM leagues')
rows = cur.fetchall()
conn.close()
for row in rows:
   print(row)