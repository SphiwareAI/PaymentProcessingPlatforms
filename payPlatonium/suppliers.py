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
        company_name TEXT NOT NULL,
        bank_name TEXT NOT NULL,
        acc_number INTEGER NOT NULL,
        branch_code INTEGER NOT NULL
    )
''')



suppliers = [
    ('James', 'Mash', 'james@sphiwareai.com', 'AI', 'SphiwareAI Inc.', 'ABSA Bank', 123456789, 1234),
    ('Mash', 'Jr', 'mashrj@sphiwareai.com', 'CTO', 'MInstanceAI Corp.', 'FNB Bank', 987654321, 4321),
    ('Sphiwe', 'Mashiyane', 'sphiwe@sphiwefarm.com', 'Farming', 'Sphiwe Fruit & Veg Ltd.', 'Capitec Bank', 111111111,2345)
]

for supplier in suppliers:
    cursor.execute('INSERT INTO suppliers (name, surname, email, department, company_name, bank_name, acc_number, branch_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', supplier)



# Commit the changes to the database

cursor.close()
conn.close()

