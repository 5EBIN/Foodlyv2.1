"""
Pydantic Schemas
File: backend/app/schemas.py
Request/Response models for API validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ============================================
# User Schemas
# ============================================

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    is_agent: bool = False

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    is_active: bool
    is_agent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for decoded token data"""
    user_id: Optional[int] = None

# ============================================
# Order Schemas
# ============================================

class OrderCreate(BaseModel):
    """Schema for creating a new order"""
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lng: float = Field(..., ge=-180, le=180)
    drop_lat: float = Field(..., ge=-90, le=90)
    drop_lng: float = Field(..., ge=-180, le=180)
    pickup_address: Optional[str] = None
    drop_address: Optional[str] = None

class OrderUpdate(BaseModel):
    """Schema for updating order status"""
    status: str = Field(..., pattern="^(pending|assigned|picked_up|in_transit|delivered|cancelled)$")

class OrderOut(BaseModel):
    """Schema for order response"""
    id: int
    user_id: int
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float
    pickup_address: Optional[str]
    drop_address: Optional[str]
    status: str
    assigned_agent_id: Optional[int]
    estimated_price: Optional[float]
    final_price: Optional[float]
    created_at: datetime
    assigned_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ============================================
# Agent Schemas
# ============================================

class AgentUpdate(BaseModel):
    """Schema for updating agent profile"""
    active: Optional[bool] = None
    online: Optional[bool] = None
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None

class LocationUpdate(BaseModel):
    """Schema for agent location update"""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class AgentOut(BaseModel):
    """Schema for agent response"""
    id: int
    user_id: int
    active: bool
    online: bool
    current_work_seconds: float
    active_seconds: float
    total_deliveries: int
    rating: float
    total_ratings: int
    vehicle_type: Optional[str]
    vehicle_number: Optional[str]
    last_location: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================
# Payment Schemas
# ============================================

class PaymentCreate(BaseModel):
    """Schema for creating a payment"""
    order_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(card|cash|wallet)$")

class PaymentOut(BaseModel):
    """Schema for payment response"""
    id: int
    order_id: int
    stripe_payment_id: Optional[str]
    amount: float
    currency: str
    status: str
    payment_method: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ============================================
# Earning Schemas
# ============================================

class EarningOut(BaseModel):
    """Schema for earning response"""
    id: int
    agent_id: int
    order_id: Optional[int]
    amount: float
    earning_type: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class EarningsSummary(BaseModel):
    """Schema for agent earnings summary"""
    total_earnings: float
    today_earnings: float
    this_week_earnings: float
    this_month_earnings: float
    total_deliveries: int

# ============================================
# Notification Schemas
# ============================================

class NotificationOut(BaseModel):
    """Schema for notification response"""
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    read: bool
    order_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
