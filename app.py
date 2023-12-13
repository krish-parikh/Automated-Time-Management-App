from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from input import parse_event_data
from model import get_event_info

class Event(BaseModel):
    event: str

app = FastAPI()

@app.post("/create_event")
async def create_event(event: Event):

    '''event_data = event.event
    event_data = get_event_info(event_data)
    event_data = parse_event_data(event_data)'''
    
    return '''{"event": event.event}'''

