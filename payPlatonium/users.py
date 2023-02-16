import sqlite3

import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
""")

cursor.execute("""
INSERT INTO users (id, username, password)
VALUES
    (NULL, "user1", "password1"),
    (NULL, "user2", "password2"),
    (NULL, "user3", "password3");
""")



def create_database():
    conn = sqlite3.connect('users.db')
    print('Database created.')
    conn.close()

def create_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username text PRIMARY KEY,
            password text NOT NULL
        );
    ''')
    print('Table created.')
    conn.commit()
    conn.close()

def insert_sample_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (NULL, 'user1', 'password1')")
    c.execute("INSERT INTO users VALUES (NULL, 'user2', 'password2')")
    c.execute("INSERT INTO users VALUES (NULL, 'user3', 'password3')")
    print('Sample users inserted.')
    conn.commit()
    conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    user = c.fetchone()
    conn.close()
    if user:
        return True
    else:
        return False
    
conn.commit()
conn.close()

