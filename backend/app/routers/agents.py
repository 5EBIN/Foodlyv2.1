from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models import models
from app.schemas import OrderOut
from app.services.matching.simulator import OrderExecutor

router = APIRouter(prefix="/agents", tags=["agents"])


def get_current_agent(db: Session = Depends(get_db)) -> models.Agent:
    # Placeholder: in a real system, derive from JWT
    agent = db.query(models.Agent).first()
    if not agent:
        raise HTTPException(status_code=401, detail="No agent found")
    return agent


@router.get("/me/assigned-orders", response_model=List[OrderOut])
def get_assigned_orders(
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(models.Order)
        .filter(
            models.Order.assigned_agent_id == current_agent.id,
            models.Order.status.in_(["assigned", "picked_up"]),
        )
        .order_by(models.Order.assigned_at.desc().nullslast())
        .all()
    )
    return orders


@router.post("/orders/{order_id}/accept", response_model=dict)
async def accept_order(
    order_id: int,
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    executor = OrderExecutor(db)
    success = await executor.accept_order(order_id, current_agent.id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot accept order")
    return {"message": "Order accepted", "order_id": order_id}


@router.post("/orders/{order_id}/pickup", response_model=dict)
async def pickup_order(
    order_id: int,
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    executor = OrderExecutor(db)
    success = await executor.pickup_order(order_id, current_agent.id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot pickup order")
    return {"message": "Order picked up", "order_id": order_id}


from pydantic import BaseModel


class DeliveryComplete(BaseModel):
    actual_work_hours: float


@router.post("/orders/{order_id}/deliver", response_model=dict)
async def deliver_order(
    order_id: int,
    delivery_data: DeliveryComplete,
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    executor = OrderExecutor(db)
    success = await executor.deliver_order(
        order_id, current_agent.id, delivery_data.actual_work_hours
    )
    if not success:
        raise HTTPException(status_code=400, detail="Cannot deliver order")
    agent = db.query(models.Agent).filter(models.Agent.id == current_agent.id).first()
    return {
        "message": "Order delivered successfully",
        "order_id": order_id,
        "earnings": agent.earnings_total,
        "work_hours": agent.work_hours,
        "active_hours": agent.active_hours,
    }


@router.get("/me/earnings", response_model=dict)
def get_earnings(
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    from app.core.config import settings

    guarantee_ratio = settings.INITIAL_GUARANTEE_RATIO
    guaranteed_hours = guarantee_ratio * float(current_agent.active_hours or 0.0)
    shortfall = max(0.0, guaranteed_hours - float(current_agent.work_hours or 0.0))
    effective_rate = (
        (float(current_agent.total_pay or 0.0) / float(current_agent.active_hours))
        if float(current_agent.active_hours or 0.0) > 0
        else 0.0
    )
    return {
        "agent_id": current_agent.id,
        "work_hours": float(current_agent.work_hours or 0.0),
        "active_hours": float(current_agent.active_hours or 0.0),
        "guaranteed_hours": guaranteed_hours,
        "shortfall_hours": shortfall,
        "earnings": float(current_agent.earnings_total or 0.0),
        "handout": float(current_agent.handout or 0.0),
        "total_pay": float(current_agent.total_pay or 0.0),
        "effective_hourly_rate": effective_rate,
        "guarantee_ratio": guarantee_ratio,
    }


