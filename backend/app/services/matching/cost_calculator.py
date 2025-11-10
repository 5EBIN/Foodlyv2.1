from __future__ import annotations
from typing import List
import numpy as np
from app.services.matching.geo_utils import travel_time_minutes
from app.core.config import settings
from app.models.models import Agent, Order, Restaurant
from sqlalchemy.orm import Session


class CostCalculator:
    """
    Computes guarantee-aware cost matrix per WORK4FOOD Equation 3.
    cost_ij =
        w_b(i,j)                           if G_t^i <= W_t^i
        max(W_t^i + w_b(i,j) - G_t^i, 0)   if G_t^i > W_t^i
    where:
      w_b(i,j) is estimated work hours for agent i to complete order j
      W_t^i is agent i's work_hours
      G_t^i is omega * agent i's active_hours
    """

    def __init__(self, db: Session, guarantee_ratio: float, prep_time_minutes: float, speed_kmph: float):
        self.db = db
        self.guarantee_ratio = guarantee_ratio
        self.prep_time_minutes = prep_time_minutes
        self.speed_kmph = speed_kmph

    def _estimate_work_hours(self, agent: Agent, order: Order) -> float:
        # Resolve restaurant and customer coords
        restaurant: Restaurant = self.db.query(Restaurant).filter(Restaurant.id == order.user_id).first()  # fallback
        # Order model here uses generic pickup/drop; use those directly for estimation
        agent_loc = (agent.last_location_lat or 0.0, agent.last_location_lon or 0.0)
        pickup_loc = (order.pickup_lat, order.pickup_lng)
        drop_loc = (order.drop_lat, order.drop_lng)

        to_pickup = travel_time_minutes(agent_loc, pickup_loc, self.speed_kmph)
        to_drop = travel_time_minutes(pickup_loc, drop_loc, self.speed_kmph)
        total_minutes = to_pickup + self.prep_time_minutes + to_drop
        return total_minutes / 60.0

    def compute_cost_matrix(self, agents: List[Agent], orders: List[Order]) -> np.ndarray:
        if not agents or not orders:
            return np.zeros((len(agents), len(orders)))
        costs = np.zeros((len(agents), len(orders)), dtype=float)
        for i, agent in enumerate(agents):
            W = float(agent.work_hours or 0.0)
            A = float(agent.active_hours or 0.0)
            G = float(self.guarantee_ratio) * A
            for j, order in enumerate(orders):
                w_b = self._estimate_work_hours(agent, order)
                if G <= W:
                    cost = w_b
                else:
                    cost = max(W + w_b - G, 0.0)
                costs[i, j] = cost
        return costs


