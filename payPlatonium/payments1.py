import sqlite3

conn = sqlite3.connect('payments1.db')
c = conn.cursor()

    
# Create the payments1 table
c.execute('''CREATE TABLE payments1
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              supplier_id INTEGER,
              name TEXT,
              surname TEXT,
              email TEXT,
              department TEXT,
              date_of_invoice TEXT, 
              date_of_payment_requested TEXT,
              payment_description TEXT,
              payment_made_to TEXT,
              company_name TEXT,
              bank_name TEXT,
              acc_number INTEGER,
              branch_code INTEGER,
              amount REAL,
              status TEXT,
              date TEXT,
              FOREIGN KEY (supplier_id) REFERENCES suppliers(id))''')

# Save the changes and close the connection
conn.commit()
conn.close()
