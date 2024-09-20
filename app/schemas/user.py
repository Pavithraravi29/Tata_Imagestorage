from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True

class Token(BaseModel):
    message: str
    access_token: str
    token_type: str

class UserRegistrationResponse(BaseModel):
    message: str
    user: User