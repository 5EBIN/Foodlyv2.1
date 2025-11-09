"""
Restaurant Seeding Script
Populates database with dummy restaurant data for testing
"""
import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import SessionLocal, create_tables
from app.models import models

# NYC coordinates for realistic testing
NYC_CENTER = (40.7128, -74.0060)

RESTAURANTS = [
    {
        "name": "Pizza Palace",
        "cuisine_type": "Italian",
        "address": "123 Broadway, New York, NY 10001",
        "lat": 40.7489,
        "lng": -73.9680,
        "rating": 4.5,
        "delivery_time": 25,
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591"
    },
    {
        "name": "Burger Haven",
        "cuisine_type": "American",
        "address": "456 5th Ave, New York, NY 10018",
        "lat": 40.7522,
        "lng": -73.9767,
        "rating": 4.3,
        "delivery_time": 20,
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd"
    },
    {
        "name": "Sushi Express",
        "cuisine_type": "Japanese",
        "address": "789 Lexington Ave, New York, NY 10065",
        "lat": 40.7614,
        "lng": -73.9776,
        "rating": 4.7,
        "delivery_time": 35,
        "image_url": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351"
    },
    {
        "name": "Taco Fiesta",
        "cuisine_type": "Mexican",
        "address": "321 Park Ave, New York, NY 10022",
        "lat": 40.7540,
        "lng": -73.9732,
        "rating": 4.2,
        "delivery_time": 22,
        "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47"
    },
    {
        "name": "Curry House",
        "cuisine_type": "Indian",
        "address": "555 Madison Ave, New York, NY 10022",
        "lat": 40.7585,
        "lng": -73.9743,
        "rating": 4.6,
        "delivery_time": 30,
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe"
    },
    {
        "name": "Noodle Bar",
        "cuisine_type": "Chinese",
        "address": "888 8th Ave, New York, NY 10019",
        "lat": 40.7619,
        "lng": -73.9858,
        "rating": 4.4,
        "delivery_time": 28,
        "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624"
    },
    {
        "name": "Mediterranean Grill",
        "cuisine_type": "Mediterranean",
        "address": "234 West St, New York, NY 10014",
        "lat": 40.7347,
        "lng": -74.0089,
        "rating": 4.5,
        "delivery_time": 32,
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947"
    },
    {
        "name": "Thai Spice",
        "cuisine_type": "Thai",
        "address": "777 3rd Ave, New York, NY 10017",
        "lat": 40.7527,
        "lng": -73.9723,
        "rating": 4.3,
        "delivery_time": 27,
        "image_url": "https://images.unsplash.com/photo-1559314809-0d155014e29e"
    },
    {
        "name": "Steakhouse Prime",
        "cuisine_type": "Steakhouse",
        "address": "999 6th Ave, New York, NY 10018",
        "lat": 40.7556,
        "lng": -73.9800,
        "rating": 4.8,
        "delivery_time": 40,
        "image_url": "https://images.unsplash.com/photo-1600891964092-4316c288032e"
    },
    {
        "name": "Vegan Delights",
        "cuisine_type": "Vegan",
        "address": "444 Houston St, New York, NY 10014",
        "lat": 40.7280,
        "lng": -74.0005,
        "rating": 4.6,
        "delivery_time": 26,
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
    },
    {
        "name": "BBQ Shack",
        "cuisine_type": "BBQ",
        "address": "111 Canal St, New York, NY 10013",
        "lat": 40.7182,
        "lng": -74.0025,
        "rating": 4.4,
        "delivery_time": 35,
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947"
    },
    {
        "name": "Breakfast Club",
        "cuisine_type": "Breakfast",
        "address": "222 Bleecker St, New York, NY 10012",
        "lat": 40.7294,
        "lng": -74.0007,
        "rating": 4.5,
        "delivery_time": 18,
        "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666"
    },
    {
        "name": "Poke Bowl Paradise",
        "cuisine_type": "Hawaiian",
        "address": "333 Lafayette St, New York, NY 10012",
        "lat": 40.7240,
        "lng": -73.9963,
        "rating": 4.3,
        "delivery_time": 24,
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
    },
    {
        "name": "Ramen Station",
        "cuisine_type": "Japanese",
        "address": "666 Broadway, New York, NY 10012",
        "lat": 40.7259,
        "lng": -73.9966,
        "rating": 4.7,
        "delivery_time": 29,
        "image_url": "https://images.unsplash.com/photo-1557872943-16a5ac26437e"
    },
    {
        "name": "Salad Bar NYC",
        "cuisine_type": "Healthy",
        "address": "555 Spring St, New York, NY 10013",
        "lat": 40.7259,
        "lng": -74.0033,
        "rating": 4.2,
        "delivery_time": 20,
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
    }
]

def seed_restaurants():
    """Seed restaurant data"""
    print("=" * 60)
    print("Restaurant Seeding Script")
    print("=" * 60)

    # Create tables
    print("\n[Creating tables...]")
    create_tables()
    print("✓ Tables ready")

    db = SessionLocal()

    try:
        # Check if restaurants already exist
        existing_count = db.query(models.Restaurant).count()
        if existing_count > 0:
            print(f"\n[INFO] {existing_count} restaurants already exist")
            response = input("Delete existing restaurants and reseed? (y/n): ")
            if response.lower() == 'y':
                db.query(models.Restaurant).delete()
                db.commit()
                print("✓ Existing restaurants deleted")
            else:
                print("Keeping existing restaurants")
                return

        # Add restaurants
        print(f"\n[Adding {len(RESTAURANTS)} restaurants...]")
        for restaurant_data in RESTAURANTS:
            restaurant = models.Restaurant(**restaurant_data, is_active=True)
            db.add(restaurant)

        db.commit()
        print(f"✓ Added {len(RESTAURANTS)} restaurants")

        # Display summary
        print("\n" + "=" * 60)
        print("✓ Restaurant seeding completed!")
        print("=" * 60)
        print("\nRestaurant Summary:")
        for restaurant in db.query(models.Restaurant).all():
            print(f"  - {restaurant.name} ({restaurant.cuisine_type}) - {restaurant.delivery_time} min")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        seed_restaurants()
    except Exception as e:
        print(f"\n✗ Seeding failed: {e}")
        sys.exit(1)
