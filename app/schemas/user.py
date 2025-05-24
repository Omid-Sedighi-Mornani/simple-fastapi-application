from sqlmodel import SQLModel


class UserBase(SQLModel):
    username: str


class UserCreate(UserBase):
    password: str
