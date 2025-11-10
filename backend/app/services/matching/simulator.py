"""
Main simulator for WORK4FOOD batch processing
Handles order batching, assignment, and execution
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models import Order, Agent, Restaurant, BatchAssignment
from app.services.matching.assignment_engine import AssignmentEngine
from app.services.matching.geo_utils import travel_time_minutes
from app.core.config import settings

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processes batches of orders and assigns to agents"""

    def __init__(self, db: Session):
        self.db = db
        self.assignment_engine = AssignmentEngine(
            {
                "agents": {"speed_kmph": settings.AGENT_SPEED_KMPH},
                "orders": {"prep_time_minutes": settings.PREP_TIME_MINUTES},
                "economics": {
                    "guarantee_ratio": settings.INITIAL_GUARANTEE_RATIO,
                    "use_dynamic_guarantee": settings.USE_DYNAMIC_GUARANTEE,
                },
            }
        )

    async def process_batch(self) -> Dict:
        """
        Main batch processing function - runs every BATCH_WINDOW_MINUTES
        """
        batch_start = datetime.utcnow()
        window_start = batch_start - timedelta(minutes=settings.BATCH_WINDOW_MINUTES)
        logger.info(f"Starting batch processing at {batch_start}")

        pending_orders = await self._get_pending_orders(window_start, batch_start)
        if not pending_orders:
            logger.info("No pending orders in this batch window")
            return {
                "batch_id": f"batch_{batch_start.strftime('%Y%m%d_%H%M%S')}",
                "total_orders": 0,
                "assigned_orders": 0,
                "available_agents": 0,
            }

        logger.info(f"Found {len(pending_orders)} pending orders")
        available_agents = await self._get_available_agents()
        if not available_agents:
            logger.warning("No available agents for batch assignment!")
            return {
                "batch_id": f"batch_{batch_start.strftime('%Y%m%d_%H%M%S')}",
                "total_orders": len(pending_orders),
                "assigned_orders": 0,
                "available_agents": 0,
            }
        logger.info(f"Found {len(available_agents)} available agents")

        # Run assignment algorithm
        assignments = self.assignment_engine.assign_batch(
            available_agents=available_agents, pending_orders=pending_orders, db=self.db
        )
        logger.info(f"Assignment algorithm returned {len(assignments)} assignments")

        # Execute assignments
        batch_id = f"batch_{batch_start.strftime('%Y%m%d_%H%M%S')}"
        assigned_count = await self._execute_assignments(assignments=assignments, batch_id=batch_id, batch_start=batch_start)

        # Update active hours for all agents (they were available during the window)
        await self._update_agent_active_hours(agents=available_agents, hours=settings.BATCH_WINDOW_MINUTES / 60.0)

        # Update guarantee predictor
        self.assignment_engine.update_predictor(available_agents)

        # Save batch record
        await self._save_batch_record(
            batch_id=batch_id,
            window_start=window_start,
            window_end=batch_start,
            total_orders=len(pending_orders),
            assigned_orders=assigned_count,
            guarantee_ratio=self.assignment_engine.guarantee_predictor.predict(),
        )

        logger.info(f"Batch processing complete: {assigned_count}/{len(pending_orders)} orders assigned")

        return {
            "batch_id": batch_id,
            "total_orders": len(pending_orders),
            "assigned_orders": assigned_count,
            "available_agents": len(available_agents),
            "guarantee_ratio": self.assignment_engine.guarantee_predictor.predict(),
        }

    async def _get_pending_orders(self, window_start: datetime, window_end: datetime) -> List[Order]:
        """Get orders that are pending assignment in the time window"""
        # Using generic 'pending' state as placeholder for PENDING_BATCH
        orders = (
            self.db.query(Order)
            .filter(
                and_(
                    Order.status == "pending",
                    # Use created_at as proxy for batch_window_start if not present in current schema flow
                    Order.created_at >= window_start,
                    Order.created_at < window_end,
                )
            )
            .all()
        )
        return orders

    async def _get_available_agents(self) -> List[Agent]:
        """Get agents that are currently available for assignment"""
        # Use status enum string value in DB
        agents = self.db.query(Agent).filter(Agent.status == "available").all()
        return agents

    async def _execute_assignments(self, assignments: List, batch_id: str, batch_start: datetime) -> int:
        """Execute the assignments by updating database records"""
        assigned_count = 0
        for agent, order in assignments:
            try:
                order.assigned_agent_id = agent.id
                order.status = "assigned"
                order.assigned_at = batch_start
                order.batch_id = batch_id
                # Estimated work hours and assignment cost
                order.estimated_work_hours = self._calculate_work_hours(agent, order)
                order.assignment_cost = order.estimated_work_hours
                # Agent status
                agent.status = "en_route"
                assigned_count += 1
                logger.debug(f"Assigned order {order.id} to agent {agent.id}")
            except Exception as e:
                logger.error(f"Failed to execute assignment: {e}")
                continue
        self.db.commit()
        return assigned_count

    def _calculate_work_hours(self, agent: Agent, order: Order) -> float:
        """
        Calculate estimated work hours for an assignment
        work_hours = (travel_to_pickup + prep_time + travel_to_drop) / 60
        """
        agent_location = (float(agent.last_location_lat or 0.0), float(agent.last_location_lon or 0.0))
        pickup_location = (float(order.pickup_lat), float(order.pickup_lng))
        drop_location = (float(order.drop_lat), float(order.drop_lng))
        to_pickup = travel_time_minutes(agent_location, pickup_location, speed_kmph=settings.AGENT_SPEED_KMPH)
        prep_time = float(settings.PREP_TIME_MINUTES)
        to_drop = travel_time_minutes(pickup_location, drop_location, speed_kmph=settings.AGENT_SPEED_KMPH)
        return (to_pickup + prep_time + to_drop) / 60.0

    async def _update_agent_active_hours(self, agents: List[Agent], hours: float):
        """Update active hours for all agents (they were available during window)"""
        for agent in agents:
            agent.active_hours = float(agent.active_hours or 0.0) + float(hours or 0.0)
        self.db.commit()

    async def _save_batch_record(
        self,
        batch_id: str,
        window_start: datetime,
        window_end: datetime,
        total_orders: int,
        assigned_orders: int,
        guarantee_ratio: float,
    ):
        """Save batch processing record for analytics"""
        batch_record = BatchAssignment(
            id=batch_id,  # store batch_id also as PK for simplicity
            batch_id=batch_id,
            window_start=window_start,
            window_end=window_end,
            total_orders=total_orders,
            assigned_orders=assigned_orders,
            guarantee_ratio=guarantee_ratio,
            created_at=datetime.utcnow(),
        )
        self.db.add(batch_record)
        self.db.commit()


