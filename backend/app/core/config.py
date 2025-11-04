from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/work4food"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "super-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ML_SERVICE_URL: str = "http://ml_service:8001"
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

