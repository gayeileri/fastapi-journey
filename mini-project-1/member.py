from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List
from models import Member
import asyncio

member_router = APIRouter()

# templates klasörü bu dosyanın yanında
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# fake db, gerçek db olmadığı için liste kullandım
db: List[Member] = [
    Member(
        id=1,
        name="Alice Johnson",
        membership_type="Premium",
        sessions=[
            {
                "session_id": 101,
                "date": "2024-03-10",
                "workout_type": "Cardio",
                "duration_minutes": 45,
                "calories_burned": 400,
            }
        ],
    ),
    Member(
        id=2,
        name="Bob Smith",
        membership_type="Basic",
        sessions=[],
    ),
]


# /home sayfası tüm üyeleri listeler
@member_router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    await asyncio.sleep(1)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "members": db},
    )


# /member/{id} tek üyenin detay sayfası
@member_router.get("/member/{id}", response_class=HTMLResponse)
async def member_page(request: Request, id: int):
    await asyncio.sleep(1)
    for m in db:
        if m.id == id:
            return templates.TemplateResponse(
                "member.html",
                {"request": request, "member": m},
            )
    raise HTTPException(status_code=404, detail="Member not found")


@member_router.get("/members", response_model=List[Member])
async def get_all_members():
    await asyncio.sleep(1)
    return db


@member_router.get("/members/{id}", response_model=Member)
async def get_member(id: int):
    await asyncio.sleep(1)
    for m in db:
        if m.id == id:
            return m
    raise HTTPException(status_code=404, detail="Member not found")


@member_router.post("/members", response_model=Member)
async def create_member(member: Member):
    await asyncio.sleep(1)
    # aynı id varsa hata ver
    for m in db:
        if m.id == member.id:
            raise HTTPException(status_code=400, detail="A member with this ID already exists")
    db.append(member)
    return member


@member_router.put("/members/{id}", response_model=Member)
async def update_member(id: int, updated: Member):
    await asyncio.sleep(1)
    if updated.id != id:
        raise HTTPException(status_code=400, detail="ID in URL and request body must match")
    for i in range(len(db)):
        if db[i].id == id:
            db[i] = updated
            return db[i]
    raise HTTPException(status_code=404, detail="Member not found")


@member_router.delete("/members/{id}")
async def delete_member(id: int):
    await asyncio.sleep(1)
    for i in range(len(db)):
        if db[i].id == id:
            db.pop(i)
            return {"message": "Member deleted successfully"}
    raise HTTPException(status_code=404, detail="Member not found")
