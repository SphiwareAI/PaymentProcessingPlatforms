import sqlite3

conn = sqlite3.connect('suppliers.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT NOT NULL,
        payment_made_to TEXT NOT NULL,
        company_name TEXT NOT NULL,
        bank_name TEXT NOT NULL,
        acc_number INTEGER NOT NULL,
        branch_code INTEGER NOT NULL,
        amount REAL NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        date_of_invoice TEXT NOT NULL,
        date_of_payment_requested TEXT NOT NULL,
        payment_description TEXT NOT NULL,
        amount REAL NOT NULL,
        manager_approval INTEGER NOT NULL,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
''')

suppliers = [
    ('James', 'Mash', 'james@sphiwareai.com', 'AI', 'James Mash', 'SphiwareAI Inc.', 'ABSA Bank', 123456789, 1234, 1000.0),
    ('Mash', 'Jr', 'mashrj@sphiwareai.com', 'CTO', 'Mash Jr', 'MInstanceAI Corp.', 'FNB Bank', 987654321, 4321, 5000.0),
    ('Sphiwe', 'Mashiyane', 'sphiwe@sphiwefarm.com', 'Farming', 'Sphiwe Mashiyane', 'Sphiwe Fruit & Veg Ltd.', 'Capitec Bank', 111111111, 1111, 2000.0)
]

for supplier in suppliers:
    cursor.execute('INSERT INTO suppliers (name, surname, email, department, payment_made_to, company_name, bank_name, acc_number, branch_code, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', supplier)


# Dummy data for invoices
invoices = [
    (1, '2022-01-01', '2022-01-15', 'Invoice Payment', 10000.0, 1),
    (2, '2022-02-01', '2022-02-15', 'Invoice Payment', 20000.0, 0),
    (3, '2022-03-01', '2022-03-15', 'Invoice Payment', 30000.0, 1)
]

# Insert the dummy data into the invoices table
for invoice in invoices:
    cursor.execute('INSERT INTO invoices (supplier_id, date_of_invoice, date_of_payment_requested, payment_description, amount, manager_approval) VALUES (?, ?, ?, ?, ?, ?)', invoice)

# Commit the changes to the database

cursor.close()
conn.close()

