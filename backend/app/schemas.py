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
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None
    is_agent: bool = False

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class UserOut(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: Optional[str]
    is_active: bool
    is_agent: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    user_type: Optional[str] = None

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

# ============================================
# Restaurant Schemas
# ============================================

class RestaurantCreate(BaseModel):
    """Schema for creating a restaurant (admin only)"""
    name: str = Field(..., min_length=1, max_length=255)
    cuisine_type: Optional[str] = None
    address: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    operating_hours: Optional[dict] = None
    image_url: Optional[str] = None
    rating: Optional[float] = Field(default=4.0, ge=0, le=5)
    delivery_time: Optional[int] = Field(default=30, gt=0)

class RestaurantOut(BaseModel):
    """Schema for restaurant response"""
    id: int
    name: str
    cuisine_type: Optional[str]
    address: str
    lat: float
    lng: float
    is_active: bool
    operating_hours: Optional[dict]
    image_url: Optional[str]
    rating: float
    delivery_time: int
    created_at: datetime
    distance: Optional[float] = None  # Calculated field for distance from user

    class Config:
        from_attributes = True

# ============================================
# Customer Order Schemas
# ============================================

class CustomerOrderCreate(BaseModel):
    """Schema for creating a customer order"""
    restaurant_id: int
    amount: float = Field(..., gt=0)
    delivery_address: str
    delivery_lat: float = Field(..., ge=-90, le=90)
    delivery_lng: float = Field(..., ge=-180, le=180)

class CustomerOrderOut(BaseModel):
    """Schema for customer order response"""
    id: int
    customer_id: int
    restaurant_id: int
    assigned_agent_id: Optional[int]
    amount: float
    delivery_address: str
    delivery_lat: float
    delivery_lng: float
    status: str
    payment_status: str
    payment_method: str
    assignment_score: Optional[float]
    created_at: datetime
    assigned_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    delivered_at: Optional[datetime]

    # Nested objects (optional, populate on demand)
    restaurant: Optional[RestaurantOut] = None

    class Config:
        from_attributes = True

class CustomerOrderWithDetails(CustomerOrderOut):
    """Extended customer order with full details"""
    restaurant: RestaurantOut
    agent_name: Optional[str] = None
