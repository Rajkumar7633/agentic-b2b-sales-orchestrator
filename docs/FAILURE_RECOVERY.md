# Failure Recovery & Resilience (`docs/FAILURE_RECOVERY.md`)

## 1. Resilience Patterns

NEXORA implements 4 layers of fault tolerance:

1. **LLM Provider Fallback**:
   - If Groq/xAI API returns non-200 or times out (>30s), `GrokProvider` logs a warning and delegates execution to `MockLLMProvider`.

2. **Event Retry Mechanism**:
   - `InMemoryEventBus` retries failing event subscribers up to `max_retries = 3` with exponential backoff (`0.1s`, `0.2s`, `0.4s`).

3. **Dead Letter Queue (DLQ)**:
   - Events that exceed retry limits are diverted to `bus.dead_letter_queue` with error details preserved for analysis and replay.

4. **Schema Normalization Guard**:
   - Agents (e.g. `CompanyResearchAgent`, `OutreachAgent`) normalize raw JSON dicts before calling Pydantic `model_validate`, ensuring missing optional keys do not crash workflow execution.
