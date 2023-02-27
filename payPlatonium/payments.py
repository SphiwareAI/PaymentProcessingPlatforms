import sqlite3

# Connect to the user database
user_conn = sqlite3.connect('users.db')
user_cursor = user_conn.cursor()

# Connect to the supplier database
supplier_conn = sqlite3.connect('suppliers.db')
supplier_cursor = supplier_conn.cursor()

# Connect to the payments database
payments_conn = sqlite3.connect('payments.db')
payments_cursor = payments_conn.cursor()

# Create the suppliers table
payments_cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT NOT NULL,
        company_name TEXT NOT NULL,
        bank_name TEXT NOT NULL,
        acc_number INTEGER NOT NULL,
        branch_code INTEGER NOT NULL
    )
''')

# Create the payments table
payments_cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        supplier_name TEXT NOT NULL,
        date_of_invoice DATE NOT NULL,
        date_of_payment_requested DATE NOT NULL,
        payment_description TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('paid', 'not paid', 'pending')),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    )
''')

# Insert the supplier data into the payments database
supplier_cursor.execute('SELECT * FROM suppliers')
suppliers_data = supplier_cursor.fetchall()

for supplier in suppliers_data:
    supplier_id, name, surname, email, department, company_name, bank_name, acc_number, branch_code = supplier
    payments_cursor.execute('INSERT INTO suppliers (id, name, surname, email, department, company_name, bank_name, acc_number, branch_code) '
                            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', supplier)

# Insert dummy data into the payments table
#payments = [
#    (1, 1, '2023-01-01', '2023-01-10', 'Supplier 1', 'Invoice Payment', 10000.0, 'not paid'),
#    (1, 2, '2023-01-15', '2023-01-20', 'Supplier 1', 'Invoice Payment', 5000.0, 'not paid'),
#    (2, 3, '2023-01-05', '2023-01-10', 'Supplier 2', 'Invoice Payment', 15000.0, 'not paid'),
#    (2, 4, '2023-01-20', '2023-01-25', 'Supplier 2', 'Invoice Payment', 20000.0, 'not paid'),
#    (3, 5, '2023-01-01', '2023-01-10', 'Supplier 3', 'Invoice Payment', 30000.0, 'not paid'),
#    (3, 6, '2023-01-15', '2023-01-20', 'Supplier 3', 'Invoice Payment', 10000.0, 'not paid')
#]

#for payment in payments:
#    payments_cursor.execute('INSERT INTO payments (supplier_id, payment_id, supplier_name, date_of_invoice, #date_of_payment_requested, payment_description, amount, status) '
#                            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)', payment)


# Commit and close connections
user_conn.commit()
user_conn.close()
supplier_conn.commit()
supplier_conn.close()
payments_conn.commit()
payments_conn.close()
