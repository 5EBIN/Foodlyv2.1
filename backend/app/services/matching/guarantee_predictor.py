from __future__ import annotations
from typing import List, Tuple


class GuaranteePredictor:
    """
    Simple moving-average predictor for guarantee ratio (omega).
    Tracks (total_work, total_active) pairs and updates omega as:
        omega = clamp( average(total_work / max(total_active, eps)) )
    with smoothing toward the configured initial value.
    """

    def __init__(self, initial_omega: float = 0.25, max_history: int = 50, smoothing: float = 0.2):
        self.omega: float = initial_omega
        self.history: List[Tuple[float, float]] = []
        self.max_history = max_history
        self.smoothing = smoothing

    def update(self, total_work: float, total_active: float) -> None:
        self.history.append((total_work, total_active))
        if len(self.history) > self.max_history:
            self.history.pop(0)
        avg_ratio = self._average_ratio()
        # Smoothly move current omega toward observed ratio
        self.omega = (1 - self.smoothing) * self.omega + self.smoothing * avg_ratio
        # Clamp to reasonable range
        self.omega = max(0.05, min(self.omega, 0.9))

    def predict(self) -> float:
        return self.omega

    def _average_ratio(self) -> float:
        if not self.history:
            return self.omega
        ratios: List[float] = []
        for work, active in self.history:
            if active <= 0:
                continue
            ratios.append(work / active)
        if not ratios:
            return self.omega
        return sum(ratios) / len(ratios)


