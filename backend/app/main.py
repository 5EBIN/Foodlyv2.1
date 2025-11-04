import asyncio
from fastapi import FastAPI
from app.routers import auth, orders, earnings, payments
from app.models.database import engine, Base
from app.core.config import settings

app = FastAPI(title="WORK4FOOD Backend")

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(earnings.router)
app.include_router(payments.router)

@app.on_event("startup")
async def startup():
    # create DB tables (for dev). Use Alembic for production.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"service": "work4food", "ml_service": settings.ML_SERVICE_URL}

