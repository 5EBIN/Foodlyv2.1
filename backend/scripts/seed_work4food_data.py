import random
from datetime import datetime
from typing import Tuple

from app.models.database import SessionLocal, Base, engine
from app.models import models
from app.services.matching.geo_utils import random_point, get_city_center
from app.core.config import settings
from app.services.auth_service import hash_password as get_password_hash

CITY_CENTER: Tuple[float, float] = (settings.CITY_CENTER_LAT, settings.CITY_CENTER_LON)


def seed_test_users(db):
    print("[SEED] Creating test user accounts...")

    # Customer user
    customer_user = models.User(
        username="customer_test",
        email="customer_test@foodly.com",
        hashed_password=get_password_hash("test123"),
        role="customer",
        is_agent=False,
        is_active=True,
        lat=CITY_CENTER[0],
        lng=CITY_CENTER[1],
    )
    db.add(customer_user)
    db.commit()
    db.refresh(customer_user)

    # Agent user + profile
    agent_user = models.User(
        username="agent_test",
        email="agent_test@foodly.com",
        hashed_password=get_password_hash("test123"),
        role="agent",
        is_agent=True,
        is_active=True,
    )
    db.add(agent_user)
    db.commit()
    db.refresh(agent_user)

    lat, lon = random_point(CITY_CENTER, 5)
    agent_profile = models.Agent(
        user_id=agent_user.id,
        active=True,
        online=True,
        last_location_lat=lat,
        last_location_lon=lon,
        speed_kmph=settings.AGENT_SPEED_KMPH,
        work_hours=0.0,
        active_hours=0.0,
        rating=5.0,
        total_ratings=0,
    )
    db.add(agent_profile)

    # Admin user
    admin_user = models.User(
        username="admin_test",
        email="admin_test@foodly.com",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_agent=False,
        is_active=True,
    )
    db.add(admin_user)

    db.commit()

    print("[SEED] Test accounts created:")
    print("[SEED]   Customer: customer_test@foodly.com / test123")
    print("[SEED]   Agent:    agent_test@foodly.com / test123")
    print("[SEED]   Admin:    admin_test@foodly.com / admin123")


def seed_agents(db, count=50):
    print(f"[SEED] Seeding {count} agents...")
    for i in range(count):
        user = models.User(
            username=f"agent_{i}",
            email=f"agent_{i}@foodly.com",
            hashed_password=get_password_hash("password123"),
            role="agent",
            is_agent=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        lat, lon = random_point(CITY_CENTER, settings.CITY_RADIUS_KM)
        agent = models.Agent(
            user_id=user.id,
            active=True,
            online=bool(i % 2),
            last_location_lat=lat,
            last_location_lon=lon,
            speed_kmph=settings.AGENT_SPEED_KMPH,
        )
        db.add(agent)
    db.commit()
    print("[SEED] Agents seeded")


def seed_restaurants(db, count=20):
    print(f"[SEED] Seeding {count} restaurants...")
    for i in range(count):
        lat, lon = random_point(CITY_CENTER, settings.CITY_RADIUS_KM)
        restaurant = models.Restaurant(
            name=f"Restaurant {i}",
            cuisine_type=random.choice(["Indian", "Chinese", "Italian"]),
            address=f"Address {i}",
            lat=lat,
            lng=lon,
            is_active=True,
            rating=4.0,
            delivery_time=30,
        )
        db.add(restaurant)
    db.commit()
    print("[SEED] Restaurants seeded")


def seed_customers(db, count=30):
    print(f"[SEED] Seeding {count} customers...")
    for i in range(count):
        lat, lon = random_point(CITY_CENTER, settings.CITY_RADIUS_KM)
        user = models.User(
            username=f"customer_{i}",
            email=f"customer_{i}@foodly.com",
            hashed_password=get_password_hash("password123"),
            role="customer",
            is_agent=False,
            is_active=True,
            lat=lat,
            lng=lon,
        )
        db.add(user)
    db.commit()
    print("[SEED] Customers seeded")


def main():
    db = SessionLocal()
    try:
        # Reset schema for development seeding
        print("[SEED] Resetting database schema...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        seed_test_users(db)
        seed_agents(db, 50)
        seed_restaurants(db, 20)
        seed_customers(db, 30)
        print("[SEED] Seeding complete")
    finally:
        db.close()


if __name__ == "__main__":
    main()


