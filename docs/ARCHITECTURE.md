# NEXORA System Architecture (`docs/ARCHITECTURE.md`)

## System Overview

The **NEXORA Pursuit Engine** is an enterprise sales pursuit platform powered by 10 agentic AI micro-services, human-in-the-loop (HITL) approval controls, RAG knowledge retrieval, and an asynchronous event bus.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Next.js 14 Web Frontend                          │
│     Dashboard | Pipeline | Approvals | Accounts | Contacts | Analytics      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST API
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            FastAPI Backend Server                           │
│  ┌───────────────────────┐ ┌──────────────────────┐ ┌────────────────────┐  │
│  │   Security / RBAC     │ │   HITL Engine        │ │   Excel Engine     │  │
│  └───────────────────────┘ └──────────────────────┘ └────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Agent Registry (10 Agents)                       │  │
│  │  Supervisor | Planner | Research | Discovery | Scoring | Outreach ...   │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │                      In-Memory Event Bus (Pub/Sub)                    │  │
│  │         Idempotency | Retries | Dead Letter Queue (DLQ)               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                              Persistence & Services                         │
│  ┌───────────────────────┐ ┌──────────────────────┐ ┌────────────────────┐  │
│  │  PostgreSQL Database  │ │  Groq / Grok LLM     │ │  RAG Vector Engine │  │
│  └───────────────────────┘ └──────────────────────┘ └────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure Overview

- `backend/app/agents/`: 10 specialized agent subpackages (`supervisor`, `planner`, `company_research`, `lead_discovery`, `lead_scoring`, `outreach`, `followup`, `meeting_scheduler`, `crm`, `analytics`).
- `backend/app/api/v1/`: FastAPI routers exposing endpoints for accounts, approvals, contacts, leads, outreach, meetings, excel, analytics, agents, eval, audit.
- `backend/app/approvals/`: HITL approval engine state machine and provider execution engine.
- `backend/app/domain/`: SQLAlchemy models and Pydantic validation schemas.
- `backend/app/events/`: Event bus interface, in-memory pub/sub, event schemas.
- `backend/app/integrations/`: LLM provider, LinkedIn, Email, Lead, and Calendar providers.
- `backend/app/knowledge/`: RAG knowledge search engine indexing playbooks and templates.
- `frontend/src/app/`: Next.js 14 App Router dashboard with 11 dedicated pages.
