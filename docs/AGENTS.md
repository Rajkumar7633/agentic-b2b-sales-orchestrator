# NEXORA Agent Registry (`docs/AGENTS.md`)

This document serves as the authoritative specification for all 10 AI Agents implemented in the **NEXORA Pursuit Engine**.

---

## 1. Supervisor Agent (`supervisor_agent`)

- **1. Purpose**: Orchestrate multi-agent sales pursuit workflows, manage correlation IDs, route execution graphs, enforce state transitions, and register HITL approval gates.
- **2. Responsibilities**:
  - Receive account pursuit requests from UI, Excel import, or API.
  - Coordinate execution with `PlannerAgent`.
  - Dispatch event triggers (`company.research.requested`, etc.).
  - Hold outbound communication steps for human approval.
- **3. Inputs**: `{"company_name": str, "domain": Optional[str], "tenant_id": str}`
- **4. Outputs**: `{"status": "APPROVAL_REQUIRED", "correlation_id": str, "plan": dict, "scoring": dict, "approval_required": dict}`
- **5. Tools**: `AgentRegistry`, `InMemoryEventBus`, `HITLApprovalEngine`.
- **6. Memory Used**: Session execution context, correlation ID state map.
- **7. Events Consumed**: `pursuit.initiated`, `approval.decision.recorded`
- **8. Events Published**: `company.research.requested`, `outreach.approval.requested`
- **9. Permissions**: `ADMIN`, `REVIEWER`, `SALES_REP` (Initiation only).
- **10. Failure Modes**: LLM timeout, downstream service exception, missing tenant context.
- **11. Retry Strategy**: 3 attempts with exponential backoff (1s, 2s, 4s).
- **12. Human Approval Requirements**: None for planning/scoring; holds for outbound actions.
- **13. LLM/Model Used**: Groq Llama-3.3-70b / xAI Grok (`GrokProvider`).
- **14. Configuration**: `DEFAULT_TENANT_ID`, `LLM_PROVIDER`, `EVENT_BUS`.
- **15. Unit/Integration Test Coverage**: `tests/test_e2e_pursuit.py`, `tests/test_agents.py`.
- **16. Example Execution**:
  ```python
  agent = SupervisorAgent()
  result = await agent.execute({"company_name": "Tesla Energy", "tenant_id": "tenant_nexora_default"})
  ```

---

## 2. Planner Agent (`planner_agent`)

- **1. Purpose**: Decompose business goals into ordered task DAGs, assign specialized agents, and define dependency chains.
- **2. Responsibilities**:
  - Translate "pursue this account" into a 8-step execution graph.
  - Inject explicit `Human Approval Gate` step before dispatch.
- **3. Inputs**: `{"goal": str, "company_name": str}`
- **4. Outputs**: `{"goal": str, "tasks": List[dict], "status": "READY"}`
- **5. Tools**: Task Graph Generator.
- **6. Memory Used**: In-memory task plan structure.
- **7. Events Consumed**: None (invoked directly by Supervisor).
- **8. Events Published**: None.
- **9. Permissions**: Internal System Agent.
- **10. Failure Modes**: Invalid goal payload.
- **11. Retry Strategy**: Immediate deterministic fallback.
- **12. Human Approval Requirements**: None.
- **13. LLM/Model Used**: Rule-based DAG generator + LLM fallback.
- **14. Configuration**: Max steps = 10.
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_planner_creates_structured_task_graph`.
- **16. Example Execution**:
  ```python
  planner = PlannerAgent()
  plan = await planner.execute({"goal": "Pursue Acme Corp", "company_name": "Acme Corp"})
  ```

---

## 3. Company Research Agent (`company_research_agent`)

- **1. Purpose**: Perform firmographic enrichment, identify upcoming projects, funding signals, hiring trends, and why-now buying triggers.
- **2. Responsibilities**:
  - Gather intelligence for target account.
  - Search playbooks via RAG Knowledge Service.
  - Return verified projects and web citations.
- **3. Inputs**: `{"company_name": str, "domain": Optional[str]}`
- **4. Outputs**: `CompanyResearchOutput` (industry, size, revenue, why_now_signal, projects, signals, confidence).
- **5. Tools**: RAG `KnowledgeService`, `BaseLLMProvider`.
- **6. Memory Used**: RAG Vector Context (Sales Playbooks).
- **7. Events Consumed**: `company.research.requested`
- **8. Events Published**: `company.research.completed`
- **9. Permissions**: Read-only web/knowledge access.
- **10. Failure Modes**: LLM response JSON schema validation error.
- **11. Retry Strategy**: Robust dictionary field normalization + Mock fallback.
- **12. Human Approval Requirements**: None.
- **13. LLM/Model Used**: Groq Llama-3.3-70b / xAI Grok.
- **14. Configuration**: RAG top_k = 3.
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_company_research_agent_returns_verified_projects`.
- **16. Example Execution**:
  ```python
  agent = CompanyResearchAgent()
  res = await agent.execute({"company_name": "Acme Construction"})
  ```

---

