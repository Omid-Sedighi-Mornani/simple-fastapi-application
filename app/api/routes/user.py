from fastapi import APIRouter, status, HTTPException, Query, BackgroundTasks
from typing import Annotated
from models.user import User
from schemas.user import UserCreate, UserUpdate
from database.core import AsyncSessionMaker
from utils.tokens import create_access_token, decode_access_token
import os
from sqlmodel import select
from jwt.exceptions import InvalidTokenError
from utils.email import send_email, render_email_template
from services.user import (
    read_user,
    read_user_by_email,
    create_user,
    update_user,
    delete_user,
)
from database.core import NotFoundError, AlreadyExistsError

router = APIRouter()

SERVER_URI = os.getenv("SERVER_URI")


@router.get("/id/{user_id}")
async def get(user_id: int, session: AsyncSessionMaker):

    try:
        user = await read_user(user_id, session)
    except NotFoundError:
        raise HTTPException(
            detail="User not found!", status_code=status.HTTP_404_NOT_FOUND
        )

    return user


@router.put("/id/{user_id}")
async def update(user_id: int, user_update: UserUpdate, session: AsyncSessionMaker):
    try:
        user = await update_user(user_id, user_update, session)
    except NotFoundError:
        raise HTTPException(
            detail="User to be updated, was not found!",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return user


@router.delete("/id/{user_id}")
async def delete(user_id: int, session: AsyncSessionMaker):
    try:
        user = await delete_user(user_id, session)
    except NotFoundError:
        raise HTTPException(
            detail="User to be deleted, was not found!",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return user


@router.post("/signin")
async def signup(
    user_create: UserCreate,
    session: AsyncSessionMaker,
    background_tasks: BackgroundTasks,
):

    try:
        user = await create_user(user_create, session)
    except AlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with email already exists in database!",
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

    try:
        user = await read_user_by_email(email, session)
    except NotFoundError:
        raise HTTPException(
            detail="User not found!", status_code=status.HTTP_404_NOT_FOUND
        )

    user.verified = True
    await session.commit()

    return {"message": f"Successfully verified the following email: {email}"}
