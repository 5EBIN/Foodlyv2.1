from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.database import get_db
from app.services.matching.simulator import BatchProcessor, PaymentProcessor
from app.models.models import BatchAssignment, Agent, Order
from app.core.config import settings
from app.core.security import require_admin
from app.models.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/batch/trigger")
async def trigger_batch_manually(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Manually trigger batch assignment (for testing)"""
    processor = BatchProcessor(db)
    result = await processor.process_batch()
    return result


@router.get("/batch/history")
def get_batch_history(limit: int = 20, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """View past batch assignments"""
    batches = (
        db.query(BatchAssignment)
        .order_by(BatchAssignment.window_start.desc())
        .limit(limit)
        .all()
    )
    return batches


@router.get("/batch/current-stats")
def get_current_batch_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Get stats for current batch window"""
    window_start = datetime.utcnow() - timedelta(minutes=settings.BATCH_WINDOW_MINUTES)
    pending_orders = (
        db.query(Order)
        .filter(Order.status == "pending", Order.batch_window_start >= window_start)
        .count()
    )
    available_agents = db.query(Agent).filter(Agent.status == "available").count()
    return {
        "pending_orders": pending_orders,
        "available_agents": available_agents,
        "window_start": window_start,
    }


from typing import Optional

@router.post("/payments/finalize")
async def finalize_payments(guarantee_ratio: Optional[float] = None, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Calculate handouts and finalize payments (end of day)"""
    processor = PaymentProcessor(db)
    ratio = guarantee_ratio or settings.INITIAL_GUARANTEE_RATIO
    result = await processor.finalize_payments(ratio)
    return result


