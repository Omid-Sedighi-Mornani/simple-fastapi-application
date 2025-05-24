from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from schemas.user import UserBase


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    verified: bool = Field(default=False)

    items: List["Item"] = Relationship(back_populates="user")
