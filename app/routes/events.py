from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from app.database.connection import Database
from app.models.events import Event, EventUpdate


event_router = APIRouter(tags=["Events"])

# create a Database instance for Event
event_database = Database(Event)


# get all events
@event_router.get("/", response_model=List[Event])
async def get_all_events():
    events = await event_database.get_all()
    return events


# get a single event by id
@event_router.get("/{id}", response_model=Event)
async def get_event(id: PydanticObjectId):
    event = await event_database.get(id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )
    return event


# create a new event
@event_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(body: Event):
    await event_database.save(body)
    return {"message": "Event created successfully."}


# update an event
@event_router.put("/{id}", response_model=Event)
async def update_event(id: PydanticObjectId, body: EventUpdate):
    updated = await event_database.update(id, body.model_dump())
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )
    return updated


# delete an event
@event_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(id: PydanticObjectId):
    deleted = await event_database.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )
