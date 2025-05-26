from fastapi import APIRouter, status, HTTPException, Query, BackgroundTasks, Depends
from typing import Annotated, Type
from schemas.user import UserCreate, UserUpdate, UserLogin
from schemas.token import Token
from database.core import AsyncSessionMaker
from utils.tokens import create_access_token, decode_access_token
import os
from jwt.exceptions import InvalidTokenError
from utils.email import send_email, render_email_template
from services.user import *
from database.core import NotFoundError, AlreadyExistsError, NotAuthenticatedError
from contextlib import asynccontextmanager
from utils.security import oauth2_scheme

router = APIRouter()

SERVER_URI = os.getenv("SERVER_URI")


@asynccontextmanager
async def http_exception_handler(
    exception: Type[Exception] | tuple[Type[Exception]] = Exception,
    status_code: int = 500,
    message: str = "Some error occured!",
    headers: dict = None,
):
    try:
        yield
    except exception:
        raise HTTPException(detail=message, status_code=status_code, headers=headers)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSessionMaker
) -> User:

    async with http_exception_handler(
        (InvalidTokenError, NotFoundError),
        status_code=401,
        message="Invalid token credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    ):

        payload = decode_access_token(token)
        email = payload.get("sub")

        if not email:
            raise NotFoundError("No email in payload provided!")

        user = await read_user(email, session)

    return user


@router.get("/id/{user_id}")
async def get(user_id: int, session: AsyncSessionMaker):

    async with http_exception_handler(
        NotFoundError, status_code=404, message="User not found!"
    ):
        user = await read_user(user_id, session)

    return user


@router.put("/id/{user_id}")
async def update(user_id: int, user_update: UserUpdate, session: AsyncSessionMaker):
    async with http_exception_handler(
        NotFoundError, status_code=404, message="User to be updated not found!"
    ):
        user = await update_user(user_id, user_update, session)

    return user


@router.delete("/id/{user_id}")
async def delete(user_id: int, session: AsyncSessionMaker):
    async with http_exception_handler(
        NotFoundError, status_code=404, message="User to be deleted not found!"
    ):
        user = await delete_user(user_id, session)

    return user


@router.post("/signin")
async def signup(
    user_create: UserCreate,
    session: AsyncSessionMaker,
    background_tasks: BackgroundTasks,
):

    async with http_exception_handler(
        AlreadyExistsError, status_code=400, message="Email already exists in database!"
    ):
        user = await create_user(user_create, session)

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

    async with http_exception_handler(
        InvalidTokenError,
        status_code=401,
        message="Invalid token credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    ):
        user_data = decode_access_token(token)
        email = user_data.get("sub")
        if not email:
            raise InvalidTokenError()

    async with http_exception_handler(
        NotFoundError, status_code=404, message="User with email not found!"
    ):
        user = await read_user(email, session)

    user.verified = True
    await session.commit()
    return {"message": f"Successfully verified the following email: {email}"}


@router.post("/login")
async def login_user(user_login: UserLogin, session: AsyncSessionMaker):
    async with http_exception_handler(
        (NotFoundError, NotAuthenticatedError),
        status_code=404,
        message="Wrong email or password provided!",
    ):
        user = await authenticate_user(user_login, session)
        access_token = create_access_token({"sub": user.email})

        return Token(access_token=access_token, token_type="bearer")


@router.get("/test")
def test(user: Annotated[User, Depends(get_current_user)]):
    return user