## 4. Lead Discovery Agent (`lead_discovery_agent`)

- **1. Purpose**: Identify executive decision makers (C-Suite, VP, Director) matching target buying personas.
- **2. Responsibilities**:
  - Query lead intelligence providers.
  - Calculate executive influence scores.
  - Extract verified contact metadata (email, LinkedIn).
- **3. Inputs**: `{"company_id": str, "company_name": str}`
- **4. Outputs**: `{"discovered_contacts": List[ContactSchema]}`
- **5. Tools**: `MockLeadProvider` / LinkedIn Integrations.
- **6. Memory Used**: Contact cache.
- **7. Events Consumed**: `company.research.completed`
- **8. Events Published**: `leads.discovered`
- **9. Permissions**: Read-only lead data.
- **10. Failure Modes**: Lead provider API timeout.
- **11. Retry Strategy**: 2 retries then mock provider fallback.
- **12. Human Approval Requirements**: None.
- **13. LLM/Model Used**: Persona matching rules + LLM.
- **14. Configuration**: Persona titles = ["VP Procurement", "CTO", "Director"].
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_lead_discovery_agent_returns_contacts`.
- **16. Example Execution**:
  ```python
  agent = LeadDiscoveryAgent()
  res = await agent.execute({"company_id": "comp_001", "company_name": "Apex Energy"})
  ```

---

## 5. Lead Scoring Agent (`lead_scoring_agent`)

- **1. Purpose**: Compute deterministic Ideal Customer Profile (ICP) fit score (0-100) and classification (`HIGH`, `MEDIUM`, `LOW`).
- **2. Responsibilities**:
  - Evaluate company research signals, verified projects, and contact seniority.
  - Calculate mathematical weighted fit score.
  - Output reasoning summary and positive/negative signal breakdown.
- **3. Inputs**: `{"company_research": dict, "contact": dict}`
- **4. Outputs**: `LeadScoringOutput` (fit_score, fit_classification, reasoning_summary, positive_signals, negative_signals).
- **5. Tools**: Deterministic Scoring Engine.
- **6. Memory Used**: ICP criteria weightings.
- **7. Events Consumed**: `leads.discovered`
- **8. Events Published**: `lead.scoring.completed`
- **9. Permissions**: Read-only computation.
- **10. Failure Modes**: Missing input keys.
- **11. Retry Strategy**: Deterministic baseline fallback (Score 75).
- **12. Human Approval Requirements**: None.
- **13. LLM/Model Used**: Rule-based scoring engine with LLM summary synthesis.
- **14. Configuration**: High threshold >= 80, Medium threshold >= 50.
- **15. Unit/Integration Test Coverage**: `tests/test_scoring.py`, `tests/test_agents.py`.
- **16. Example Execution**:
  ```python
  agent = LeadScoringAgent()
  res = await agent.execute({"company_research": {...}, "contact": {...}})
  ```

---

## 6. Outreach Agent (`outreach_agent`)

- **1. Purpose**: Draft personalized multi-channel (LinkedIn / Email) outreach messages tailored to target contact persona and verified why-now signals.
- **2. Responsibilities**:
  - Retrieve RAG outreach templates.
  - Draft highly relevant message text.
  - Set draft status to `PENDING` approval.
- **3. Inputs**: `{"company_name": str, "contact": dict, "why_now_signal": str}`
- **4. Outputs**: `OutreachDraftOutput` (lead_id, channel, subject, body_text, reasoning, approval_status="PENDING").
- **5. Tools**: RAG Template Search, `BaseLLMProvider`.
- **6. Memory Used**: RAG Template Knowledge Base.
- **7. Events Consumed**: `lead.scoring.completed`
- **8. Events Published**: `outreach.approval.requested`
- **9. Permissions**: Internal drafting permission only (Cannot execute outbound call).
- **10. Failure Modes**: Template missing or LLM timeout.
- **11. Retry Strategy**: Fallback to baseline personalized template.
- **12. Human Approval Requirements**: **MANDATORY**. Draft is locked until approved by human in Approval Center.
- **13. LLM/Model Used**: Groq Llama-3.3-70b / xAI Grok.
- **14. Configuration**: Default channel = `LINKEDIN`.
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_outreach_agent_always_produces_pending_draft`.
- **16. Example Execution**:
  ```python
  agent = OutreachAgent()
  res = await agent.execute({"company_name": "Acme", "contact": {...}, "why_now_signal": "Series C"})
  ```

---

## 7. Follow-up Agent (`followup_agent`)

- **1. Purpose**: Manage 5-7 day non-response cadence and automated follow-up sequences.
- **2. Responsibilities**:
  - Calculate cadence intervals.
  - Monitor prospect interaction state.
  - Draft follow-up messages for approval.
