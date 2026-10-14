# Memory Architecture (`docs/MEMORY_ARCHITECTURE.md`)

## Memory Layers Overview

NEXORA utilizes a 3-tier memory model:

1. **Short-Term Agent Memory (Execution Context)**:
   - In-memory state tracking per pursuit transaction.
   - Preserves correlation ID, current task step, and transient LLM responses during multi-step pursuit execution.

2. **Long-Term Vector Memory (RAG Knowledge Engine)**:
   - Implemented via `app/knowledge/rag_engine.py` (`KnowledgeService`).
   - Indexes sales playbooks, objection handling guides, and cold outreach templates.
   - Evaluates cosine/text similarity search to inject context into `CompanyResearchAgent` and `OutreachAgent` prompts.

3. **Persistent Structural Memory (PostgreSQL Source of Truth)**:
   - Stores account records (`Company`), project signals (`CompanyProject`, `CompanySignal`), named decision makers (`Contact`), lead fit scores (`Lead`), HITL approval decisions (`Approval`), and audit logs (`AuditLog`).
   - Supports multi-tenant isolation via `tenant_id` foreign keys.
