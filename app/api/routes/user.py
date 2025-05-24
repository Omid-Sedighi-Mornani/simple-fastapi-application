from fastapi import APIRouter, status, HTTPException, Query
from typing import Annotated
from models.user import User
from schemas.user import UserCreate
from utils.hashing import hash_password
from deps.db import AsyncSessionMaker
from utils.tokens import create_access_token, decode_access_token
import os
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

router = APIRouter()

SERVER_URI = os.getenv("SERVER_URI")


@router.get("/")
def test_response():
    return {"message": "response received!"}


@router.post("/signin")
async def signup(user_create: UserCreate, session: AsyncSessionMaker):

    user_dict = user_create.model_dump(exclude={"password"})
    hashed_password = hash_password(user_create.password)
    user = User(**user_dict, hashed_password=hashed_password)

    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists in database!",
        )

    to_encode = {"sub": user_create.email}
    token = create_access_token(to_encode)

    verification_link = f"{SERVER_URI}/users/verify?token={token}"
    print(verification_link)

    return {"message": "The verification mail has been sent. Please check your email"}


@router.get("/verify")
async def verify_user(token: Annotated[str, Query(...)], session: AsyncSessionMaker):
    try:
        user_data = decode_access_token(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No valid token provided!"
        )

    email = user_data.get("sub")
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)

    user = result.one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.verified = True
    await session.commit()

    return {"message": f"Successfully verified the following email: {email}"}
