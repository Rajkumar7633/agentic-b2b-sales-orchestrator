# REST API Reference (`docs/API.md`)

## Endpoints Summary

Base path: `/api/v1`

### Authentication (`/auth`)
- `POST /auth/login`: Authenticate and receive JWT access token.

### Target Accounts (`/accounts`)
- `GET /accounts`: List target accounts for active tenant.
- `GET /accounts/{id}`: Get account detail with projects & signals.
- `POST /accounts/pursue`: Trigger multi-agent pursuit workflow for account.

### Human Approvals (`/approvals`)
- `GET /approvals`: List pending HITL approval records.
- `POST /approvals/{id}/approve`: Approve draft and dispatch via provider.
- `POST /approvals/{id}/reject`: Reject draft with refinement feedback.

### Contacts & Scoring (`/contacts`, `/leads`)
- `GET /contacts`: List decision maker contacts.
- `GET /leads`: List lead fit scores and classification reasons.

### Outreach & Meetings (`/outreach`, `/meetings`)
- `GET /outreach`: List outreach message queue.
- `GET /meetings`: List proposed and booked meetings.

### Excel Studio (`/excel`)
- `POST /excel/import`: Upload `.xlsx` sales workbook.
- `GET /excel/export`: Download formatted pipeline Excel workbook.

### Agent Registry & Evaluation (`/agents`, `/eval`, `/analytics`)
- `GET /agents`: List registered agents and capabilities.
- `POST /eval/run`: Run automated evaluation benchmark suite.
- `GET /analytics`: Telemetry metrics, conversion rates, and weekly recommendations.
- `GET /audit-logs`: Query system audit logs.
