from fastapi import FastAPI, HTTPException
from models import Member
from typing import List
import asyncio

app = FastAPI()

# Temporary in-memory database
db = []

@app.post("/members/", response_model=Member)
async def create_member(member: Member):
    await asyncio.sleep(1)
    for m in db:
        if m.member_id == member.member_id:
            raise HTTPException(status_code=400, detail="ID already exists")
    db.append(member)
    return member

@app.get("/members/", response_model=List[Member])
async def get_members():
    await asyncio.sleep(1)
    return db

@app.get("/members/{member_id}", response_model=Member)
async def get_member(member_id: int):
    await asyncio.sleep(1)
    for m in db:
        if m.member_id == member_id:
            return m
    raise HTTPException(status_code=404, detail="Member not found")

@app.put("/members/{member_id}", response_model=Member)
async def update_member(member_id: int, member: Member):
    await asyncio.sleep(1)
    # Make sure the ID in the URL and the body match
    if member.member_id != member_id:
        raise HTTPException(status_code=400, detail="Member ID in URL and body must match")
    for i in range(len(db)):
        if db[i].member_id == member_id:
            db[i] = member
            return db[i]
    raise HTTPException(status_code=404, detail="Member not found")

@app.delete("/members/{member_id}")
async def delete_member(member_id: int):
    await asyncio.sleep(1)
    for i in range(len(db)):
        if db[i].member_id == member_id:
            db.pop(i)
            return {"message": "Member deleted"}
    raise HTTPException(status_code=404, detail="Member not found")
