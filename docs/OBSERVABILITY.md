# Observability & Audit Logging (`docs/OBSERVABILITY.md`)

## 1. Structured Telemetry Logging

All agents log execution state through python `logging`:
```
2026-08-10 00:34:04,458 [INFO] app.agents.base: [Company Research Agent] Executing task with payload keys: ['company_name']
2026-08-10 00:34:05,504 [INFO] httpx: HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"
2026-08-10 00:34:05,505 [INFO] app.integrations.llm.provider: Successfully generated response via Groq (Llama-3.3-70b)
```

## 2. Agent Telemetry Metrics (`AgentRegistryItem`)

The `AgentRegistry` tracks operational metrics per agent:
- `total_invocations`: Count of task executions.
- `total_tokens_used`: Cumulative LLM tokens consumed.
- `estimated_cost_usd`: Financial cost tracking.
- `status`: `IDLE`, `RUNNING`, `ERROR`, `COMPLETED`.

## 3. Immutable Audit Logs

Every state-changing action writes an immutable record to the `AuditLog` database table:
- Endpoint: `GET /api/v1/audit-logs`
- UI View: `http://localhost:3000/audit`
