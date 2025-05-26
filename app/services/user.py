from database.core import AsyncSessionMaker, NotFoundError, AlreadyExistsError
from models.user import User
from schemas.user import UserCreate, UserUpdate
from utils.hashing import hash_password
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr
from sqlmodel import select


async def read_user(user_id: int, session: AsyncSessionMaker) -> User:
    user = await session.get(User, user_id)

    if not user:
        raise NotFoundError("The user with specified Id was not found in database!")

    return user


async def read_user_by_email(email: EmailStr, session: AsyncSessionMaker) -> User:
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    user = result.one_or_none()

    if not user:
        raise NotFoundError("The user with specified email was not found in database!")

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
    user_id: int, user_update: UserUpdate, session: AsyncSessionMaker
) -> User:
    user = await read_user(user_id, session)
    for key, value in user_update.model_dump(exclude_none=True).items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)

    return user


async def delete_user(user_id: int, session: AsyncSessionMaker) -> User:
    user = await read_user(user_id, session)
    session.delete(user)
    await session.commit()

    return user
