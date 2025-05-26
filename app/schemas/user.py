from sqlmodel import SQLModel, Field
from pydantic import EmailStr, StringConstraints
from typing import Annotated, Optional

PasswordStr = Annotated[str, StringConstraints(min_length=8)]


class UserBase(SQLModel):
    username: str
    email: EmailStr = Field(unique=True)


class UserCreate(UserBase):
    password: PasswordStr


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[PasswordStr] = None
    verified: Optional[bool] = None
