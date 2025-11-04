from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import models
from app.models.database import get_db
from app.schemas import EarningsOut

router = APIRouter(prefix="/earnings", tags=["earnings"])

@router.get("/agent/{agent_id}", response_model=list[EarningsOut])
async def get_agent_earnings(agent_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(models.Earning.__table__.select().where(models.Earning.agent_id == agent_id))
    rows = res.fetchall()
    return [r[0] for r in rows]
