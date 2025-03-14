from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    account_id: UUID
    account_short_code: str
    password: str 
    phone_no: Optional[str] = "123-543-2913"
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    email: Optional[str]

class LoginRequest(BaseModel):
    email: Optional[str]

class LoggedInUser(BaseModel):
    email: Optional[str] = None
    account_id: str
    account_short_code: str
    user_id: str

class UserLogin(BaseModel):
    email: Optional[str] = None
    password: str 
    account_short_code: Optional[str] = None

class UserCreate(BaseModel):
    email: Optional[str] = None
    account_shortcode: str
    password: str 
    phone_no: Optional[str] = None