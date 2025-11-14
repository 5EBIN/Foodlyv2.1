# 🚀 WORK4FOOD Project - Implementation Roadmap

## Project Goal
Food delivery platform with **ML-powered fair agent assignment** using Gaussian Process models.

## ✅ What's Already Working
- Backend: FastAPI with SQLite
- Auth: Username/password for customers & agents
- Worker App: Basic delivery worker interface
- Database: Users, Agents, Orders, Earnings, Payments, Notifications
- ML Service: Gaussian Process model ready

---

## 🎯 Implementation Phases (Optimized for MVP)

### **PHASE 1: Database & Backend Foundation** ✅ IN PROGRESS
**Files Modified:**
- ✅ `backend/app/models/models.py` - Added Restaurant & CustomerOrder models
- ⏳ `backend/app/schemas.py` - Add Pydantic schemas
- ⏳ `backend/seed_database.py` - Add restaurant dummy data

**New Models:**
```python
- Restaurant (name, cuisine, location, hours, rating)
- CustomerOrder (links customer → restaurant → agent)
```

---

### **PHASE 2: Backend APIs** ⏳ NEXT
**New Routers to Create:**

#### `backend/app/routers/restaurants.py`
```python
GET  /api/restaurants              # List all (with distance from user)
GET  /api/restaurants/{id}         # Get single restaurant
POST /api/restaurants              # Admin create (optional)
```

#### `backend/app/routers/customer_orders.py`
```python
POST /api/customer/orders          # Create order → Triggers ML assignment
GET  /api/customer/orders/active   # Get customer's current order
GET  /api/customer/orders/history  # Past orders
GET  /api/customer/orders/{id}     # Single order details
```

#### `backend/app/services/ml_matcher.py` (NEW - KEY FEATURE!)
```python
assign_agent_to_order(order_id) → agent_id
  - Calls ML service with order details
  - Gets G-values for available agents
  - Selects best agent
  - Updates order with assignment
```

---

### **PHASE 3: Customer Mobile App** ⏳ PRIORITY
**New Screens:**

1. **RestaurantListScreen.tsx**
   - Grid of restaurant cards
   - Show: name, cuisine, distance, delivery time, rating
   - Filter by distance/cuisine
   - Click → RestaurantDetailScreen

2. **RestaurantDetailScreen.tsx**
   - Restaurant info
   - Large "Order Now" button (fixed amount: $25)
   - Estimated delivery time
   - Click → OrderConfirmationScreen

3. **OrderConfirmationScreen.tsx**
   - Shows: Restaurant name, amount, delivery address
   - "Proceed to Payment" button
   - Click → MockPaymentScreen

4. **MockPaymentScreen.tsx**
   - Simple mock payment UI
   - "Pay & Confirm Order" button
   - On click → Create order API call → ActiveOrderScreen

5. **ActiveOrderScreen.tsx**
   - Show current order status
   - Restaurant name + delivery address
   - Status updates (pending → assigned → picked_up → delivered)
   - Mock progress bar

**Navigation Update:**
```tsx
Bottom Tabs:
  - Home (Restaurants List)
  - Orders (Active Order / History)
  - Profile (User info)
```

---

### **PHASE 4: ML Integration** ⏳ KEY DIFFERENTIATOR
**Workflow:**
```
Customer places order
  ↓
Backend creates CustomerOrder (status=pending)
  ↓
Trigger ML assignment service
  ↓
ML service:
  1. Get order location (restaurant + delivery address)
  2. Get all available agents (online, not busy)
  3. For each agent:
     - Calculate distance to restaurant
     - Get agent's performance metrics
     - Call GP model for G-value
  4. Select agent with best G-value
  ↓
Update order: assigned_agent_id, status=assigned, assignment_score
  ↓
Notify agent (push notification)
  ↓
Agent sees order in their app
```

**ML Service Integration:**
```python
# backend/app/services/ml_matcher.py
async def assign_best_agent(order: CustomerOrder):
    # Get available agents
    agents = get_online_agents()

    # Calculate scores for each
    scores = []
    for agent in agents:
        g_value = await call_ml_service(
            order_location=order.restaurant.location,
            delivery_location=(order.delivery_lat, order.delivery_lng),
            agent_location=agent.last_location,
            agent_history=agent.performance_metrics
        )
        scores.append((agent.id, g_value))

    # Select best
    best_agent = max(scores, key=lambda x: x[1])
    return best_agent
```

