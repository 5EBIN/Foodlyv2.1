from fastapi import APIRouter, Request, HTTPException, status
import stripe
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["payments"])
stripe.api_key = settings.STRIPE_API_KEY

@router.post("/create-payment-intent")
async def create_payment_intent(payload: dict):
    # payload expected: {"amount": 1000, "currency": "inr", "metadata": {...}}
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payload["amount"]),
            currency=payload.get("currency", "inr"),
            metadata=payload.get("metadata", {})
        )
        return {"client_secret": intent.client_secret, "id": intent.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Event.construct_from(request.json(), stripe.api_key)
    except Exception:
        # Fallback simple parse in dev
        event = await request.json()
    # handle events
    # e.g., payment_intent.succeeded, payout.paid, etc.
    return {"received": True}
