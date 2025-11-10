"""
Configuration Settings
File: backend/app/core/config.py
Environment variables and app configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application
    APP_NAME: str = "Delivery Service API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./delivery.db"  # Default to SQLite
    # For PostgreSQL, use: postgresql+asyncpg://user:password@localhost/dbname
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8081", "*"]
    
    # Stripe (for payments)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Google Maps API (for distance calculations)
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # Pricing
    BASE_DELIVERY_PRICE: float = 5.0
    PRICE_PER_KM: float = 1.5
    PRICE_PER_MINUTE: float = 0.5
    
    # Agent earnings split
    AGENT_COMMISSION_PERCENTAGE: float = 75.0  # Agent gets 75% of delivery fee
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ML Service
    ML_SERVICE_URL: str = "http://ml_service:8001"
    
    # WORK4FOOD Configuration
    BATCH_WINDOW_MINUTES: int = 3
    AGENT_SPEED_KMPH: float = 25.0
    PAY_PER_HOUR: float = 100.0
    MIN_WAGE: float = 80.0
    INITIAL_GUARANTEE_RATIO: float = 0.25
    USE_DYNAMIC_GUARANTEE: bool = True
    PREP_TIME_MINUTES: float = 8.0
    CITY_CENTER_LAT: float = 19.0760  # Mumbai
    CITY_CENTER_LON: float = 72.8777
    CITY_RADIUS_KM: float = 12.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
