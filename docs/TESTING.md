# Testing Specification (`docs/TESTING.md`)

## 1. Test Suite Architecture

NEXORA includes a 26-test automated verification suite built on `pytest` and `pytest-asyncio`.

## 2. Test File Layout

| Test File | Verification Target | Test Count |
| :--- | :--- | :---: |
| `tests/test_agents.py` | Individual unit tests for all 10 agents | 8 |
| `tests/test_approvals.py` | HITL approval state transitions & provider execution | 1 |
| `tests/test_e2e_pursuit.py` | Full multi-agent pursuit workflow from trigger to approval | 1 |
| `tests/test_evaluation.py` | AI evaluation engine & quality benchmark scoring | 1 |
| `tests/test_event_bus_advanced.py` | Dead Letter Queue (DLQ) & multi-subscriber fanout | 2 |
| `tests/test_events.py` | Event bus pub/sub & idempotency deduplication | 1 |
| `tests/test_excel.py` | Excel sheet parsing & column mapping | 1 |
| `tests/test_excel_advanced.py` | Excel row counting, empty row handling & duplicate prevention | 3 |
| `tests/test_llm_providers.py` | LLM schema output generation & provider fallbacks | 4 |
| `tests/test_rbac_tenancy.py` | Multi-tenant data isolation & RBAC authorization | 3 |
| `tests/test_scoring.py` | ICP fit score calculator | 1 |

## 3. Running Test Commands

```bash
cd backend
PYTHONPATH=. .venv/bin/pytest -v
```
