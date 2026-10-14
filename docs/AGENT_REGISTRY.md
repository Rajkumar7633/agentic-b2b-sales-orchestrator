# NEXORA Agent Registry Specification

## 1. Overview
The **Agent Registry** maintains runtime metadata, health status, capabilities, versioning, and execution performance for all 10 agents operating within the NEXORA Pursuit Engine.

It provides a dual-layer persistence model:
1. **In-Memory Registry Singleton** (`app.agents.registry.agent_registry`): High-speed runtime lookup for agent instances and execution info.
2. **Database Persistence Table** (`AgentRegistryItem` model): Relational database table populated at startup and synced during runtime for admin dashboard visibility.

---

## 2. Agent Metadata Schema

Each registered agent tracks the following fields via `BaseAgent.get_info()`:

| Field | Type | Description |
|---|---|---|
| `agent_id` | String | Unique slug identifier (e.g. `supervisor_agent`) |
| `name` | String | Human-readable name (e.g. `Supervisor Agent`) |
| `version` | String | SemVer format (default `1.0.0`) |
| `status` | String | `HEALTHY`, `DEGRADED`, or `UNAVAILABLE` |
| `capabilities` | List[String] | Capability tags (e.g., `['firmographic_enrichment', 'project_discovery']`) |
| `supported_tasks` | List[String] | Task types handled by this agent |
| `total_invocations` | Integer | Total executions since startup |
| `successful_invocations` | Integer | Count of successful runs |
| `failed_invocations` | Integer | Count of failed runs |
| `last_execution_latency_ms` | Float | Duration of last execution in milliseconds |
| `total_tokens_used` | Integer | Total LLM tokens consumed |
| `estimated_cost_usd` | Float | Estimated LLM API cost in USD |
| `last_heartbeat` | ISO Timestamp | UTC timestamp of last activity |

---

## 3. Registered Agents Index

| Agent ID | Agent Class | Primary Capability |
|---|---|---|
| `supervisor_agent` | `SupervisorAgent` | Goal orchestration & HITL policy gatekeeper |
| `planner_agent` | `PlannerAgent` | Goal decomposition & structured task graphs |
| `company_research_agent` | `CompanyResearchAgent` | Firmographic enrichment & why-now signals |
| `lead_discovery_agent` | `LeadDiscoveryAgent` | Executive contact discovery & decision maker search |
| `lead_scoring_agent` | `LeadScoringAgent` | Deterministic ICP scoring (0-100) & reasoning |
| `outreach_agent` | `OutreachAgent` | Personalized LinkedIn/Email message drafting |
| `followup_agent` | `FollowupAgent` | Multi-touch cadence state machine |
| `meeting_scheduler_agent` | `MeetingSchedulerAgent` | Calendar window proposal (3 slots) |
| `crm_pipeline_agent` | `CRMPipelineAgent` | CRM stage transitions & DB updates |
| `analytics_agent` | `AnalyticsAgent` | Pipeline KPIs & weekly AI recommendation plans |

---

## 4. API Endpoints

- `GET /api/v1/agents`: Returns JSON list of all registered agents and their metrics.
