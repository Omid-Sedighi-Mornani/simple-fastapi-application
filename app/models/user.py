from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from schemas.user import UserBase
from pydantic import field_serializer
from pydantic_core import PydanticUndefined


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    verified: bool = Field(default=False)

    items: List["Item"] = Relationship(back_populates="user")

    @field_serializer("hashed_password", return_type=str)
    def hide_password(self, hashed_password: str, _info) -> dict:
        return "***"
