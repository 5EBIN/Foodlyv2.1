# Worker App Project

A full-stack worker application with backend, g-value service, and React Native frontend.

## Project Structure

```
worker-app-project/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── orders.py
│   │   │   └── earnings.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── services/
│   │       ├── auth_service.py
│   │       ├── redis_client.py
│   │       ├── g_value_client.py
│   │       └── gp_model.py
│   ├── main.py
│   └── requirements.txt
├── g-value-service/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   │       ├── gp_model.py
│   │       └── redis_client.py
│   └── requirements.txt
├── frontend/
│   └── worker-app/
│       ├── App.tsx
│       ├── src/
│       │   ├── navigation/
│       │   │   └── AppNavigator.tsx
│       │   ├── screens/
│       │   │   ├── LoginScreen.tsx
│       │   │   ├── OrdersScreen.tsx
│       │   │   ├── CurrentJobScreen.tsx
│       │   │   └── EarningsScreen.tsx
│       │   ├── services/
│       │   │   └── api.ts
│       │   └── types/
│       │       └── index.ts
│       ├── app.json
│       ├── package.json
│       └── tsconfig.json
├── docker-compose.yml
└── README.md
```

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### G-Value Service

```bash
cd g-value-service
pip install -r requirements.txt
python -m app.main
```

### Frontend

```bash
cd frontend/worker-app
npm install
npm start
```

### Docker

```bash
docker-compose up
```

## Services

- **Backend**: Main API server (port 8000)
- **G-Value Service**: GP model service (port 8001)
- **Redis**: Caching service (port 6379)
- **Frontend**: Expo React Native app

## Development

See individual service READMEs for more details.


