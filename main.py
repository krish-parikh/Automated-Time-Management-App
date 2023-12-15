from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

from pipeline import pipeline

class Prompt(BaseModel):
    prompt: str
    user_id: int

app = FastAPI()

@app.post("/create_event")
async def create_event(prompt: Prompt):

    event_data = prompt.prompt
    user_id = prompt.user_id
    event_data = pipeline(event_data, user_id)

    if event_data == 0:
        return {"message": "Event creation failed"}
    else:
        return {"message": "Event created successfully"}