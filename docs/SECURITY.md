# Security & Role-Based Access Control (`docs/SECURITY.md`)

## 1. Authentication & JWT Tokens

- Authentication uses standard Bearer JWT tokens (`HS256`).
- Token claims include `sub` (User ID), `email`, `role`, and `tenant_id`.

## 2. Multi-Tenant Data Isolation

- Every SQL query filters explicitly by `tenant_id == current_user.tenant_id`.
- Verified by automated unit tests in `tests/test_rbac_tenancy.py::test_tenant_isolation`.

## 3. Role Permissions Matrix

| Operation | ADMIN | REVIEWER | SALES_REP |
| :--- | :---: | :---: | :---: |
| View Dashboard & Pipeline | Yes | Yes | Yes |
| Initiate Pursuit Workflow | Yes | Yes | Yes |
| Review & Approve HITL Action | Yes | Yes | **No (403 Forbidden)** |
| Upload / Export Excel Workbook | Yes | Yes | Yes |
| Run Evaluation Suite | Yes | No | No |
