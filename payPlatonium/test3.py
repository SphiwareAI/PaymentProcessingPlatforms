import sqlite3

# Connect to the payments database
conn = sqlite3.connect('payments.db')
c = conn.cursor()

# Count the number of rows in the 'payments' table
c.execute("SELECT COUNT(*) FROM payments")
num_rows = c.fetchone()[0]

if num_rows == 0:
    print("The 'payments' table is empty.")
else:
    print("The 'payments' table has {} rows.".format(num_rows))

# Close the database connection
c.close()

