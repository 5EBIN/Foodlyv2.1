from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_agent = Column(Boolean, default=False)  # driver or consumer
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pickup_lat = Column(Float)
    pickup_lng = Column(Float)
    drop_lat = Column(Float)
    drop_lng = Column(Float)
    status = Column(String, default="pending")  # pending, assigned, delivered
    assigned_agent_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    active = Column(Boolean, default=True)
    current_work_seconds = Column(Float, default=0.0)  # Wv
    active_seconds = Column(Float, default=0.0)        # Av
    last_location = Column(JSON, nullable=True)        # {"lat":.., "lng":..}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Earning(Base):
    __tablename__ = "earnings"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    amount = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    stripe_payment_id = Column(String, nullable=True)
    amount = Column(Float)
    status = Column(String, default="created")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

