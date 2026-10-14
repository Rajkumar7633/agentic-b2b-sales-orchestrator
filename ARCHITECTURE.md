# 🏛️ Architecture & System Design — NEXORA

This document details the architectural blueprints, design patterns, event flows, and state machines underpinning the **NEXORA Agentic B2B Sales Orchestrator**.

---

## 1. High-Level Enterprise Topology

```mermaid
graph TB
    subgraph Client ["Client Layer"]
        NextJS["Next.js 14 Web Console<br/>(TypeScript, Tailwind CSS, Lucide)"]
    end

    subgraph Gateway ["API Gateway & Core Security"]
        FastAPI["FastAPI Async REST Gateway<br/>(Python 3.13, Pydantic v2)"]
        Auth["JWT Authenticator & RBAC Engine"]
        RateLimit["Distributed Rate Limiter (Token Bucket)"]
        Audit["Immutable Audit Log Dispatcher"]
    end

    subgraph Orchestration ["Agentic Orchestration Layer"]
        Supervisor["Supervisor Agent<br/>(Workflow DAG Orchestration)"]
        Planner["Planner Agent<br/>(Task Decomposition & Strategy)"]
        EventBus["Async Domain Event Bus<br/>(Correlation IDs, DLQ, Retries)"]
    end

    subgraph Agents ["Specialized Micro-Agent Pool"]
        LeadDiscovery["Lead Discovery Agent"]
        CompanyResearch["Company Research Agent"]
        LeadScoring["Lead Scoring Agent (0-100 ICP)"]
        OutreachGen["Outreach Generator Agent"]
        ApprovalControl["HITL Approval Governance Agent"]
        MeetingIntel["Meeting Intelligence Agent"]
        ExcelStudio["Excel Studio Ingestion / Export"]
        Analytics["Pipeline Analytics Agent"]
        KnowledgeGraph["RAG & Knowledge Graph Agent"]
        Evaluation["AI Evaluation & Hallucination Agent"]
    end

    subgraph Storage ["Persistence & State Infrastructure"]
        PG[(PostgreSQL 16 Engine<br/>AsyncPG Connection Pool)]
        Redis[(Redis 7 Cache<br/>Session & Working Memory)]
        RAG[(Vector & Knowledge Store)]
    end

    NextJS -->|REST + Bearer JWT| FastAPI
    FastAPI --> Auth
    Auth --> RateLimit
    RateLimit --> Orchestration
    Orchestration <--> EventBus
    Orchestration <--> Agents
    Agents <--> Storage
    Audit --> PG
```

---

## 2. Core Architectural Principles

1. **AI Proposes, Humans Approve (HITL First)**:
   Autonomous agents possess read and preparation privileges. However, high-impact external actions (email dispatch, LinkedIn messages, calendar invitations, contract pricing) strictly pause at `PENDING_APPROVAL` status. The system cannot autonomously contact prospects without human sign-off.
2. **Row-Level Multi-Tenancy**:
   Every database model contains `tenant_id`. Every API request resolves `UserContext` from the JWT bearer token, and all database queries enforce row-level tenant filtering. Cross-tenant data bleed is impossible.
3. **Event-Driven Asynchronous Decoupling**:
   Agents communicate across a non-blocking domain event bus. Long-running tasks (e.g., firmographic web crawling or LLM synthesis) publish events such as `account.discovered`, `research.completed`, and `outreach.drafted` rather than holding synchronous HTTP connections.
4. **Resilience & Dead-Letter Queue (DLQ)**:
   If an agent encounters an error or malformed LLM response, the event bus retries with exponential backoff. If retry thresholds are exceeded, messages are diverted to a Dead-Letter Queue (DLQ) with correlation IDs for diagnostic playback without impacting the rest of the cluster.
5. **Zero External API Lock-In**:
   Full end-to-end functionality executes out of the box using realistic mock providers (`MockLLMProvider`, `MockWebResearchProvider`, `MockLinkedInProvider`, `MockEmailProvider`, `MockCalendarProvider`). Real Grok API keys or alternative LLMs can be toggled via environment settings with zero code changes.

---

## 3. Human-in-the-Loop (HITL) State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFTED: Outreach Agent generates copy
    DRAFTED --> RISK_ASSESSMENT: Evaluate account tier & tone
    RISK_ASSESSMENT --> PENDING_APPROVAL: Risk evaluated (LOW / MED / HIGH)
    
    state PENDING_APPROVAL {
        [*] --> InQueue
        InQueue --> UnderReview: Reviewer opens ticket
    }

    PENDING_APPROVAL --> APPROVED: Reviewer approves as-is
    PENDING_APPROVAL --> EDITED_AND_APPROVED: Reviewer modifies text & approves
    PENDING_APPROVAL --> REJECTED: Reviewer rejects with feedback

    APPROVED --> DISPATCHED: Integration provider executes send
    EDITED_AND_APPROVED --> DISPATCHED: Integration provider executes send
    REJECTED --> ARCHIVED: Feedback logged for agent re-prompting

    DISPATCHED --> [*]
    ARCHIVED --> [*]
