from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import jwt
import datetime
import sqlite3
import bcrypt
import uvicorn


def create_user(username, password, email):
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Connect to the SQLite database
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()

    # Insert a new user
    query = 'INSERT INTO users (username, password, email) VALUES (?, ?, ?)'
    cursor.execute(query, (username, hashed_password, email))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def validate_credentials(email, password):
    # Connect to the SQLite database
    conn = sqlite3.connect('calendar_app.db')
    cursor = conn.cursor()

    # Find user by email
    query = 'SELECT password FROM users WHERE email = ?'
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if user exists and the passwords match
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True
    else:
        return False

class User(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

app = FastAPI()

SECRET_KEY = "secret"

@app.post("/login")
async def login(request: LoginRequest):
    email = request.email
    password = request.password

    if validate_credentials(email, password):
        token = jwt.encode({
            'user': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY)
        return {"token": token}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed. Please try again.")

@app.post("/register")
async def register(user: User):
    create_user(user.username, user.password, user.email)
    '''Verify user email and handle errors for username and email already existing, make sure password is non-empty'''
    return {"message": "User created successfully."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
