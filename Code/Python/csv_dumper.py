import csv
import sqlite3

conn = sqlite3.connect('test.db')

c = conn.cursor()
c.execute("Select * from Songs;")

f = open('songs.csv', 'w')
writer = csv.writer(f)

for row in c.fetchall():
    # the csv module can't handle unicode, so encode the strings
    row = [item  for item in row]
    writer.writerow(row)
