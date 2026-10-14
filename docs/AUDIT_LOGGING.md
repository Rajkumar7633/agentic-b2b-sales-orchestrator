# Audit Logging Specification (`docs/AUDIT_LOGGING.md`)

## 1. Overview

NEXORA enforces immutable audit logging for all critical business actions. Audit logs are written through `app/core/audit.py` to the `AuditLog` database table.

## 2. Audited Business Actions

- `USER_LOGIN`: User authentication attempt.
- `COMPANY_PURSUIT_INITIATED`: Multi-agent pursuit workflow triggered for target account.
- `COMPANY_UPDATED`: Manual or automated update to company firmographics.
- `LEAD_SCORED`: Lead scoring agent computed ICP fit score.
- `OUTREACH_DRAFTED`: Outreach agent generated message draft.
- `OUTREACH_APPROVED`: Human reviewer approved outbound message.
- `OUTREACH_REJECTED`: Human reviewer rejected outbound message with feedback.
- `OUTREACH_DISPATCHED`: Provider delivered message to prospect.
- `MEETING_BOOKED`: Prospect meeting confirmed.
- `CRM_SYNCHRONIZED`: Account stage updated in CRM.

## 3. PII & Secret Redaction

The audit logger automatically masks sensitive fields:
- Passwords, tokens, JWTs, API keys are replaced with `[REDACTED]`.
