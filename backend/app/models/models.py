"""
Complete Database Models
File: backend/app/models/models.py
All tables with proper relationships and indexes
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, Text, Index, Enum
import enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base

class User(Base):
    """
    User table - stores both customers and agents
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)  # Made optional
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="customer", index=True)  # admin, agent, customer
    is_agent = Column(Boolean, default=False, index=True)

    # Customer profile fields
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")
    agent_profile = relationship("Agent", back_populates="user", uselist=False)
    customer_orders = relationship("CustomerOrder", back_populates="customer", foreign_keys="CustomerOrder.customer_id")

class Restaurant(Base):
    """
    Restaurant table - stores restaurant information
    """
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cuisine_type = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    lat = Column(Float, nullable=False, index=True)
    lng = Column(Float, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    operating_hours = Column(JSON, nullable=True)  # {"monday": {"open": "09:00", "close": "22:00"}, ...}
    image_url = Column(String(500), nullable=True)
    rating = Column(Float, default=4.0)
    delivery_time = Column(Integer, default=30)  # minutes
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    customer_orders = relationship("CustomerOrder", back_populates="restaurant")

class Order(Base):
    """
    Order table - delivery orders
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Location coordinates
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    drop_lat = Column(Float, nullable=False)
    drop_lng = Column(Float, nullable=False)
    
    # Optional address details
    pickup_address = Column(Text, nullable=True)
    drop_address = Column(Text, nullable=True)
    
    # Order status: pending, assigned, picked_up, in_transit, delivered, cancelled
    status = Column(String(50), default="pending", index=True)
    
    # Agent assignment
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    
    # Pricing
    estimated_price = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    assigned_at = Column(DateTime, nullable=True)
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders", foreign_keys=[user_id])
    agent = relationship("Agent", back_populates="assigned_orders", foreign_keys=[assigned_agent_id])
    payment = relationship("Payment", back_populates="order", uselist=False)

    # WORK4FOOD batching & matching metadata
    batch_id = Column(String(64), nullable=True, index=True)  # e.g., batch_YYYYMMDD_HHMMSS
    batch_window_start = Column(DateTime, nullable=True, index=True)
    estimated_work_hours = Column(Float, default=0.0)
    actual_work_hours = Column(Float, nullable=True)
    assignment_cost = Column(Float, nullable=True)

class AgentStatus(enum.Enum):
    available = "available"
    en_route = "en_route"
    delivering = "delivering"
    offline = "offline"


class Agent(Base):
    """
    Agent table - delivery agents
    """
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Agent status
    active = Column(Boolean, default=True, index=True)
    online = Column(Boolean, default=False)
    
    # Work tracking (in seconds)
    current_work_seconds = Column(Float, default=0.0)
    active_seconds = Column(Float, default=0.0)
    total_deliveries = Column(Integer, default=0)
    
    # Location tracking
    last_location = Column(JSON, nullable=True)  # retained for backward-compat
    last_location_lat = Column(Float, nullable=True)
    last_location_lon = Column(Float, nullable=True)
    
    # Ratings
    rating = Column(Float, default=5.0)
    total_ratings = Column(Integer, default=0)
    
    # Vehicle info
    vehicle_type = Column(String(50), nullable=True)  # bike, scooter, car
    vehicle_number = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    last_active_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="agent_profile")
    assigned_orders = relationship("Order", back_populates="agent", foreign_keys="Order.assigned_agent_id")
    earnings = relationship("Earning", back_populates="agent")

    # WORK4FOOD tracking fields
    # Hours in hours (not seconds) for compatibility with WORK4FOOD notation
    work_hours = Column(Float, default=0.0)  # W_t
    active_hours = Column(Float, default=0.0)  # A_t
    earnings_total = Column(Float, default=0.0)  # cumulative earnings
    handout = Column(Float, default=0.0)  # guarantee compensation
    total_pay = Column(Float, default=0.0)  # earnings_total + handout
    speed_kmph = Column(Float, default=25.0)
    status = Column(Enum(AgentStatus), default=AgentStatus.available, nullable=False, index=True)

class Earning(Base):
    """
    Earnings table - tracks agent earnings
    """
    __tablename__ = "earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    amount = Column(Float, default=0.0, nullable=False)
    earning_type = Column(String(50), default="delivery")  # delivery, bonus, tip
    
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="earnings")

class Payment(Base):
    """
    Payment table - tracks customer payments
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    # Stripe integration
    stripe_payment_id = Column(String(255), nullable=True, unique=True)
    stripe_payment_intent = Column(String(255), nullable=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    # Payment status: created, processing, succeeded, failed, refunded
    status = Column(String(50), default="created", index=True)
    
    payment_method = Column(String(50), nullable=True)  # card, cash, wallet
    
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payment")

class Notification(Base):
    """
    Notification table - push notifications to users/agents
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")  # info, order_update, payment, alert
    
    read = Column(Boolean, default=False, index=True)
    
    # Optional order reference
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), index=True)

class CustomerOrder(Base):
    """
    CustomerOrder table - food delivery orders from restaurants
    This is the main order type for the customer-facing app
    """
    __tablename__ = "customer_orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)

    # Order details
    amount = Column(Float, nullable=False)
    delivery_address = Column(Text, nullable=False)
    delivery_lat = Column(Float, nullable=False)
    delivery_lng = Column(Float, nullable=False)

    # Status: pending, assigned, picked_up, in_transit, delivered, cancelled
    status = Column(String(50), default="pending", index=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    assigned_at = Column(DateTime, nullable=True)
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Payment
    payment_status = Column(String(50), default="pending")  # pending, completed, failed
    payment_method = Column(String(50), default="mock")  # mock, card, cash

    # ML assignment scores (for tracking)
    assignment_score = Column(Float, nullable=True)  # G-value or matching score

    # Relationships
    customer = relationship("User", back_populates="customer_orders", foreign_keys=[customer_id])
    restaurant = relationship("Restaurant", back_populates="customer_orders")
    agent = relationship("Agent", foreign_keys=[assigned_agent_id])

class BatchAssignment(Base):
    """
    BatchAssignment table - tracks matching runs (3-minute windows)
    """
    __tablename__ = "batch_assignments"

    id = Column(String(36), primary_key=True)  # UUID string
    batch_id = Column(String(64), nullable=False, unique=True, index=True)
    window_start = Column(DateTime, nullable=False, index=True)
    window_end = Column(DateTime, nullable=False)
    total_orders = Column(Integer, default=0)
    assigned_orders = Column(Integer, default=0)
    guarantee_ratio = Column(Float, default=0.25)
    created_at = Column(DateTime, server_default=func.now())

# Create indexes for better query performance
Index('idx_orders_status_agent', Order.status, Order.assigned_agent_id)
Index('idx_orders_user_status', Order.user_id, Order.status)
Index('idx_orders_batch_id', Order.batch_id)
Index('idx_orders_batch_window', Order.batch_window_start)
Index('idx_earnings_agent_timestamp', Earning.agent_id, Earning.timestamp)
Index('idx_payments_order_status', Payment.order_id, Payment.status)
Index('idx_customer_orders_status', CustomerOrder.status)
Index('idx_customer_orders_customer', CustomerOrder.customer_id, CustomerOrder.status)
Index('idx_customer_orders_agent', CustomerOrder.assigned_agent_id, CustomerOrder.status)
Index('idx_agent_status', Agent.status)
