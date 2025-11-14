"""
Customer Orders Router
File: backend/app/routers/customer_orders.py
APIs for customer food delivery orders with ML-based agent assignment
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.schemas import CustomerOrderCreate, CustomerOrderOut, CustomerOrderWithDetails, RestaurantOut
from app.models import models
from app.models.database import get_db
from app.routers.auth import get_current_user
import random

router = APIRouter(prefix="/customer/orders", tags=["customer-orders"])

async def assign_agent_to_order(order_id: int, db: Session):
    """
    Background task to assign best agent using ML
    This will be called asynchronously after order creation
    """
    # Get the order
    order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not order:
        return

    # Get restaurant location
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == order.restaurant_id).first()
    if not restaurant:
        return

    # Get available agents (online and not busy)
    available_agents = db.query(models.Agent).filter(
        models.Agent.online == True,
        models.Agent.active == True
    ).all()

    if not available_agents:
        print(f"[ML Assignment] No available agents for order {order_id}")
        return

    # TODO: Call actual ML service here
    # For now, using simplified logic with random selection weighted by distance
    # In production, this would call your Gaussian Process model

    best_agent = None
    best_score = -1

    for agent in available_agents:
        # Simple scoring: closer agents get higher scores
        # Replace this with actual ML model call
        if agent.last_location:
            agent_lat = agent.last_location.get('lat', 0)
            agent_lng = agent.last_location.get('lng', 0)

            # Simple distance calculation (replace with proper Haversine)
            dist_to_restaurant = abs(restaurant.lat - agent_lat) + abs(restaurant.lng - agent_lng)
            dist_to_delivery = abs(order.delivery_lat - agent_lat) + abs(order.delivery_lng - agent_lng)

            # Simple score (higher is better, closer is better)
            score = 1 / (1 + dist_to_restaurant + dist_to_delivery)

            # Add some randomness to simulate ML variation
            score *= random.uniform(0.8, 1.2)

            if score > best_score:
                best_score = score
                best_agent = agent

    if best_agent:
        # Assign the order
        order.assigned_agent_id = best_agent.id
        order.status = "assigned"
        order.assigned_at = datetime.now()
        order.assignment_score = best_score

        db.commit()
        print(f"[ML Assignment] Order {order_id} assigned to Agent {best_agent.id} (score: {best_score:.4f})")
    else:
        print(f"[ML Assignment] Could not assign order {order_id}")

@router.post("", response_model=CustomerOrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: CustomerOrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new customer order
    Triggers ML-based agent assignment in the background
    """
    # Verify restaurant exists and is active
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == order_in.restaurant_id,
        models.Restaurant.is_active == True
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found or inactive"
        )

    # Create the order
    order = models.CustomerOrder(
        customer_id=current_user.id,
        restaurant_id=order_in.restaurant_id,
        amount=order_in.amount,
        delivery_address=order_in.delivery_address,
        delivery_lat=order_in.delivery_lat,
        delivery_lng=order_in.delivery_lng,
        status="pending",
        payment_status="completed",  # Mock payment
        payment_method="mock"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # Trigger ML-based agent assignment in background
    background_tasks.add_task(assign_agent_to_order, order.id, db)

    return order

@router.get("/active", response_model=Optional[CustomerOrderWithDetails])
def get_active_order(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get customer's current active order
    """
    order = db.query(models.CustomerOrder).filter(
        models.CustomerOrder.customer_id == current_user.id,
        models.CustomerOrder.status.in_(["pending", "assigned", "picked_up", "in_transit"])
    ).order_by(models.CustomerOrder.created_at.desc()).first()

    if not order:
        return None

    # Get restaurant details
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == order.restaurant_id
    ).first()

    # Get agent name if assigned
    agent_name = None
    if order.assigned_agent_id:
        agent = db.query(models.Agent).filter(models.Agent.id == order.assigned_agent_id).first()
        if agent:
            user = db.query(models.User).filter(models.User.id == agent.user_id).first()
            if user:
                agent_name = user.username

    # Build response
    restaurant_out = RestaurantOut(
        id=restaurant.id,
        name=restaurant.name,
        cuisine_type=restaurant.cuisine_type,
        address=restaurant.address,
        lat=restaurant.lat,
        lng=restaurant.lng,
        is_active=restaurant.is_active,
        operating_hours=restaurant.operating_hours,
        image_url=restaurant.image_url,
        rating=restaurant.rating,
        delivery_time=restaurant.delivery_time,
        created_at=restaurant.created_at
    )

    order_dict = {
        "id": order.id,
        "customer_id": order.customer_id,
        "restaurant_id": order.restaurant_id,
        "assigned_agent_id": order.assigned_agent_id,
        "amount": order.amount,
        "delivery_address": order.delivery_address,
        "delivery_lat": order.delivery_lat,
        "delivery_lng": order.delivery_lng,
        "status": order.status,
        "payment_status": order.payment_status,
        "payment_method": order.payment_method,
        "assignment_score": order.assignment_score,
        "created_at": order.created_at,
        "assigned_at": order.assigned_at,
        "picked_up_at": order.picked_up_at,
        "delivered_at": order.delivered_at,
        "restaurant": restaurant_out,
        "agent_name": agent_name
    }

    return CustomerOrderWithDetails(**order_dict)

@router.get("/history", response_model=List[CustomerOrderOut])
def get_order_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get customer's past orders
    """
    orders = db.query(models.CustomerOrder).filter(
        models.CustomerOrder.customer_id == current_user.id,
        models.CustomerOrder.status.in_(["delivered", "cancelled"])
    ).order_by(models.CustomerOrder.created_at.desc()).limit(limit).all()

    return orders

@router.get("/{order_id}", response_model=CustomerOrderWithDetails)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific order by ID
    """
    order = db.query(models.CustomerOrder).filter(
        models.CustomerOrder.id == order_id,
        models.CustomerOrder.customer_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Get restaurant
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == order.restaurant_id
    ).first()

    # Get agent name
    agent_name = None
    if order.assigned_agent_id:
        agent = db.query(models.Agent).filter(models.Agent.id == order.assigned_agent_id).first()
        if agent:
            user = db.query(models.User).filter(models.User.id == agent.user_id).first()
            if user:
                agent_name = user.username

    restaurant_out = RestaurantOut(
        id=restaurant.id,
        name=restaurant.name,
        cuisine_type=restaurant.cuisine_type,
        address=restaurant.address,
        lat=restaurant.lat,
        lng=restaurant.lng,
        is_active=restaurant.is_active,
        operating_hours=restaurant.operating_hours,
        image_url=restaurant.image_url,
        rating=restaurant.rating,
        delivery_time=restaurant.delivery_time,
        created_at=restaurant.created_at
    )

    order_dict = {
        "id": order.id,
        "customer_id": order.customer_id,
        "restaurant_id": order.restaurant_id,
        "assigned_agent_id": order.assigned_agent_id,
        "amount": order.amount,
        "delivery_address": order.delivery_address,
        "delivery_lat": order.delivery_lat,
        "delivery_lng": order.delivery_lng,
        "status": order.status,
        "payment_status": order.payment_status,
        "payment_method": order.payment_method,
        "assignment_score": order.assignment_score,
        "created_at": order.created_at,
        "assigned_at": order.assigned_at,
        "picked_up_at": order.picked_up_at,
        "delivered_at": order.delivered_at,
        "restaurant": restaurant_out,
        "agent_name": agent_name
    }

    return CustomerOrderWithDetails(**order_dict)
