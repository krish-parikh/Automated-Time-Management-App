from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import datetime
import uvicorn

from pipeline import pipeline
from priority import DBManager
from user import create_user, validate_credentials, get_user_details  # assuming get_user_details is a function you have

from dotenv import load_dotenv
import os

class Prompt(BaseModel):
    prompt: str

class User(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RateLimiter:
    def __init__(self):
        self.requests = {}

    def limit(self, user_id: int, max_requests: int):
        if user_id in self.requests:
            self.requests[user_id]["count"] += 1
        else:
            self.requests[user_id] = {"count": 1, "time": datetime.datetime.now()}

        time_diff = datetime.datetime.now() - self.requests[user_id]["time"]
        if time_diff.days >= 1:
            self.requests[user_id] = {"count": 1, "time": datetime.datetime.now()}
        elif self.requests[user_id]["count"] > max_requests:
            return False

        return True

rate_limiter = RateLimiter()

app = FastAPI()

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("user")
        if email is None:
            raise credentials_exception
        # Fetch more user details if needed
        user = get_user_details(email)
        if user is None:
            raise credentials_exception
        # Check if token has expired
        expiration = payload.get("exp")
        if expiration is None or datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(expiration):
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

@app.post("/login")
async def login(request: LoginRequest):
    email = request.email
    password = request.password

    if validate_credentials(email, password):
        token = jwt.encode({
            'user': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm=ALGORITHM)
        return {"token": token}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed. Please try again.")

@app.post("/register")
async def register(user: User):
    create_user(user.username, user.password, user.email)
    return {"message": "User created successfully."}
    
@app.post("/create_event")
async def create_event(prompt: Prompt, user_id: int = Depends(get_current_user)):
    if not rate_limiter.limit(user_id, 20):
        return JSONResponse(status_code=429, content={"message": "Rate limit exceeded"})

    event_data = prompt.prompt
    event_data = pipeline(event_data, user_id)

    if event_data == 0:
        return {"message": "Event creation failed"}

    else:
        return {"message": "Event created successfully"}
    
@app.get("/events")
async def get_events(user_id: int = Depends(get_current_user)):
    with DBManager('calendar_app.db') as cursor:
        cursor.execute("SELECT * FROM events WHERE user_id = ?", (user_id,))
        events = cursor.fetchall()
        return events
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
