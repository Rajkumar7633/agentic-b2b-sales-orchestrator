import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.init_agents import initialize_agents
from app.api.v1 import (
    accounts,
    agents,
    analytics,
    approvals,
    audit,
    auth,
    contacts,
    eval,
    excel,
    health,
    knowledge,
    leads,
    meetings,
    outreach,
)
from app.core.config import settings
from app.core.rate_limit import rate_limit_middleware
from app.seeds.seed import seed_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexora_pursuit_engine")


async def run_auto_migrations(conn):
    from sqlalchemy import text
    cols_to_add = [
        ("companies", "sector", "VARCHAR(128)"),
        ("companies", "priority", "VARCHAR(64)"),
        ("companies", "hq_focus", "VARCHAR(255)"),
        ("companies", "active_upcoming_work", "TEXT"),
        ("companies", "lead_service", "VARCHAR(255)"),
        ("companies", "named_contacts_str", "TEXT"),
        ("companies", "relationship_stage", "VARCHAR(128)"),
        ("companies", "timing", "VARCHAR(128)"),
        ("companies", "recommended_next_action", "TEXT"),
        ("companies", "company_source", "VARCHAR(255)"),
        ("companies", "project_source", "VARCHAR(255)"),
        ("companies", "notes", "TEXT"),
        ("companies", "coverage_pct", "FLOAT"),
        ("contacts", "why_this_person", "TEXT"),
        ("contacts", "public_profile", "VARCHAR(512)"),
        ("contacts", "public_email", "VARCHAR(255)"),
        ("contacts", "priority", "VARCHAR(64)"),
        ("contacts", "suggested_channel", "VARCHAR(64)"),
        ("contacts", "opening_context", "TEXT"),
        ("contacts", "linkedin_intro", "TEXT"),
        ("contacts", "linkedin_sent", "VARCHAR(64)"),
        ("contacts", "date_sent", "VARCHAR(64)"),
        ("contacts", "accepted", "VARCHAR(64)"),
        ("contacts", "followup_due", "VARCHAR(64)"),
        ("contacts", "relationship_stage", "VARCHAR(128)"),
        ("contacts", "next_best_action", "TEXT"),
        ("contacts", "notes", "TEXT"),
        ("contacts", "linkedin_status", "VARCHAR(64) DEFAULT 'NOT_STARTED'"),
        ("leads", "linkedin_status", "VARCHAR(64) DEFAULT 'NOT_STARTED'"),
        ("leads", "meeting_status", "VARCHAR(64) DEFAULT 'NOT_SCHEDULED'"),
        ("leads", "meeting_link", "VARCHAR(512)"),
        ("leads", "meeting_date", "VARCHAR(128)"),
        ("leads", "transcript_text", "TEXT"),
        ("leads", "transcript_analysis", "JSON"),
        ("company_projects", "location", "VARCHAR(255)"),
        ("company_projects", "stage", "VARCHAR(128)"),
        ("company_projects", "sector", "VARCHAR(128)"),
        ("company_projects", "scale_context", "TEXT"),
        ("company_projects", "expected_completion", "VARCHAR(128)"),
        ("company_projects", "lead_quality", "VARCHAR(64)"),
        ("company_projects", "source", "VARCHAR(255)"),
        ("meetings", "meeting_date", "VARCHAR(128)"),
        ("meetings", "transcript_text", "TEXT"),
        ("meetings", "transcript_analysis", "JSON"),
    ]
    for table, col_name, col_type in cols_to_add:
        try:
            await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type};"))
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NEXORA Pursuit Engine backend services...")
    initialize_agents()
    try:
        from app.core.database import Base, engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await run_auto_migrations(conn)
        await seed_database()
        from app.agents.registry import agent_registry
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await agent_registry.sync_to_db(session)
    except Exception as exc:
        logger.warning(f"Seed initialization note: {exc!s}")
    yield
    logger.info("Shutting down NEXORA Pursuit Engine backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Agentic AI Sales Pursuit Platform with Human-In-The-Loop Approval Control",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.middleware("http")(rate_limit_middleware)

@app.middleware("http")
async def add_security_and_request_id_headers(request, call_next):
    import time
    import uuid
    request_id = request.headers.get("X-Request-ID", f"req_{uuid.uuid4().hex[:12]}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Include API v1 Routers
app.include_router(health.router)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(accounts.router, prefix=settings.API_V1_STR)
app.include_router(contacts.router, prefix=settings.API_V1_STR)
app.include_router(leads.router, prefix=settings.API_V1_STR)
app.include_router(outreach.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)
app.include_router(meetings.router, prefix=settings.API_V1_STR)
app.include_router(excel.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(eval.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(knowledge.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
