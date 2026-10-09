import sqlite3

conn = sqlite3.connect('epl.db')

with open("schema.sql") as sql_file:
    contents = sql_file.read()

conn.executescript(contents)

conn.commit()
conn.close()