- **3. Inputs**: `{"lead_id": str, "cadence_days": int, "current_attempt": int}`
- **4. Outputs**: `{"status": "SCHEDULED", "next_followup_at": str, "sequence_number": int}`
- **5. Tools**: Sequence Cadence Scheduler.
- **6. Memory Used**: Interaction timeline.
- **7. Events Consumed**: `outreach.approved`, `prospect.no_response`
- **8. Events Published**: `followup.scheduled`
- **9. Permissions**: Internal scheduling permission.
- **10. Failure Modes**: Attempt overflow (> max_attempts).
- **11. Retry Strategy**: Cap sequence at max_attempts = 3.
- **12. Human Approval Requirements**: Mandatory approval for follow-up message dispatches.
- **13. LLM/Model Used**: Sequence state machine + LLM template.
- **14. Configuration**: Cadence days = 7, max attempts = 3.
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_followup_agent_schedules_correct_cadence`.
- **16. Example Execution**:
  ```python
  agent = FollowupAgent()
  res = await agent.execute({"lead_id": "lead_001", "cadence_days": 7})
  ```

---

## 8. Meeting Scheduler Agent (`meeting_scheduler_agent`)

- **1. Purpose**: Propose 3 availability slots and coordinate calendar bookings upon prospect response.
- **2. Responsibilities**:
  - Query calendar availability.
  - Format 3 meeting time proposals.
  - Handle calendar invite creation upon approval.
- **3. Inputs**: `{"lead_id": str, "company_name": str}`
- **4. Outputs**: `{"status": "PROPOSED", "proposed_slots": List[str], "meeting_id": str}`
- **5. Tools**: `MockCalendarProvider`.
- **6. Memory Used**: Representative calendar slots.
- **7. Events Consumed**: `prospect.replied`
- **8. Events Published**: `meeting.proposed`, `meeting.booked`
- **9. Permissions**: Calendar API Read/Write.
- **10. Failure Modes**: Calendar slot overlap.
- **11. Retry Strategy**: Shift window by +24 hours.
- **12. Human Approval Requirements**: Mandatory approval for external invite dispatch.
- **13. LLM/Model Used**: Calendar slot parsing + LLM invitation generator.
- **14. Configuration**: Duration = 30 mins.
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_meeting_scheduler_proposes_three_slots`.
- **16. Example Execution**:
  ```python
  agent = MeetingSchedulerAgent()
  res = await agent.execute({"lead_id": "lead_001", "company_name": "Acme"})
  ```

---

## 9. CRM / Pipeline Agent (`crm_pipeline_agent`)

- **1. Purpose**: Synchronize account pursuit pipeline stages across internal database and external CRM systems.
- **2. Responsibilities**:
  - Transition account stage (`TARGET` -> `QUALIFIED` -> `OUTREACH_SENT` -> `MEETING_BOOKED`).
  - Log audit trail records.
- **3. Inputs**: `{"company_id": str, "lead_id": str, "new_stage": str}`
- **4. Outputs**: `{"status": "SYNCHRONIZED", "pipeline_stage": str, "synced_at": str}`
- **5. Tools**: PostgreSQL Database Session, Audit Logger.
- **6. Memory Used**: Database transactional state.
- **7. Events Consumed**: `outreach.approved`, `meeting.booked`
- **8. Events Published**: `pipeline.stage.updated`
- **9. Permissions**: Database Write permission.
- **10. Failure Modes**: Database transaction deadlock.
- **11. Retry Strategy**: Transaction rollback and retry (3x).
- **12. Human Approval Requirements**: None (Internal state sync).
- **13. LLM/Model Used**: Deterministic database synchronizer.
- **14. Configuration**: Isolated per tenant.
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_crm_pipeline_agent_updates_stage`.
- **16. Example Execution**:
  ```python
  agent = CRMPipelineAgent()
  res = await agent.execute({"company_id": "comp_001", "new_stage": "MEETING_BOOKED"})
  ```

---

## 10. Analytics Agent (`analytics_agent`)

- **1. Purpose**: Calculate pipeline telemetry, conversion rates, channel response metrics, and weekly AI recommendations.
- **2. Responsibilities**:
  - Aggregate target account stats.
  - Calculate meeting conversion rates.
  - Generate weekly AI pursuit plan suggestions.
- **3. Inputs**: `{"tenant_id": str}`
- **4. Outputs**: `AnalyticsResponse` (total_accounts, qualified_leads, high_value_leads, response_rate, weekly_recommendations).
- **5. Tools**: Analytics Query Engine.
- **6. Memory Used**: Aggregated metric tables.
- **7. Events Consumed**: None (Invoked on schedule or UI request).
- **8. Events Published**: `analytics.refreshed`
- **9. Permissions**: Read-only telemetry.
- **10. Failure Modes**: Empty dataset handling.
- **11. Retry Strategy**: Return baseline default metrics.
- **12. Human Approval Requirements**: None.
- **13. LLM/Model Used**: SQL aggregator + LLM recommendation synthesizer.
- **14. Configuration**: 30-day rolling window.
- **15. Unit/Integration Test Coverage**: `tests/test_agents.py::test_analytics_agent_returns_complete_kpis`.
- **16. Example Execution**:
  ```python
  agent = AnalyticsAgent()
  res = await agent.execute({"tenant_id": "tenant_nexora_default"})
  ```
