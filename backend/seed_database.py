"""
Seed script to populate the database with dummy data for testing
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import SessionLocal, create_tables
from app.models import models
from app.services.auth_service import hash_password

def clear_database():
    """Clear all existing data"""
    db = SessionLocal()
    try:
        print("\n[Clearing existing data...]")
        db.query(models.Notification).delete()
        db.query(models.Payment).delete()
        db.query(models.Earning).delete()
        db.query(models.Order).delete()
        db.query(models.Agent).delete()
        db.query(models.User).delete()
        db.commit()
        print("✓ Database cleared")
    except Exception as e:
        db.rollback()
        print(f"✗ Error clearing database: {e}")
        raise
    finally:
        db.close()

def seed_users():
    """Create dummy users (customers and agents)"""
    db = SessionLocal()
    try:
        print("\n[Creating users...]")

        # Create customers
        customers = [
            {"username": "customer1", "password": "password123", "is_agent": False},
            {"username": "customer2", "password": "password123", "is_agent": False},
            {"username": "customer3", "password": "password123", "is_agent": False},
            {"username": "customer4", "password": "password123", "is_agent": False},
            {"username": "customer5", "password": "password123", "is_agent": False},
        ]

        # Create agent users
        agents = [
            {"username": "agent1", "password": "password123", "is_agent": True},
            {"username": "agent2", "password": "password123", "is_agent": True},
            {"username": "agent3", "password": "password123", "is_agent": True},
            {"username": "agent4", "password": "password123", "is_agent": True},
        ]

        user_objects = []

        # Create customer users
        for customer_data in customers:
            user = models.User(
                username=customer_data["username"],
                email=f"{customer_data['username']}@example.com",
                hashed_password=hash_password(customer_data["password"]),
                is_active=True,
                is_agent=False
            )
            db.add(user)
            user_objects.append(user)

        # Create agent users
        for agent_data in agents:
            user = models.User(
                username=agent_data["username"],
                email=f"{agent_data['username']}@example.com",
                hashed_password=hash_password(agent_data["password"]),
                is_active=True,
                is_agent=True
            )
            db.add(user)
            user_objects.append(user)

        db.commit()
        print(f"✓ Created {len(customers)} customers and {len(agents)} agent users")
        return user_objects

    except Exception as e:
        db.rollback()
        print(f"✗ Error creating users: {e}")
        raise
    finally:
        db.close()

def seed_agents(agent_users):
    """Create agent profiles"""
    db = SessionLocal()
    try:
        print("\n[Creating agent profiles...]")

        vehicle_types = ["bike", "scooter", "car"]

        agent_profiles = []
        for i, user in enumerate(agent_users):
            if user.is_agent:
                agent = models.Agent(
                    user_id=user.id,
                    active=True,
                    online=random.choice([True, False]),
                    current_work_seconds=random.uniform(0, 3600),
                    active_seconds=random.uniform(7200, 36000),
                    total_deliveries=random.randint(10, 200),
                    last_location={"lat": 40.7128 + random.uniform(-0.1, 0.1),
                                   "lng": -74.0060 + random.uniform(-0.1, 0.1),
                                   "timestamp": datetime.now().isoformat()},
                    rating=random.uniform(4.0, 5.0),
                    total_ratings=random.randint(10, 100),
                    vehicle_type=random.choice(vehicle_types),
                    vehicle_number=f"XYZ-{random.randint(1000, 9999)}",
                    last_active_at=datetime.now() - timedelta(hours=random.randint(0, 24))
                )
                db.add(agent)
                agent_profiles.append(agent)

        db.commit()
        print(f"✓ Created {len(agent_profiles)} agent profiles")
        return agent_profiles

    except Exception as e:
        db.rollback()
        print(f"✗ Error creating agents: {e}")
        raise
    finally:
        db.close()

def seed_orders(customers, agents):
    """Create dummy orders"""
    db = SessionLocal()
    try:
        print("\n[Creating orders...]")

        # NYC coordinates for variety
        locations = [
            {"lat": 40.7589, "lng": -73.9851, "name": "Times Square"},
            {"lat": 40.7484, "lng": -73.9857, "name": "Empire State Building"},
            {"lat": 40.7614, "lng": -73.9776, "name": "Central Park South"},
            {"lat": 40.7580, "lng": -73.9855, "name": "Midtown"},
            {"lat": 40.7505, "lng": -73.9934, "name": "Penn Station"},
            {"lat": 40.7614, "lng": -73.9776, "name": "Columbus Circle"},
        ]

        statuses = ["pending", "assigned", "picked_up", "in_transit", "delivered", "cancelled"]

        orders = []
        for i in range(20):
            pickup = random.choice(locations)
            drop = random.choice([loc for loc in locations if loc != pickup])

            status = random.choice(statuses)

            # Assign agent if not pending
            assigned_agent = None
            if status != "pending" and agents:
                assigned_agent = random.choice(agents)

            order = models.Order(
                user_id=random.choice(customers).id,
                pickup_lat=pickup["lat"],
                pickup_lng=pickup["lng"],
                drop_lat=drop["lat"],
                drop_lng=drop["lng"],
                pickup_address=f"{pickup['name']}, New York, NY",
                drop_address=f"{drop['name']}, New York, NY",
                status=status,
                assigned_agent_id=assigned_agent.id if assigned_agent else None,
                estimated_price=random.uniform(10, 50),
                final_price=random.uniform(10, 50) if status in ["delivered", "cancelled"] else None,
                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                assigned_at=datetime.now() - timedelta(days=random.randint(0, 7)) if status != "pending" else None,
                picked_up_at=datetime.now() - timedelta(hours=random.randint(1, 48)) if status in ["picked_up", "in_transit", "delivered"] else None,
                delivered_at=datetime.now() - timedelta(hours=random.randint(0, 24)) if status == "delivered" else None
            )
            db.add(order)
            orders.append(order)

        db.commit()
        print(f"✓ Created {len(orders)} orders")
        return orders

    except Exception as e:
        db.rollback()
        print(f"✗ Error creating orders: {e}")
        raise
    finally:
        db.close()

def seed_payments(orders):
    """Create payment records for orders"""
    db = SessionLocal()
    try:
        print("\n[Creating payments...]")

        payment_statuses = ["created", "processing", "succeeded", "failed"]
        payment_methods = ["card", "cash", "wallet"]

        payments = []
        for order in orders:
            if order.status in ["delivered", "in_transit", "picked_up"]:
                payment = models.Payment(
                    order_id=order.id,
                    stripe_payment_id=f"pi_{random.randint(100000, 999999)}" if random.random() > 0.5 else None,
                    amount=order.estimated_price or random.uniform(10, 50),
                    currency="USD",
                    status=random.choice(payment_statuses) if order.status != "delivered" else "succeeded",
                    payment_method=random.choice(payment_methods),
                    created_at=order.created_at,
                    completed_at=order.delivered_at if order.status == "delivered" else None
                )
                db.add(payment)
                payments.append(payment)

        db.commit()
        print(f"✓ Created {len(payments)} payments")
        return payments

    except Exception as e:
        db.rollback()
        print(f"✗ Error creating payments: {e}")
        raise
    finally:
        db.close()

def seed_earnings(agents, orders):
    """Create earnings for agents"""
    db = SessionLocal()
    try:
        print("\n[Creating earnings...]")

        earning_types = ["delivery", "bonus", "tip"]

        earnings = []
        for order in orders:
            if order.assigned_agent_id and order.status == "delivered":
                # Main delivery earning
                earning = models.Earning(
                    agent_id=order.assigned_agent_id,
                    order_id=order.id,
                    amount=(order.final_price or order.estimated_price) * 0.75,  # 75% commission
                    earning_type="delivery",
                    timestamp=order.delivered_at
                )
                db.add(earning)
                earnings.append(earning)

                # Random tip
                if random.random() > 0.5:
                    tip = models.Earning(
                        agent_id=order.assigned_agent_id,
                        order_id=order.id,
                        amount=random.uniform(2, 10),
                        earning_type="tip",
                        timestamp=order.delivered_at
                    )
                    db.add(tip)
                    earnings.append(tip)

        # Add some random bonuses
        for agent in agents:
            if random.random() > 0.6:
                bonus = models.Earning(
                    agent_id=agent.id,
                    order_id=None,
                    amount=random.uniform(10, 50),
                    earning_type="bonus",
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                db.add(bonus)
                earnings.append(bonus)

        db.commit()
        print(f"✓ Created {len(earnings)} earnings records")
        return earnings

    except Exception as e:
        db.rollback()
        print(f"✗ Error creating earnings: {e}")
        raise
    finally:
        db.close()

def seed_notifications(users, orders):
    """Create notifications"""
    db = SessionLocal()
    try:
        print("\n[Creating notifications...]")

        notification_types = ["info", "order_update", "payment", "alert"]

        notifications = []
        for user in users[:8]:  # Create notifications for some users
            for i in range(random.randint(2, 5)):
                notification = models.Notification(
                    user_id=user.id,
                    title=f"Notification {i+1}",
                    message=f"This is a test notification for {user.username}",
                    notification_type=random.choice(notification_types),
                    read=random.choice([True, False]),
                    order_id=random.choice(orders).id if random.random() > 0.5 and orders else None,
                    created_at=datetime.now() - timedelta(hours=random.randint(0, 72))
                )
                db.add(notification)
                notifications.append(notification)

        db.commit()
        print(f"✓ Created {len(notifications)} notifications")
        return notifications

    except Exception as e:
        db.rollback()
        print(f"✗ Error creating notifications: {e}")
        raise
    finally:
        db.close()

def main():
    """Main seeding function"""
    print("=" * 60)
    print("Database Seeding Script")
    print("=" * 60)

    # Drop and recreate all tables
    print("\n[Dropping existing tables...]")
    from app.models.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    print("✓ Old tables dropped")

    # Create tables fresh
    print("\n[Creating new tables with updated schema...]")
    create_tables()
    print("✓ Database initialized with new schema")

    # Seed data
    users = seed_users()

    # Separate customers and agent users
    db = SessionLocal()
    all_users = db.query(models.User).all()
    customers = [u for u in all_users if not u.is_agent]
    agent_users = [u for u in all_users if u.is_agent]
    db.close()

    agents = seed_agents(agent_users)

    # Refresh agent profiles to get IDs
    db = SessionLocal()
    agents = db.query(models.Agent).all()
    db.close()

    orders = seed_orders(customers, agents)

    # Refresh orders to get IDs
    db = SessionLocal()
    orders = db.query(models.Order).all()
    db.close()

    payments = seed_payments(orders)
    earnings = seed_earnings(agents, orders)
    notifications = seed_notifications(all_users, orders)

    print("\n" + "=" * 60)
    print("✓ Database seeded successfully!")
    print("=" * 60)
    print("\nSummary:")
    print(f"  - Users: {len(all_users)} (Customers: {len(customers)}, Agents: {len(agent_users)})")
    print(f"  - Agent Profiles: {len(agents)}")
    print(f"  - Orders: {len(orders)}")
    print(f"  - Payments: {len(payments)}")
    print(f"  - Earnings: {len(earnings)}")
    print(f"  - Notifications: {len(notifications)}")
    print("\nTest Credentials:")
    print("  Customer: customer1 / password123")
    print("  Agent: agent1 / password123")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Seeding failed: {e}")
        sys.exit(1)
