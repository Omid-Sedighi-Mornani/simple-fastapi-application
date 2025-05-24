from fastapi import APIRouter
from models.user import User
from schemas.user import UserCreate
from utils.hashing import hash_password
from deps.db import AsyncSessionMaker

router = APIRouter()


@router.get("/")
def test_response():
    return {"message": "response received!"}


@router.post("/")
async def add_new_user(user_create: UserCreate, session: AsyncSessionMaker):
    hashed_password = hash_password(user_create.password)
    user = User(username=user_create.username, hashed_password=hashed_password)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
