"""
Migration script to add username column to existing users table
"""
import sys
import os
import sqlite3

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Add username column and populate it from email"""

    db_path = "app/delivery.db"

    print("=" * 60)
    print("Database Migration: Add Username Column")
    print("=" * 60)

    if not os.path.exists(db_path):
        print(f"\n✗ Database not found at {db_path}")
        print("  Creating new database with updated schema...")
        from app.models.database import create_tables
        create_tables()
        print("✓ New database created with username field")
        return True

    print(f"\n[Connecting to database: {db_path}]")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if username column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'username' in columns:
            print("✓ Username column already exists")
            return True

        print("\n[Adding username column...]")

        # Add username column (nullable first)
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
        conn.commit()
        print("✓ Username column added")

        # Populate username from email
        print("\n[Populating usernames from emails...]")
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()

        for user_id, email in users:
            # Extract username from email (part before @)
            username = email.split('@')[0] if email else f"user{user_id}"
            cursor.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))

        conn.commit()
        print(f"✓ Updated {len(users)} users with usernames")

        # Make email optional (we can't easily add NOT NULL to existing column in SQLite)
        # This would require recreating the table, which is complex
        print("\n⚠ Note: Email column is still required in existing schema")
        print("  For full migration, consider recreating the database")

        # Create unique index on username
        print("\n[Creating unique index on username...]")
        try:
            cursor.execute("CREATE UNIQUE INDEX idx_users_username ON users(username)")
            conn.commit()
            print("✓ Unique index created on username")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print("✓ Index already exists")
            else:
                raise

        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)

        # Show updated users
        print("\nUpdated users:")
        cursor.execute("SELECT id, username, email, is_agent FROM users")
        for row in cursor.fetchall():
            user_type = "Agent" if row[3] else "Customer"
            print(f"  {user_type}: {row[1]} (email: {row[2]})")

        return True

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
