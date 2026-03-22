from fastapi import FastAPI
from member import member_router  # import the router from member.py

app = FastAPI(title="Gym Management API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Gym Management API!"}

app.include_router(member_router)
