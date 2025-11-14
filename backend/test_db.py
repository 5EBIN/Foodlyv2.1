"""
Test script to verify SQLite database connectivity
"""
import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import Base, engine, SessionLocal, create_tables
from app.models import models
from sqlalchemy import text

def test_database():
    """Test database connection and basic operations"""

    print("=" * 60)
    print("SQLite Database Connection Test")
    print("=" * 60)

    # Step 1: Create tables
    print("\n[1] Creating database tables...")
    try:
        create_tables()
        print("✓ Tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

    # Step 2: Test connection
    print("\n[2] Testing database connection...")
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    finally:
        db.close()

    # Step 3: Verify tables exist
    print("\n[3] Verifying tables...")
    try:
        db = SessionLocal()

        # Get all table names
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        table_names = [t[0] for t in tables]

        print(f"✓ Found {len(table_names)} tables:")
        for table in table_names:
            print(f"  - {table}")

        # Check expected tables
        expected_tables = ['users', 'orders', 'agents', 'earnings', 'payments', 'notifications']
        missing_tables = [t for t in expected_tables if t not in table_names]

        if missing_tables:
            print(f"⚠ Missing tables: {missing_tables}")
        else:
            print("✓ All expected tables present")

    except Exception as e:
        print(f"✗ Error verifying tables: {e}")
        return False
    finally:
        db.close()

    # Step 4: Test basic CRUD
    print("\n[4] Testing basic database operations...")
    try:
        db = SessionLocal()

        # Count users
        user_count = db.query(models.User).count()
        print(f"✓ Users in database: {user_count}")

        # Count orders
        order_count = db.query(models.Order).count()
        print(f"✓ Orders in database: {order_count}")

        # Count agents
        agent_count = db.query(models.Agent).count()
        print(f"✓ Agents in database: {agent_count}")

    except Exception as e:
        print(f"✗ Error during CRUD test: {e}")
        return False
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("✓ All tests passed! SQLite is working properly.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
