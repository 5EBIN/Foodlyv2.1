# Database schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Payment schemas
class PaymentBase(BaseModel):
    amount: float
    order_id: Optional[int] = None
    status: str = "pending"

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    pickup: str
    dropoff: str
    eta: int
    g_mean: Optional[float] = None
    g_var: Optional[float] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Earnings schemas
class EarningsResponse(BaseModel):
    total_earnings: float
    completed_jobs: list
    period: Optional[str] = None

# Authentication schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: str
