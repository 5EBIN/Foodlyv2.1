from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import numpy as np
from scipy.optimize import linear_sum_assignment

from app.models import models
from app.schemas import OrderCreate, OrderOut
from app.models.database import get_db
from app.services.g_value_client import predict_wv

router = APIRouter(prefix="/orders", tags=["orders"])

# utility: simple travel-time placeholder (Haversine or precomputed)
def travel_time_seconds(pick_lat, pick_lng, drop_lat, drop_lng):
    # placeholder -> use actual travel-time / distance APIs or routing
    dx = pick_lat - drop_lat
    dy = pick_lng - drop_lng
    return (abs(dx) + abs(dy)) * 1000  # synthetic

@router.post("/", response_model=OrderOut)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    order = models.Order(
        pickup_lat=order_in.pickup_lat,
        pickup_lng=order_in.pickup_lng,
        drop_lat=order_in.drop_lat,
        drop_lng=order_in.drop_lng
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

@router.get("/batch_and_match")
async def batch_and_match(db: AsyncSession = Depends(get_db)):
    """
    1) collect pending unassigned orders in current window
    2) create batches (for simplicity: one order per batch OR simple grouping)
    3) compute edge weights e(v,b) per eq (3) + foodmatch term (efm)
    4) run Hungarian to assign batches to agents
    """
    # 1) fetch unassigned orders
    res = await db.execute(models.Order.__table__.select().where(models.Order.status == "pending"))
    orders = [r for r in res.fetchall()]
    if not orders:
        return {"message": "no pending orders"}

    # 2) fetch active agents
    res = await db.execute(models.Agent.__table__.select().where(models.Agent.active == True))
    agents = [r for r in res.fetchall()]
    if not agents:
        return {"message": "no active agents"}

    # For simplicity, each order is its own batch
    batches = orders
    n_agents = len(agents)
    n_batches = len(batches)
    # cost matrix size max(n_agents, n_batches) by filling with large cost for padding
    N = max(n_agents, n_batches)
    cost = np.zeros((N, N), dtype=float) + 1e6

    # populate cost for real agent-batch entries
    for i, agent_row in enumerate(agents):
        agent = agent_row[0] if isinstance(agent_row, tuple) else agent_row
        # predict agent Wv using ML (GPR) to compute ωv = Wv / Av
        agent_features = {
            "lat": agent.last_location.get("lat") if agent.last_location else 0.0,
            "lng": agent.last_location.get("lng") if agent.last_location else 0.0,
            "num_agents": n_agents,
            "orders_per_window": n_batches,
            "active_seconds": agent.active_seconds or 3600
        }
        try:
            predicted_w = await predict_wv(agent_features)
        except Exception:
            predicted_w = agent.current_work_seconds or 0.0

        # computed gv = ωv = predicted_w / Av (Av can't be zero)
        if (agent.active_seconds or 1.0) > 0:
            gv = predicted_w / (agent.active_seconds or 1.0)
        else:
            gv = 0.0

        Wt_v = agent.current_work_seconds or 0.0
        Gt_v = gv * (agent.active_seconds or 1.0)

        for j, order_row in enumerate(batches):
            order = order_row[0] if isinstance(order_row, tuple) else order_row
            # compute wb_v = extra work required to deliver batch b by agent v
            wb_v = travel_time_seconds(agent.last_location.get("lat") if agent.last_location else order.pickup_lat,
                                       agent.last_location.get("lng") if agent.last_location else order.pickup_lng,
                                       order.drop_lat, order.drop_lng)
            # eq (3):
            if Gt_v > Wt_v:
                edge_extra = max(Wt_v + wb_v - Gt_v, 0)
            else:
                edge_extra = wb_v * Gt_v  # matches the paper formula for Gt_v <= Wt_v
            # add FOODMATCH term efm (approximated by sum of travel_time for orders in b)
            efm = wb_v  # simplified
            # final edge weight: combine (paper adds them)
            weight = edge_extra + efm
            cost[i, j] = weight

    row_ind, col_ind = linear_sum_assignment(cost)
    assignments = []
    for r, c in zip(row_ind, col_ind):
        if r < n_agents and c < n_batches and cost[r, c] < 1e5:
            # assign orders[c] to agents[r]
            order_row = batches[c]
            agent_row = agents[r]
            order = order_row[0] if isinstance(order_row, tuple) else order_row
            agent = agent_row[0] if isinstance(agent_row, tuple) else agent_row
            order.assigned_agent_id = agent.id
            order.status = "assigned"
            db.add(order)
            assignments.append({"order_id": order.id, "agent_id": agent.id, "cost": float(cost[r,c])})
    await db.commit()
    return {"assignments": assignments}
