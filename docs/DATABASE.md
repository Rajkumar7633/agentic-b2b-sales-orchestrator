# Database Schema & Models (`docs/DATABASE.md`)

## 1. Overview

NEXORA uses SQLAlchemy 2.0 async ORM with PostgreSQL (or SQLite async fallback for local dev).

## 2. Core Entity Relationship Model

- **`Tenant`**: Multi-tenant isolation boundary (`id`, `name`, `created_at`).
- **`User`**: Account owner (`id`, `tenant_id`, `email`, `hashed_password`, `role`).
- **`Company`**: Target account (`id`, `tenant_id`, `name`, `industry`, `size`, `why_now_signal`, `pipeline_stage`).
- **`CompanyProject`**: Verified expansion project (`id`, `company_id`, `project_name`, `budget`, `timeframe`, `verified`).
- **`CompanySignal`**: Market trigger (`id`, `company_id`, `signal_type`, `summary`, `confidence`).
- **`Contact`**: Named decision maker (`id`, `company_id`, `first_name`, `last_name`, `title`, `influence_score`).
- **`Lead`**: Deterministic fit score (`id`, `company_id`, `contact_id`, `fit_score`, `fit_classification`, `positive_signals`).
- **`OutreachMessage`**: AI generated draft (`id`, `lead_id`, `channel`, `subject`, `body_text`, `approval_status`).
- **`Approval`**: HITL record (`id`, `tenant_id`, `entity_type`, `action_type`, `draft_payload`, `status`, `risk_level`).
- **`Meeting`**: Scheduled meeting (`id`, `lead_id`, `status`, `proposed_slots`, `confirmed_slot`).
- **`AuditLog`**: Audit record (`id`, `tenant_id`, `action`, `actor_id`, `details`, `timestamp`).
