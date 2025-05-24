from sqlmodel import SQLModel, Field
from pydantic import EmailStr, StringConstraints
from typing import Annotated


class UserBase(SQLModel):
    username: str
    email: EmailStr = Field(unique=True)


class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8)]
