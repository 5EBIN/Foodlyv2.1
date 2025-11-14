from __future__ import annotations
from typing import List, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment
from sqlalchemy.orm import Session
from app.services.matching.cost_calculator import CostCalculator
from app.services.matching.guarantee_predictor import GuaranteePredictor
from app.core.config import settings
from app.models.models import Agent, Order


class AssignmentEngine:
    """
    Runs the WORK4FOOD assignment using the Hungarian algorithm.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.guarantee_predictor = GuaranteePredictor(
            initial_omega=getattr(settings, "INITIAL_GUARANTEE_RATIO", 0.25)
        )

    def assign_batch(self, available_agents: List[Agent], pending_orders: List[Order], db: Session | None = None) -> List[Tuple[Agent, Order]]:
        if not available_agents or not pending_orders:
            return []

        # Cost calculator uses DB to resolve any metadata if needed
        # Pass current omega and configuration knobs
        calculator = CostCalculator(
            db=db,
            guarantee_ratio=self.guarantee_predictor.predict(),
            prep_time_minutes=getattr(settings, "PREP_TIME_MINUTES", 8.0),
            speed_kmph=getattr(settings, "AGENT_SPEED_KMPH", 25.0),
        )
        base_costs = calculator.compute_cost_matrix(available_agents, pending_orders)

        # Pad to square matrix with large costs if needed
        n_agents, n_orders = base_costs.shape
        n = max(n_agents, n_orders)
        padded = np.full((n, n), fill_value=1e6, dtype=float)
        padded[:n_agents, :n_orders] = base_costs

        # Hungarian
        rows, cols = linear_sum_assignment(padded)

        assignments: List[Tuple[Agent, Order]] = []
        for r, c in zip(rows, cols):
            if r < n_agents and c < n_orders and padded[r, c] < 1e6:
                assignments.append((available_agents[r], pending_orders[c]))
        return assignments

    def update_predictor(self, agents: List[Agent]) -> None:
        total_work = sum(float(a.work_hours or 0.0) for a in agents)
        total_active = sum(float(a.active_hours or 0.0) for a in agents)
        self.guarantee_predictor.update(total_work, total_active)


