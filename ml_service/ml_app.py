# Simple FastAPI microservice that returns predicted Wv
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Features(BaseModel):
    lat: float
    lng: float
    num_agents: int
    orders_per_window: int
    active_seconds: float

@app.post("/predict_w")
async def predict_w(f: Features):
    # This is a placeholder. Replace with GPR model loaded from disk.
    # A heuristic: predicted_w = orders_per_window / max(1, num_agents) * active_seconds * 0.5
    ratio = f.orders_per_window / max(1, f.num_agents)
    predicted_w = ratio * f.active_seconds * 0.5
    return {"predicted_w": predicted_w}

@app.get("/")
async def root():
    return {"service": "ml_service", "status": "running"}

