from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_agent: bool = False

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_agent: bool

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float

class OrderOut(BaseModel):
    id: int
    status: str
    assigned_agent_id: Optional[int]

    class Config:
        orm_mode = True

class AgentOut(BaseModel):
    id: int
    active: bool
    last_location: Optional[dict]

    class Config:
        orm_mode = True

class EarningsOut(BaseModel):
    agent_id: int
    amount: float
    timestamp: str

