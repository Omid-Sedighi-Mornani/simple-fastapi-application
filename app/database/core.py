from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from typing import AsyncGenerator
import os
from typing import Annotated
from models.user import User
from models.item import Item
from fastapi import Depends

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


AsyncSessionMaker = Annotated[AsyncSession, Depends(get_async_session)]


class NotFoundError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass
