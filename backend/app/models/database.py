"""
Fixed Database Configuration
File: backend/app/models/database.py
Key fixes:
1. Single Base object for all models
2. Proper SQLite/PostgreSQL detection
3. Correct async/sync session handling
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from app.core.config import settings

# CREATE A SINGLE Base FOR ALL MODELS
# This is critical - all models must use this same Base
Base = declarative_base()

# Determine database type from DATABASE_URL
if "sqlite" in settings.DATABASE_URL:
    # ============================================
    # SQLite Setup (Synchronous)
    # ============================================
    
    # Handle relative paths for SQLite
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    # Convert to absolute path if relative
    if not os.path.isabs(db_path):
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(backend_dir, db_path)
    
    # Create sync engine for SQLite
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
    )
    
    # Create sync session factory
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
    
    # Sync dependency for FastAPI routes
    def get_db():
        """
        Dependency for SQLite (synchronous)
        Use in routes like: db: Session = Depends(get_db)
        """
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
else:
    # ============================================
    # PostgreSQL Setup (Asynchronous)
    # ============================================
    
    # Create async engine for PostgreSQL
    engine = create_async_engine(
        settings.DATABASE_URL,
        future=True,
        echo=False
    )
    
    # Create async session factory
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Async dependency for FastAPI routes
    async def get_db():
        """
        Dependency for PostgreSQL (asynchronous)
        Use in routes like: db: AsyncSession = Depends(get_db)
        """
        async with AsyncSessionLocal() as session:
            yield session

# Utility function to create all tables
def create_tables():
    """
    Create all tables defined in models.
    Call this once on application startup.
    
    For SQLite: Works directly
    For PostgreSQL: Need to use async version
    """
    if "sqlite" in settings.DATABASE_URL:
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] SQLite tables created successfully")
    else:
        print("[WARNING] For PostgreSQL, use create_tables_async() instead")

async def create_tables_async():
    """
    Async version for PostgreSQL.
    Call this from an async context on startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("[SUCCESS] PostgreSQL tables created successfully")
