import sqlite3

conn = sqlite3.connect('events.db')
with open('schema.sql', 'r') as f:
    conn.executescript(f.read())
conn.close()
print('Schema created')
