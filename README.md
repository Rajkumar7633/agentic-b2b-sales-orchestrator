# ⚡ NEXORA — Agentic B2B Sales Orchestrator

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg?logo=redis&logoColor=white)](https://redis.io)
[![Tests](https://img.shields.io/badge/Tests-142%20Passed-brightgreen.svg)](https://pytest.org)
[![Coverage](https://img.shields.io/badge/Coverage-84%25-success.svg)](https://pytest-cov.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **Enterprise-Grade Autonomous B2B Sales Pursuit & Revenue Engine** powered by 10 specialized Agentic AI Micro-services, Human-in-the-Loop (HITL) Safety Gates, Multi-Provider LLM Intelligence (xAI Grok, Groq Llama-3.3-70B, Mock), Event-Driven Architecture, Deterministic Lead Scoring, and Bi-directional Excel Data Ingestion.

---

## 📑 Table of Contents

- [Executive Overview](#-executive-overview)
- [System Architecture](#-system-architecture)
- [The 10 Autonomous AI Agents](#-the-10-autonomous-ai-agents)
- [Multi-Agent Orchestration Flow](#-multi-agent-orchestration-flow)
- [Human-in-the-Loop (HITL) Governance](#-human-in-the-loop-hitl-governance)
- [Deterministic Fit Scoring Algorithm](#-deterministic-fit-scoring-algorithm)
- [Bi-Directional Excel Ingestion Engine](#-bi-directional-excel-ingestion-engine)
- [Tech Stack](#-tech-stack)
- [Quick Start Guide](#-quick-start-guide)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#1-backend-setup-fastapi)
  - [Frontend Setup](#2-frontend-setup-nextjs-14)
  - [Docker Compose Deployment](#3-docker-compose-deployment)
- [Automated Verification & Test Suite](#-automated-verification--test-suite)
- [API Reference & Endpoints](#-api-reference--endpoints)
- [Security & Multi-Tenancy](#-security--multi-tenancy)
- [Project Structure](#-project-structure)
- [Documentation Index](#-documentation-index)

---

## 🌟 Executive Overview

**NEXORA** is a full-stack, enterprise-grade autonomous sales pursuit engine designed to replace brittle point-to-point prospecting tools with an **orchestrated multi-agent system**. 

Traditional SDR automation blasts generic outreach. NEXORA orchestrates specialized micro-agents that:
1. Detect accounts and intent signals.
2. Ingest structured enterprise data from custom Excel sheets without data loss.
3. Conduct deep firmographic & technographic research.
4. Calculate mathematical, deterministic ICP fit scores (0–100).
5. Synthesize hyper-personalized multi-channel copy (LinkedIn, Email, Exec Briefings).
6. **Enforce Human-in-the-Loop (HITL) approval gates** before any communication is dispatched.
7. Schedule meetings, process transcripts, and deliver real-time pipeline velocity analytics.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    subgraph UI ["Frontend Client (Next.js 14 App Router)"]
        Dashboard["Executive Dashboard"]
        Pipeline["Kanban Pipeline"]
        ApprovalsUI["HITL Approval Center"]
        ExcelUI["Excel Studio"]
        AnalyticsUI["Analytics & KPIs"]
    end

    subgraph Gateway ["FastAPI Gateway & Security Layer"]
        AuthMiddleware["JWT Auth & Multi-Tenant RBAC"]
        RateLimiter["Redis Token Bucket Rate Limiter"]
        AuditLogger["Immutable Audit Logger"]
    end

    subgraph Core ["Agent Orchestration & Event Bus"]
        Supervisor["Supervisor & Planner Agent"]
        EventBus["Async Event Bus (Correlation IDs & DLQ)"]
        WorkingMem["Redis Session & Working Memory"]
    end

    subgraph Agents ["10 Autonomous Micro-Agents"]
        Discovery["Lead Discovery Agent"]
        Research["Company Research Agent"]
        Scoring["Lead Scoring Agent (0-100 ICP)"]
        Outreach["Outreach Generator Agent"]
        HITL["Approval Governance Agent"]
        Meeting["Meeting Intelligence Agent"]
        ExcelAgent["Excel Ingestion / Export Agent"]
        Analytics["Pipeline Analytics Agent"]
        Knowledge["RAG & Knowledge Graph Agent"]
        Evaluator["LLM Benchmark & Eval Agent"]
    end

    subgraph Storage ["Enterprise Persistence Tier"]
        PG[(PostgreSQL 16 AsyncPG)]
        RedisCache[(Redis Cache & State)]
        Docs[(RAG Document Vectors)]
    end

    UI -->|REST + Bearer JWT| Gateway
    Gateway --> Core
    Core <--> Agents
    Agents <--> Storage
    Core <--> EventBus
```

---

## 🤖 The 10 Autonomous AI Agents

| # | Agent Name | Core Responsibility | Output Artifact |
|---|---|---|---|
| 1 | **Supervisor Agent** | Decomposes high-level sales pursuits into coordinated multi-agent subtasks | Execution DAG, Agent Task Assignments |
| 2 | **Lead Discovery Agent** | Ingests raw accounts, searches decision makers, extracts intent signals | Enriched Lead Profiles, Discovered Contacts |
| 3 | **Company Research Agent** | Analyzes technographics, financial triggers, industry headwinds, news | 360° Account Intelligence Brief |
| 4 | **Lead Scoring Agent** | Computes deterministic ICP score (0–100) + LLM qualitative fit analysis | Tier Classification (`HIGH`, `MEDIUM`, `LOW`) |
| 5 | **Outreach Generator** | Synthesizes personalized multichannel copy (LinkedIn InMail, cold email) | Actionable Draft Messages |
| 6 | **Approval Control Agent** | Enforces governance, evaluates message risk, triggers HITL gates | Approval Tickets (`PENDING`, `APPROVED`, `REJECTED`) |
| 7 | **Meeting Intelligence** | Coordinates calendar slots, ingests call transcripts, extracts next steps | Structured Meeting Notes & Action Items |
| 8 | **Excel Studio Agent** | Parses, maps, validates, and syncs multi-sheet enterprise workbooks | Additive Ingestions & Two-Way Sync |
| 9 | **Pipeline Analytics** | Computes pipeline velocity, stage conversion, and bottleneck diagnostics | Real-Time Metrics & Recommendations |
| 10 | **AI Evaluation Agent** | Runs continuous benchmarks on LLM outputs (hallucination scoring, tone) | Quality Metrics & Model Evals |

---

## 🔄 Multi-Agent Orchestration Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Sales Rep / Admin
    participant Excel as Excel Ingestion Engine
    participant Sup as Supervisor & Planner
    participant Res as Research & Scoring Agents
    participant Out as Outreach Generator
    participant Gate as HITL Approval Gate
    participant Bus as Event Bus & Adapters
    participant DB as PostgreSQL & Redis

    User->>Excel: Upload XLSX Workbook (Companies + Contacts)
    Excel->>DB: Additive Ingestion & Deduplication
    User->>Sup: Trigger Pursuit Workflow
    Sup->>Res: Dispatch Research & Fit Scoring Tasks
    Res->>DB: Store Firmographics & Compute 0-100 Score
    Res->>Out: Hand off Qualified Leads
    Out->>Gate: Draft Outreach Message (Risk: MEDIUM/HIGH)
    Note over Gate: Execution PAUSES automatically.<br/>No message dispatched without sign-off.
    User->>Gate: Review, Edit & Approve Message
    Gate->>Bus: Publish `outreach.approved` Domain Event
    Bus->>DB: Record Immutable Audit Log & Update Pipeline Stage
```

---

## 🛡️ Human-in-the-Loop (HITL) Governance

In enterprise sales, unchecked AI hallucination or premature outreach can damage brand reputation. NEXORA implements strict **HITL safety gates**:

- **Automated Risk Triage**: Messages are classified as `LOW`, `MEDIUM`, or `HIGH` risk based on account tier, tone, and deal size.
- **Mandatory Approval Pause**: The outreach agent drafts messages and transitions the state to `PENDING_APPROVAL`.
- **Reviewer Action**: Authorized users (`ADMIN`, `REVIEWER`) can:
  - **Approve**: Dispatches the communication via configured provider (Mock, LinkedIn, Email).
  - **Edit & Approve**: Modifies copy inline; audit logs store both the AI draft and the human edits.
  - **Reject**: Halts the outreach and logs the reviewer's rejection reason.
- **Role Enforcement**: Sales reps cannot approve their own high-risk campaigns without managerial sign-off.

---

## 📐 Deterministic Fit Scoring Algorithm

Rather than relying on ungrounded LLM guesses, NEXORA evaluates accounts through a deterministic multi-factor algorithm combined with qualitative LLM reasoning:

$$\text{Score} = w_1 \cdot S_{\text{industry}} + w_2 \cdot S_{\text{size}} + w_3 \cdot S_{\text{revenue}} + w_4 \cdot S_{\text{intent}} + w_5 \cdot S_{\text{technographic}}$$

```python
# ICP Scoring Tiers
Score >= 80: TIER_1 (Immediate Multi-Channel Outreach)
Score 50-79: TIER_2 (Nurture & Technographic Research)
Score < 50:  TIER_3 (Low Priority / Disqualified)
```

Each score is saved with an explainable breakdown showing exact positive signals, negative deductions, and confidence ratings.

---

## 📊 Bi-Directional Excel Ingestion Engine

NEXORA features a custom Excel processing pipeline powered by `openpyxl`:
- **Additive Ingestion (Append-Only)**: Uploading new sheets *never* overwrites or drops existing account histories.
- **Deduplication**: Automatically detects duplicates by normalized company name and domain, skipping duplicates gracefully.
- **Multi-Sheet Support**: Ingests both `Companies` and `Contacts` sheets simultaneously, linking foreign keys automatically.
- **Validation & Error Isolation**: Malformed rows or missing columns produce structured warnings without crashing the batch.
- **Export Engine**: Export full live database snapshots back into styled XLSX workbooks at any time.

---

## 💻 Tech Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | **Python 3.13**, **FastAPI**, **Pydantic v2**, **Uvicorn** |
| **Frontend Framework** | **Next.js 14** (App Router), **TypeScript**, **Tailwind CSS**, **Lucide Icons** |
| **Database & ORM** | **PostgreSQL 16**, **SQLAlchemy 2.0 (Async)**, **AsyncPG**, **SQLite (Test Runner)** |
| **Cache & State** | **Redis 7**, Distributed Locks, Token Bucket Rate Limiting |
| **LLM Providers** | **xAI Grok**, **Groq (Llama-3.3-70B)**, **OpenAI**, **Anthropic**, **Mock Provider** |
| **Event Architecture** | **In-Memory Event Bus** with Dead-Letter Queues (DLQ) & Correlation IDs |
| **Testing & CI/CD** | **Pytest**, **Pytest-AsyncIO**, **Pytest-Cov** (142 tests, 84% coverage), GitHub Actions |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm
- **PostgreSQL 14+** (or Docker)
- **Redis** (optional; defaults to in-memory fallback)

---

### 1. Backend Setup (FastAPI)

```bash
# Clone the repository
git clone https://github.com/Rajkumar7633/agentic-b2b-sales-orchestrator.git
cd agentic-b2b-sales-orchestrator/backend

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp ../.env.example .env

# Initialize database schema and active agents
PYTHONPATH=. python app/seeds/seed.py

# Start FastAPI server
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend is now live at `http://localhost:8000`.  
Explore interactive OpenAPI docs at `http://localhost:8000/docs`.

---

### 2. Frontend Setup (Next.js 14)

In a separate terminal:

```bash
cd agentic-b2b-sales-orchestrator/frontend

# Install dependencies
npm install

# Start development dashboard
npm run dev -- --port 3000
```

Open `http://localhost:3000` in your browser.

---

### 3. Docker Compose Deployment

Launch the entire stack (FastAPI, Next.js, PostgreSQL, Redis) with a single command:

```bash
docker-compose up --build -d
```

To stop:
```bash
docker-compose down
```

---

## 🧪 Automated Verification & Test Suite

The repository includes a comprehensive test suite running against ASGI mock transports and isolated database fixtures.

```bash
cd backend
source .venv/bin/activate

# Run all 142 automated tests
PYTHONPATH=. pytest -v

# Run with test coverage report
PYTHONPATH=. pytest --cov=app --cov-report=term-missing
```

### Verified Test Results:
```
======================= 142 passed, 3 warnings in 9.49s =======================
TOTAL Coverage: 84%
```

| Test Category | Tests | Description |
|---|---|---|
| **E2E Pursuit Workflow** | 3 tests | Health check, pursuit initiation, HITL approval, meeting sync |
| **Multi-Agent Registry** | 10 tests | Agent capability declaration, discovery, health status, metadata |
| **HITL Governance** | 11 tests | State transitions, RBAC enforcement, expiration, audit triggers |
| **Excel Ingestion / Export** | 17 tests | Multi-sheet parsing, deduplication, row-validation, export integrity |
| **Deterministic Scoring** | 5 tests | ICP algorithmic weights, boundary tests, tier classifications |
| **Analytics Engine** | 12 tests | KPI calculations, industry breakdown, stage distributions |
| **Security & RBAC** | 14 tests | JWT issuance, tenant isolation, role barriers (Admin, Reviewer, Rep) |
| **Event Bus & DLQ** | 4 tests | Async pub/sub, subscriber failure recovery, dead-letter routing |

---

## 🌐 API Reference & Endpoints

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **System** | `GET` | `/health` | Health status and uptime |
| **Auth** | `POST` | `/api/v1/auth/login` | Issue JWT access token |
| **Accounts** | `GET` | `/api/v1/accounts` | List accounts with pipeline stages |
| **Accounts** | `POST` | `/api/v1/accounts` | Create or update account |
| **Contacts** | `GET` | `/api/v1/contacts` | List executive contacts |
| **Approvals** | `GET` | `/api/v1/approvals` | List pending HITL approval items |
| **Approvals** | `POST` | `/api/v1/approvals/{id}/approve` | Approve message dispatch |
| **Approvals** | `POST` | `/api/v1/approvals/{id}/reject` | Reject message dispatch |
| **Excel** | `POST` | `/api/v1/excel/inspect` | Inspect workbook sheets and columns |
| **Excel** | `POST` | `/api/v1/excel/import` | Execute additive workbook import |
| **Excel** | `GET` | `/api/v1/excel/export` | Export database state to XLSX |
| **Analytics** | `GET` | `/api/v1/analytics` | High-level metrics, KPIs & recommendations |
| **Agents** | `GET` | `/api/v1/agents` | Status and metrics for all 10 AI agents |
| **Meetings** | `GET` | `/api/v1/meetings` | Scheduled meetings and transcripts |
| **Audit** | `GET` | `/api/v1/audit-logs` | Immutable system activity audit log |

---

## 🔐 Security & Multi-Tenancy

- **Row-Level Tenant Isolation**: Every query and database transaction enforces `tenant_id` boundaries.
- **Role-Based Access Control (RBAC)**:
  - `ADMIN`: Full access to accounts, agents, config, and audit logs.
  - `REVIEWER`: Can review, edit, approve, or reject HITL outreach messages.
  - `SALES_REP`: Can browse accounts, contacts, and initiate pursuits (cannot approve outbound messages).
- **Data Sanitization & Secret Redaction**: Audit logs automatically redact sensitive fields (passwords, tokens, API keys) via regex filters before persisting.

---

## 📂 Project Structure

```
agentic-b2b-sales-orchestrator/
├── .github/workflows/          # CI/CD GitHub Actions pipelines
├── ARCHITECTURE.md             # System architecture & sequence diagrams
├── README.md                   # Project documentation & guide
├── docker-compose.yml          # Containerized multi-service orchestrator
├── docs/                       # 20+ Detailed technical specification specs
├── NEXORA_Pursuit_Engine_Dummy.xlsx # Sample dataset for instant testing
│
├── backend/                    # FastAPI Microservices Backend
│   ├── app/
│   │   ├── agents/             # 10 Autonomous AI Agents & Registry
│   │   ├── api/v1/             # REST API Endpoints & Route Handlers
│   │   ├── approvals/          # Human-in-the-Loop Approval Engine
│   │   ├── core/               # Security, Database, Audit, RBAC
│   │   ├── domain/             # SQLAlchemy Models & Pydantic Schemas
│   │   ├── evaluation/         # LLM Hallucination & Scoring Evaluator
│   │   ├── events/             # Domain Event Bus & Dead-Letter Queue
│   │   ├── excel/              # OpenPyXL Importer & Exporter
│   │   ├── integrations/       # LLM, LinkedIn, Email, Calendar Providers
│   │   └── memory/             # Redis Session & Working Memory
│   ├── tests/                  # Pytest automated test suite (142 tests)
│   ├── requirements.txt        # Python backend dependencies
│   └── pytest.ini              # Pytest configuration
│
└── frontend/                   # Next.js 14 Modern Web Console
    ├── src/
    │   ├── app/                # App Router Pages (15 Routes)
    │   │   ├── accounts/       # Account Intelligence Scorecards
    │   │   ├── approvals/      # HITL Review & Approval Portal
    │   │   ├── excel/          # Workbook Ingestion Studio
    │   │   ├── pipeline/       # Dynamic Kanban Pursuit Board
    │   │   ├── analytics/      # Pipeline Velocity & KPIs
    │   │   └── ...             # Outreach, Meetings, Audit, Evaluation
    │   └── components/         # Reusable UI Components & Glassmorphism Sidebar
    ├── package.json            # Node.js dependencies
    └── tailwind.config.js      # Tailored styling tokens
```

---

## 📚 Documentation Index

Deep-dive engineering specs are available in the [`/docs`](docs/) directory:

- 🏗️ **[System Architecture](docs/ARCHITECTURE.md)** — Architectural patterns & topology
- 🤖 **[Agent Registry Specification](docs/AGENTS.md)** — Detailed specs for all 10 AI Agents
- 🔄 **[Agent Workflows](docs/AGENT_WORKFLOWS.md)** — State machines & transition logic
- ⚡ **[Event Bus Architecture](docs/EVENT_BUS.md)** — Async messaging, pub/sub topics & retries
- 🧠 **[Memory Systems](docs/MEMORY_ARCHITECTURE.md)** — Redis working memory & PostgreSQL state
- 🛡️ **[Human-in-the-Loop Engine](docs/HUMAN_IN_THE_LOOP.md)** — Approval policies & risk grading
- 🗄️ **[Data Model Specification](docs/DATA_MODEL.md)** — Relational entity schemas & diagrams
- 🌐 **[REST API Reference](docs/API.md)** — Complete OpenAPI specification
- 🔐 **[Security & RBAC](docs/SECURITY.md)** — Authentication, tokens, and multi-tenant isolation
- 🧪 **[Testing Architecture](docs/TESTING.md)** — Test plan & coverage breakdown

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Built for Enterprise Autonomous Sales Orchestration</b>
</p>
