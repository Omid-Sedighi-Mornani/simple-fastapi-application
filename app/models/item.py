from sqlmodel import SQLModel, Field, ForeignKey, Relationship
from typing import Optional


class Item(SQLModel, table=True):
    __tablename__ = "items"
    id: int = Field(primary_key=True)
    name: str
    price: float
    user_id: int = Field(foreign_key="users.id")

    user: Optional["User"] = Relationship(back_populates="items")
