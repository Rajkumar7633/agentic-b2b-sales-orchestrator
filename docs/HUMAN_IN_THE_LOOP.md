# Human-in-the-Loop (HITL) Architecture (`docs/HUMAN_IN_THE_LOOP.md`)

## 1. Philosophical Principle

> **AI RECOMMENDS & PREPARES; Humans APPROVE customer-facing actions; Systems EXECUTE approved actions.**

Agents in NEXORA have **zero direct execution authority** for customer-facing communication (LinkedIn messages, Emails, Calendar invites).

## 2. Approval Engine State Machine

```
               ┌────────────────────────┐
               │  Outreach Agent Drafts  │
               └───────────┬────────────┘
                           │
                           ▼
               ┌────────────────────────┐
               │  Approval Item Created │
               │    (Status: PENDING)   │
               └───────────┬────────────┘
                           │
            ┌──────────────┴──────────────┐
   (Approve)│                             │(Reject)
            ▼                             ▼
┌───────────────────────┐     ┌───────────────────────┐
│   Status: APPROVED    │     │   Status: REJECTED    │
└───────────┬───────────┘     └───────────┬───────────┘
            │                             │
            ▼                             ▼
 ┌─────────────────────┐       ┌─────────────────────┐
 │  Dispatch via Provider│     │ Refine Prompt / Agent│
 └─────────────────────┘       └─────────────────────┘
```

## 3. Risk Classification Rules

- **`LOW`**: Internal pipeline stage update or non-customer data sync.
- **`MEDIUM`**: Standard personalized outreach to non-C-level prospects.
- **`HIGH`**: C-Level outreach, formal pricing proposals, or high-value account communications.

## 4. Audit Trail & Integrity

Every approval decision records:
- `approved_by_user_id`: ID of human reviewer.
- `approved_at`: ISO timestamp.
- `rejection_reason`: Feedback text if rejected.
- `execution_result`: Dispatch response payload from LinkedIn/Email provider.
