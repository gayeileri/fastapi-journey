from fastapi import APIRouter, HTTPException, status

from app.database.connection import Database
from app.models.users import User, UserSignIn


user_router = APIRouter(tags=["Users"])
user_database = Database(User)


# sign up - also checks if the email is already registered
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(body: User):
    existing = await User.find_one(User.email == body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )
    await user_database.save(body)
    return {"message": "User created successfully."}


# sign in
@user_router.post("/signin")
async def sign_in(body: UserSignIn):
    user = await User.find_one(User.email == body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    # check the password
    if user.password != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password."
        )
    return {"message": "Signed in successfully."}
