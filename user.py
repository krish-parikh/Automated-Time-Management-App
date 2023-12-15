import bcrypt
from priority import DBManager
import sqlite3
import re

def check_email_format(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def create_user(username, password, email):
    # Hash the password using bcrypt
    email = email.lower()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    if check_email_format(email):
        with DBManager('calendar_app.db') as cursor:
            try:
                # Insert user details into the database
                query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
                cursor.execute(query, (username, hashed_password, email))
            except sqlite3.IntegrityError:
                return "User already exists"
    else :
        return "Email format is not valid"
             
def validate_credentials(email, password):
    email = email.lower()
    # Connect to the SQLite database
    with DBManager('calendar_app.db') as cursor:
        # Find user by email
        query = 'SELECT password FROM users WHERE email = ?'
        cursor.execute(query, (email,))
        result = cursor.fetchone()

    # Check if user exists and the passwords match
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True
    else:
        return False
    
def get_user_details(email):
    # Connect to the SQLite database
    email = email.lower()
    with DBManager('calendar_app.db') as cursor:
        # Find user by email
        query = 'SELECT id FROM users WHERE email = ?'
        cursor.execute(query, (email,))
        result = cursor.fetchone()

    # Check if user exists and the passwords match
    if result:
        return result[0]
    else:
        return None
