# MCP Tools & Integrations (`docs/MCP_TOOLS.md`)

## 1. Overview

Agents in NEXORA consume tools and external integration providers through standard interface abstractions.

## 2. Tool Declarations & Bindings

| Tool Name | Class | Binding Agents | Description |
| :--- | :--- | :--- | :--- |
| `KnowledgeService` | `app.knowledge.rag_engine` | Research, Outreach | RAG vector playbook search |
| `MockLeadProvider` | `app.integrations.lead` | Lead Discovery | Executive persona discovery & contact extraction |
| `MockLinkedInProvider` | `app.integrations.linkedin` | HITL Engine | Dispatches approved outreach to LinkedIn API |
| `MockEmailProvider` | `app.integrations.email` | HITL Engine | Dispatches approved outreach to SMTP/SendGrid |
| `MockCalendarProvider` | `app.integrations.calendar` | Meeting Scheduler | Calendar slot search & invite creation |
| `ExcelImporter` | `app.excel.importer` | API / Excel Studio | Ingests `.xlsx` sales workbooks |
| `ExcelExporter` | `app.excel.exporter` | API / Excel Studio | Generates downloadable Excel pipeline reports |
| `EvaluationEngine` | `app.evaluation.evaluator` | AI Evaluation Studio | Benchmark quality & factuality suite runner |
