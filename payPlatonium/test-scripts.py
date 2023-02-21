import sqlite3

conn = sqlite3.connect('payments.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
if c.fetchone():
    print("Table exists")
else:
    print("Table does not exist")

c.close()
