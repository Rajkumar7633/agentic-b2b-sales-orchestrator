# Knowledge Engine & RAG Architecture (`docs/KNOWLEDGE_AND_RAG.md`)

## 1. Overview

The RAG Knowledge Service (`app/knowledge/rag_engine.py`) provides semantic memory augmentation for AI agents. It indexes target enterprise sales playbooks, objection handling guidelines, and cold outreach templates.

## 2. In-Memory & Persistent Vector Memory Tiering

```
 ┌────────────────────────────────────────────────────────────────┐
 │                      Knowledge Layer Architecture              │
 │                                                                │
 │  Working / Session Memory  ──►  Redis (Token & context cache)  │
 │  Long-Term Data Memory    ──►  PostgreSQL (Schemas & entities) │
 │  Semantic Vector Memory   ──►  RAG Knowledge Service (Cosine)  │
 └────────────────────────────────────────────────────────────────┘
```

## 3. Query Flow

1. Agent (`CompanyResearchAgent` or `OutreachAgent`) passes query string (e.g. `"Acme data center expansion software"`).
2. `KnowledgeService.search(query, top_k=3)` performs keyword + semantic similarity scoring against indexed sales playbook chunks.
3. Top matching context snippets are injected directly into the LLM prompt.
