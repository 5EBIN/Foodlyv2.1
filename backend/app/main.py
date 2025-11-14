"""
FastAPI Application Main Entry Point
File: backend/app/main.py
Complete setup with database initialization and routes
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.models.database import Base, engine, create_tables
from app.core.batch_scheduler import start_scheduler
from app.models import models  # Import all models to register them
from app.routers import auth
from app.routers import restaurants, customer_orders, earnings, agents, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler
    Runs on startup and shutdown
    """
    # Startup: Create database tables
    print("[STARTUP] Starting up...")
    print(f"[DATABASE] Database: {settings.DATABASE_URL}")
    
    # Create all tables
    if "sqlite" in settings.DATABASE_URL:
        create_tables()
    else:
        # For PostgreSQL, you'd use create_tables_async()
        print("[WARNING] PostgreSQL detected - implement async table creation")
    
    print("[SUCCESS] Application ready!")
    # Start WORK4FOOD batch scheduler
    try:
        app.state.scheduler = start_scheduler()
        logging.getLogger(__name__).info("WORK4FOOD scheduler started")
    except Exception as e:
        logging.getLogger(__name__).exception(f"Failed to start scheduler: {e}")
    
    yield
    
    # Shutdown
    print("[SHUTDOWN] Shutting down...")
    # Stop scheduler if running
    scheduler = getattr(app.state, "scheduler", None)
    if scheduler:
        try:
            scheduler.shutdown()
        except Exception:
            pass

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Delivery service API with real-time order tracking",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Delivery Service API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION
    }

# Include routers
app.include_router(auth.router, prefix="/api")

# Import and include new routers
app.include_router(restaurants.router, prefix="/api")
app.include_router(customer_orders.router, prefix="/api")
app.include_router(earnings.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# You can add more routers here:
# from app.routers import orders, agents, payments
# app.include_router(orders.router, prefix="/api")
# app.include_router(agents.router, prefix="/api")
# app.include_router(payments.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
