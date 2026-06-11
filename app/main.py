from fastapi import FastAPI

from app.database.connection import initialize_database
from app.routes.events import event_router
from app.routes.users import user_router


app = FastAPI()


# initialize the database when the app starts
@app.on_event("startup")
async def on_startup():
    await initialize_database()


# register the routers
app.include_router(event_router, prefix="/event")
app.include_router(user_router, prefix="/user")


@app.get("/")
async def index():
    return {"message": "Hello, the API is running!"}
