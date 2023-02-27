import sqlite3

conn = sqlite3.connect('payments.db')
c = conn.cursor()

#c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
#if c.fetchone():
#    print("Table exists")
#else:
#    print("Table does not exist")

#c.close()

# Retrieve all data from the payments table
cur = conn.cursor()
cur.execute("SELECT * FROM payments")
rows = cur.fetchall()

# Print the data
for row in rows:
    print(row)

#print(rows[0][5])
# Close the database connection
conn.close()
