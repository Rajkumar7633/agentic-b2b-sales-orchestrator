# Production Deployment Guide (`docs/DEPLOYMENT.md`)

## 1. Local Development Deployment

```bash
# Start Backend
cd backend
PYTHONPATH=. GROK_API_KEY=gsk_... LLM_PROVIDER=grok .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start Frontend
cd frontend
npm run dev -- --port 3000
```

## 2. Docker Compose Containerization

```bash
# Build and start all services
docker-compose up --build -d

# Services exposed:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - Redis: localhost:6379
# - PostgreSQL: localhost:5432
```

## 3. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `grok` | Options: `grok`, `groq`, `openai`, `mock` |
| `GROK_API_KEY` | `gsk_...` | Groq / xAI API key |
| `DATABASE_URL` | `sqlite+aiosqlite:///./nexora_pursuit.db` | PostgreSQL URL for production |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis instance for event bus / cache |
| `JWT_SECRET` | `nexora_super_secret_jwt_key...` | JWT signature secret |
| `DEFAULT_TENANT_ID`| `tenant_nexora_default` | Primary tenant identifier |