---

### **PHASE 5: Worker App Updates** ⏳
**Changes:**
- Show CustomerOrder in "Available Orders" tab
- Display: Restaurant name, delivery address, estimated earnings
- Accept button → Update status to picked_up
- Complete button → Update status to delivered

---

## 📁 Complete File Structure
```
cnprjv2/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── models.py         ✅ Updated
│   │   │   └── database.py
│   │   ├── routers/
│   │   │   ├── auth.py           ✅ Existing
│   │   │   ├── restaurants.py    🆕 NEW
│   │   │   └── customer_orders.py 🆕 NEW
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   └── ml_matcher.py     🆕 NEW - ML INTEGRATION
│   │   ├── schemas.py            ⏳ Update needed
│   │   └── main.py
│   ├── seed_database.py          ⏳ Update needed
│   └── requirements.txt
├── frontend/ (Customer App)
│   ├── src/
│   │   ├── screens/
│   │   │   ├── LandingScreen.tsx         ✅ Done
│   │   │   ├── LoginScreen.tsx           ✅ Done
│   │   │   ├── RestaurantListScreen.tsx  🆕 NEW
│   │   │   ├── RestaurantDetailScreen.tsx 🆕 NEW
│   │   │   ├── OrderConfirmationScreen.tsx 🆕 NEW
│   │   │   ├── MockPaymentScreen.tsx     🆕 NEW
│   │   │   └── ActiveOrderScreen.tsx     🆕 NEW
│   │   ├── services/
│   │   │   └── api.ts            ⏳ Add restaurant & order APIs
│   │   └── navigation/
│   │       └── AppNavigator.tsx  ⏳ Update navigation
│   └── package.json
├── ml_service/ (Existing ML service)
│   └── Add endpoint for agent assignment
└── docker-compose.yml            ⏳ Update

```

---

## 🔥 NEXT STEPS (In Order)
1. ✅ Complete database models
2. ⏳ **Add Pydantic schemas** (schemas.py)
3. ⏳ **Seed restaurant data** (10-15 dummy restaurants)
4. ⏳ **Create restaurant API router**
5. ⏳ **Create customer orders API router**
6. ⏳ **Integrate ML matching service**
7. ⏳ **Build customer app screens** (5 screens)
8. ⏳ **Update worker app** to show customer orders
9. ⏳ **Test end-to-end flow**

---

## 🎨 UI Design References
- **Customer App**: Zomato-like (clean, card-based, minimal clicks)
- **Color Scheme**:
  - Primary: #E23744 (Red - food apps)
  - Secondary: #1F2937 (Dark gray)
  - Accent: #10B981 (Green for success states)

---

## ⚡ Quick Demo Flow (What User Experiences)
```
1. Open app → Landing (Customer/Agent choice)
2. Click "Customer" → Login (customer1/password123)
3. See restaurant list (15 restaurants with distances)
4. Click restaurant → See details + "Order Now"
5. Click "Order Now" → Confirm order ($25)
6. Click "Proceed to Payment" → Mock payment
7. Click "Pay" → Order created
   [ML service assigns best agent in background]
8. See "Order Placed!" → Redirected to active order
9. Track order status: Pending → Assigned → Picked Up → Delivered
```

---

## 🚀 Estimated Timeline
- Phase 1-2 (Backend): 2-3 hours
- Phase 3 (Customer App): 3-4 hours
- Phase 4 (ML Integration): 2 hours
- Phase 5 (Worker Updates): 1 hour
- Testing & Polish: 1-2 hours

**Total: ~10-12 hours for full MVP**

---

## 💡 Key Innovation: ML-Based Fair Assignment
Unlike Uber/DoorDash (first-come-first-served or simple distance-based),
your system uses **Gaussian Process** to:
- Balance workload across agents
- Consider agent performance history
- Optimize for fairness (work4food concept)
- Reduce agent idle time
- Improve overall system efficiency

This is your **competitive advantage**!
