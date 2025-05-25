from fastapi import APIRouter, status, HTTPException, Query, BackgroundTasks
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
from utils.email import send_email, render_email_template

router = APIRouter()

SERVER_URI = os.getenv("SERVER_URI")


@router.get("/")
def test_response():
    return {"message": "response received!"}


@router.post("/signin")
async def signup(
    user_create: UserCreate,
    session: AsyncSessionMaker,
    background_tasks: BackgroundTasks,
):

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

    token = create_access_token({"sub": user_create.email})

    verification_link = f"{SERVER_URI}/users/verify?token={token}"

    html_content = await render_email_template(
        "verification.html",
        {"username": user.username, "verification_link": verification_link},
    )

    background_tasks.add_task(
        send_email, user.email, f"Hi {user.username}!", html_content
    )

    return {"message": "The verification mail has been sent. Please check your email"}


@router.get("/verify")
async def verify_user(token: Annotated[str, Query(...)], session: AsyncSessionMaker):

    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token credentials!",
        headers={"wWW-Authenticate": "Bearer"},
    )

    try:
        user_data = decode_access_token(token)
    except InvalidTokenError:
        raise invalid_token_exception
    email = user_data.get("sub")

    if not email:
        raise invalid_token_exception

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
