from sqlmodel import SQLModel, Field
from pydantic import EmailStr, StringConstraints
from typing import Annotated, Optional
from pydantic import BaseModel

PasswordStr = Annotated[str, StringConstraints(min_length=8)]


class UserBase(SQLModel):
    username: str
    email: EmailStr = Field(unique=True)


class UserCreate(UserBase):
    password: PasswordStr


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[PasswordStr] = None
    verified: Optional[bool] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: PasswordStr
