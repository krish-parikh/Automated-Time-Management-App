import sqlite3
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from pipeline import pipeline

class Prompt(BaseModel):
    prompt: str

class Event(BaseModel):
    event_name: str
    start_datetime: str
    end_datetime: str
    event_date: str
    event_flexibility: int
    event_importance: int

app = FastAPI()

# Connection Manager
class DBManager:
    def __init__(self, database: str):
        self.database = database

    def __enter__(self):
        self.conn = sqlite3.connect(self.database)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

def get_db():
    with DBManager('calendar_app.db') as cursor:
        yield cursor

@app.post("/events")
def create_event(user_id: int, event: Event, cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute("INSERT INTO events (user_id, event_name, start_datetime, end_datetime, event_date, event_flexibility, event_importance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (user_id, event.event_name, event.start_datetime, event.end_datetime, event.event_date, event.event_flexibility, event.event_importance))
    event_id = cursor.lastrowid
    return {"event_id": event_id}

@app.put("/events/{event_id}")
def update_event(user_id: int, event_id: int, event: Event, cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute("UPDATE events SET event_name = ?, start_datetime = ?, end_datetime = ?, event_date = ?, event_flexibility = ?, event_importance = ? WHERE id = ? AND user_id = ?",
                   (event.event_name, event.start_datetime, event.end_datetime, event.event_date, event.event_flexibility, event.event_importance, event_id, user_id))
    return {"message": "Event updated successfully"}

@app.delete("/events/{event_id}")
def delete_event(user_id: int, event_id: int, cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute("DELETE FROM events WHERE id = ? AND user_id = ?", (event_id, user_id))
    return {"message": "Event deleted successfully"}

@app.get("/events")
def get_events(user_id: int, cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute("SELECT * FROM events WHERE user_id = ?", (user_id,))
    events = cursor.fetchall()
    return events

@app.post("/create_event")
async def create_event(user_id: int, event: Prompt):
    pipeline(event.prompt)
    return

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
