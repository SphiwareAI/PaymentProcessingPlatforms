import sqlite3

# Connect to the payments database
conn = sqlite3.connect('payments.db')
c = conn.cursor()

# Get the list of tables in the database
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()

# Check if the 'payments' table is in the list of tables
if ('payments',) in tables:
    print("The 'payments' table exists in the database.")
else:
    print("The 'payments' table does not exist in the database.")

# Close the database connection
c.close()

