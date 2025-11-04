import httpx
from app.core.config import settings

# client that asks ML service (GPR) to predict expected work Wv given features
async def predict_wv(agent_features: dict) -> float:
    """
    agent_features: {
      "login_time": "...",
      "lat": 12.34,
      "lng": 56.78,
      "num_agents": 100,
      "orders_per_window": 50,
      "active_seconds": 3600
    }
    returns predicted Wv (seconds of expected work) as float
    """
    url = f"{settings.ML_SERVICE_URL}/predict_w"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=agent_features)
        resp.raise_for_status()
        data = resp.json()
    return float(data["predicted_w"])