class OrderExecutor:
    """Handles order lifecycle after assignment"""

    def __init__(self, db: Session):
        self.db = db

    async def accept_order(self, order_id: int, agent_id: int) -> bool:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order or order.assigned_agent_id != agent_id or order.status != "assigned":
            return False
        return True

    async def pickup_order(self, order_id: int, agent_id: int) -> bool:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not order or order.assigned_agent_id != agent_id:
            return False
        order.status = "picked_up"
        order.picked_up_at = datetime.utcnow()
        # Optionally update agent location to pickup (not available in this generic schema)
        agent.status = "delivering"
        self.db.commit()
        return True

    async def deliver_order(self, order_id: int, agent_id: int, actual_work_hours: float) -> bool:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not order or order.assigned_agent_id != agent_id:
            return False
        order.status = "delivered"
        order.delivered_at = datetime.utcnow()
        order.actual_work_hours = actual_work_hours
        agent.work_hours = float(agent.work_hours or 0.0) + float(actual_work_hours or 0.0)
        # Update earnings_total
        agent.earnings_total = float(agent.earnings_total or 0.0) + float(settings.PAY_PER_HOUR) * float(actual_work_hours or 0.0)
        agent.status = "available"
        self.db.commit()
        return True


class PaymentProcessor:
    """Handles end-of-day payment calculations"""

    def __init__(self, db: Session):
        self.db = db

    async def finalize_payments(self, guarantee_ratio: float) -> Dict:
        agents = self.db.query(Agent).filter((Agent.active_hours.isnot(None)) & (Agent.active_hours > 0)).all()
        total_earnings = 0.0
        total_handouts = 0.0
        violations = 0
        for agent in agents:
            active = float(agent.active_hours or 0.0)
            work = float(agent.work_hours or 0.0)
            guaranteed_hours = guarantee_ratio * active
            shortfall = max(0.0, guaranteed_hours - work)
            handout = float(settings.PAY_PER_HOUR) * shortfall
            agent.handout = handout
            agent.total_pay = float(agent.earnings_total or 0.0) + handout
            total_earnings += float(agent.earnings_total or 0.0)
            total_handouts += handout
            effective_wage = agent.total_pay / active if active > 0 else 0.0
            if effective_wage < float(settings.MIN_WAGE):
                violations += 1
        self.db.commit()
        return {
            "total_agents": len(agents),
            "total_earnings": total_earnings,
            "total_handouts": total_handouts,
            "platform_cost": total_earnings + total_handouts,
            "min_wage_violations": violations,
            "guarantee_ratio": guarantee_ratio,
        }


