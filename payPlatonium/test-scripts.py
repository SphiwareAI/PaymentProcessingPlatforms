import sqlite3

# Connect to the database
conn = sqlite3.connect('payments.db')

# Create a cursor object
cursor = conn.cursor()

# Execute a SELECT statement to retrieve all rows from the payments table
cursor.execute('SELECT * FROM payments')

# Fetch all rows and print them
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the database connection
conn.close()