```

---

## 4. Multi-Layer Memory Architecture

| Memory Tier | Technology | Lifetime | Purpose |
|---|---|---|---|
| **Working Memory** | Memory / Thread Context | Request / Task Lifetime | Stores intermediate prompt tokens, scratchpad calculations, and current DAG step status. |
| **Session Memory** | Redis 7 (`SETEX`) | Session (Configurable TTL) | Stores short-term dialogue context, active user sessions, and rate-limit token buckets. |
| **Long-Term Memory** | PostgreSQL 16 (AsyncPG) | Permanent (Transactional) | Accounts, Contacts, Pipeline Stages, Audit Logs, Approval Decisions, and Agent Metrics. |
| **Knowledge Memory** | Vector Embeddings / RAG | Permanent / Versioned | Company collateral, sales playbooks, objection-handling scripts, and buyer persona briefs. |

---

## 5. Domain Event Catalog

| Event Name | Producer | Consumers | Description |
|---|---|---|---|
| `account.ingested` | Excel / API | Research Agent, Scoring Agent | Triggered when new company record is created. |
| `research.completed` | Research Agent | Scoring Agent, Supervisor | Emitted when 360° firmographic profile is ready. |
| `lead.scored` | Scoring Agent | Supervisor, Outreach Agent | Emitted when ICP score and tier are calculated. |
| `outreach.drafted` | Outreach Agent | Approval Control Agent | Emitted when personalized copy is generated. |
| `approval.created` | Approval Control | Notification Service, Frontend | Signals new item in HITL approval center. |
| `outreach.approved` | Reviewer (UI) | Email / LinkedIn Provider | Triggered upon human sign-off; authorizes message send. |
| `outreach.sent` | Integration Provider | Pipeline Analytics, Audit Logger | Confirms successful external message dispatch. |
| `meeting.scheduled` | Meeting Intelligence | Calendar Provider, Analytics | Confirms calendar booking with prospect. |

---

## 6. Deterministic ICP Fit Scoring Formula

$$S_{\text{total}} = 0.30 \cdot S_{\text{industry}} + 0.25 \cdot S_{\text{revenue}} + 0.20 \cdot S_{\text{headcount}} + 0.15 \cdot S_{\text{intent}} + 0.10 \cdot S_{\text{tech}}$$

```
Tier 1 (High Fit):    Score >= 80  --> Immediate Multi-Channel Outreach
Tier 2 (Medium Fit):  Score 50-79  --> Nurture Campaign / Additional Research
Tier 3 (Low Fit):     Score < 50   --> Disqualified or Long-Term Tracking
```

---

## 7. Security & Compliance Architecture

- **JWT Authentication**: HS256 / RS256 token verification with user claims (`sub`, `email`, `role`, `tenant_id`).
- **Role Hierarchies**:
  - `ADMIN`: Full system configuration, user provisioning, audit inspection.
  - `REVIEWER`: Review, edit, approve, or reject outbound messages.
  - `SALES_REP`: Account discovery, pursuit initiation, contact creation.
- **Audit Immutability**: All actions generate an `AuditLog` row containing user ID, tenant ID, timestamp, IP, action, resource, and redacted payload parameters. Passwords and API secrets are automatically scrubbed before persistence.

---

## 8. Real-Time Streaming Architecture (Server-Sent Events)

```mermaid
sequenceDiagram
    autonumber
    actor Client as Next.js 14 Client
    participant Gateway as FastAPI Router (/stream)
    participant Broadcaster as Async System Event Broadcaster
    participant Agents as Multi-Agent Pool

    Client->>Gateway: GET /api/v1/stream/pursuit?company_name=...
    Gateway-->>Client: HTTP 200 (text/event-stream)
    loop Sequential Multi-Agent Execution
        Agents->>Gateway: Step Progress & Chain-of-Thought
        Gateway-->>Client: data: {"step": 1, "phase": "DISCOVERY", "thought": "..."}\n\n
    end
    Agents->>Gateway: Staged at HITL Gate (100% Progress)
    Gateway-->>Client: data: {"step": 6, "phase": "GOVERNANCE", "status": "PENDING_APPROVAL"}\n\n

    Note over Client,Broadcaster: Live Event Broadcast Feed
    Client->>Gateway: GET /api/v1/stream/events
    Broadcaster-->>Client: data: {"event_type": "PIPELINE_STAGE_CHANGED", ...}\n\n
```

---

## 9. Durable Cadence & Workflow Engine

```mermaid
stateDiagram-v2
    [*] --> Day1_Research: Cadence Initialized (Day 1)
    Day1_Research --> Day3_OutreachDraft: 360° Firmographics Ingested
    
    state Day3_OutreachDraft {
        [*] --> SynthesizeCopy: Generate Email Pitch
        SynthesizeCopy --> StageHITL: Route to Approval Queue
    }

    Day3_OutreachDraft --> WAITING_APPROVAL: Outreach Drafted
    WAITING_APPROVAL --> Day6_LinkedInFollowup: Manager Signs Off
    
    state Day6_LinkedInFollowup {
        [*] --> SynthesizeInMail: Generate LinkedIn Pitch
        SynthesizeInMail --> StageInMailHITL: Route to Approval Queue
    }

    Day6_LinkedInFollowup --> Day10_MeetingSync: Follow-up Dispatched
    Day10_MeetingSync --> COMPLETED: Calendar Slots Synchronized
    COMPLETED --> [*]
```

