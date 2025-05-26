from database.core import (
    AsyncSessionMaker,
    NotFoundError,
    AlreadyExistsError,
    NotAuthenticatedError,
)
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserLogin
from utils.security import hash_password, verify_password
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from typing import Union


async def read_user(
    user_identifier: Union[int, str], session: AsyncSessionMaker
) -> User:
    print(type(user_identifier))
    if isinstance(user_identifier, int):
        user = await session.get(User, user_identifier)
    elif isinstance(user_identifier, str):
        statement = select(User).where(User.email == user_identifier)
        result = await session.exec(statement)
        user = result.one_or_none()
    else:
        raise ValueError("You have to provide an email or user id!")

    if not user:
        raise NotFoundError("The user with specified Id was not found in database!")

    return user


async def create_user(user_create: UserCreate, session: AsyncSessionMaker) -> User:
    user_dict = user_create.model_dump(exclude={"password"})
    hashed_password = hash_password(user_create.password)

    try:
        user = User(**user_dict, hashed_password=hashed_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        raise AlreadyExistsError("User already exists in database!")

    return user


async def update_user(
    user_identifier: Union[int, str],
    user_update: UserUpdate,
    session: AsyncSessionMaker,
) -> User:
    user = await read_user(user_identifier, session)
    for key, value in user_update.model_dump(exclude_none=True).items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)

    return user


async def delete_user(
    user_identifier: Union[int, str], session: AsyncSessionMaker
) -> User:
    user = await read_user(user_identifier, session)
    await session.delete(user)
    await session.commit()
    return user


async def authenticate_user(user_login: UserLogin, session: AsyncSessionMaker) -> User:
    user = await read_user(user_login.email, session)

    if verify_password(user_login.password, user.hashed_password):
        return user
    else:
        raise NotAuthenticatedError("The provided password is wrong!")
