"""
Restaurant Router
File: backend/app/routers/restaurants.py
APIs for restaurant management and listing
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas import RestaurantCreate, RestaurantOut
from app.models import models
from app.models.database import get_db
from app.routers.auth import get_current_user
import math

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

@router.get("", response_model=List[RestaurantOut])
def list_restaurants(
    lat: Optional[float] = Query(None, description="User's latitude for distance calculation"),
    lng: Optional[float] = Query(None, description="User's longitude for distance calculation"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine type"),
    max_distance: Optional[float] = Query(None, description="Maximum distance in km"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all active restaurants
    Optionally filter by distance and cuisine
    """
    query = db.query(models.Restaurant).filter(models.Restaurant.is_active == True)

    if cuisine:
        query = query.filter(models.Restaurant.cuisine_type.ilike(f"%{cuisine}%"))

    restaurants = query.all()

    # Calculate distances if user location provided
    result = []
    for restaurant in restaurants:
        restaurant_dict = {
            "id": restaurant.id,
            "name": restaurant.name,
            "cuisine_type": restaurant.cuisine_type,
            "address": restaurant.address,
            "lat": restaurant.lat,
            "lng": restaurant.lng,
            "is_active": restaurant.is_active,
            "operating_hours": restaurant.operating_hours,
            "image_url": restaurant.image_url,
            "rating": restaurant.rating,
            "delivery_time": restaurant.delivery_time,
            "created_at": restaurant.created_at,
            "distance": None
        }

        if lat is not None and lng is not None:
            distance = calculate_distance(lat, lng, restaurant.lat, restaurant.lng)
            restaurant_dict["distance"] = round(distance, 2)

            # Filter by max distance if specified
            if max_distance and distance > max_distance:
                continue

        result.append(RestaurantOut(**restaurant_dict))

    # Sort by distance if available
    if lat is not None and lng is not None:
        result.sort(key=lambda x: x.distance if x.distance is not None else float('inf'))

    return result

@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(
    restaurant_id: int,
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a single restaurant by ID
    """
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id,
        models.Restaurant.is_active == True
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    restaurant_dict = {
        "id": restaurant.id,
        "name": restaurant.name,
        "cuisine_type": restaurant.cuisine_type,
        "address": restaurant.address,
        "lat": restaurant.lat,
        "lng": restaurant.lng,
        "is_active": restaurant.is_active,
        "operating_hours": restaurant.operating_hours,
        "image_url": restaurant.image_url,
        "rating": restaurant.rating,
        "delivery_time": restaurant.delivery_time,
        "created_at": restaurant.created_at,
        "distance": None
    }

    if lat is not None and lng is not None:
        distance = calculate_distance(lat, lng, restaurant.lat, restaurant.lng)
        restaurant_dict["distance"] = round(distance, 2)

    return RestaurantOut(**restaurant_dict)

@router.post("", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    restaurant_in: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new restaurant (admin only - simplified for now)
    """
    # TODO: Add admin check when role system is implemented

    restaurant = models.Restaurant(
        name=restaurant_in.name,
        cuisine_type=restaurant_in.cuisine_type,
        address=restaurant_in.address,
        lat=restaurant_in.lat,
        lng=restaurant_in.lng,
        operating_hours=restaurant_in.operating_hours,
        image_url=restaurant_in.image_url,
        rating=restaurant_in.rating or 4.0,
        delivery_time=restaurant_in.delivery_time or 30,
        is_active=True
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant
