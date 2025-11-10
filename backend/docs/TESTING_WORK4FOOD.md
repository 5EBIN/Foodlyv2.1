# WORK4FOOD Testing Guide

## Setup

1. Seed data:
```bash
python backend/scripts/seed_work4food_data.py
```

2. Start backend:
```bash
cd backend
uvicorn app.main:app --reload
```

3. Verify scheduler is running:
Look for log: "WORK4FOOD batch scheduler started (3-minute intervals)"

## Test Flow

### Admin API (JWT)
- Login via /api/auth/login with admin_test@foodly.com / admin123 to get access_token
- Use Authorization: Bearer <token> for:
  - POST /api/admin/batch/trigger
  - GET /api/admin/batch/history
  - GET /api/admin/batch/current-stats
  - POST /api/admin/payments/finalize

### Customer → Order → Assignment
1) Place order:
POST /api/orders
Body:
```json
{
  "pickup_lat": 19.08,
  "pickup_lng": 72.89,
  "drop_lat": 19.06,
  "drop_lng": 72.91
}
```
2) Trigger batch or wait 3 minutes
3) As agent_test, check:
GET /api/agents/me/assigned-orders
4) Lifecycle:
POST /api/agents/orders/{id}/accept
POST /api/agents/orders/{id}/pickup
POST /api/agents/orders/{id}/deliver { "actual_work_hours": 0.35 }
5) Earnings:
GET /api/agents/me/earnings

## Success Criteria
- Admin/customer/agent test users exist
- 50 agents, 20 restaurants, 30 customers seeded
- Batch trigger works (manual and automatic)
- Orders assigned with Hungarian algorithm
- Payments finalize and handouts computed


