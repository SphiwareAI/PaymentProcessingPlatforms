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

# Create the payments table
payments_cursor.execute('''
    CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        supplier_id INTEGER,
        amount REAL,
        status TEXT,
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
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    )
''')

# Insert the user and supplier data into the payments table
user_cursor.execute('SELECT id, username, password FROM users')
supplier_cursor.execute('SELECT id, payment_made_to, company_name, bank_name, acc_number, branch_code FROM suppliers')
user_data = user_cursor.fetchall()
supplier_data = supplier_cursor.fetchall()

for supplier in supplier_data:
    supplier_id, payment_made_to, company_name, bank_name, acc_number, branch_code = supplier
    for user in user_data:
        user_id, _, _, name, surname, email, department = user
        payment = (user_id, supplier_id, min(user[3], supplier[1]), 'pending', name, surname, email, department,
                   payment_made_to, company_name, bank_name, acc_number, branch_code)
        payments_cursor.execute('INSERT INTO payments (user_id, supplier_id, amount, status, name, surname, email, department, '
                                'payment_made_to, company_name, bank_name, acc_number, branch_code) '
                                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', payment)

# Commit and close connections
user_conn.commit()
user_conn.close()
supplier_conn.commit()
supplier_conn.close()
payments_conn.commit()
payments_conn.close()
