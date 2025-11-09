import os
import time

db_files = [
    "app/delivery.db",
    "app/worker_app.db",
    "delivery.db",
    "worker_app.db"
]

print("Attempting to delete database files...")
for db_file in db_files:
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✓ Deleted: {db_file}")
        except Exception as e:
            print(f"✗ Could not delete {db_file}: {e}")
    else:
        print(f"- Not found: {db_file}")

print("\nDone!")
