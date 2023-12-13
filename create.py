import sqlite3
import hashlib
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect('calendar_app.db')  # 'calendar_app.db' is the name of your database

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Create 'users' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT
    )
''')

# Create 'events' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_name TEXT,
        start_datetime DATETIME,
        end_datetime DATETIME,
        event_date DATE NOT NULL,
        event_flexibility INTEGER NOT NULL,
        event_importance INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
