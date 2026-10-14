# Human-in-the-Loop AI Pursuit Workflow Specification

The **NEXORA Pursuit Engine** combines **4 Active AI Reasoning Agents** with strict **Human-in-the-Loop (HITL)** execution boundaries.

---

## 🔄 End-to-End Pursuit Sequence

```
USER UPLOADS XLSX WORKBOOK
            │
            ▼
DYNAMIC INGESTION ENGINE (Schema Mapping & PostgreSQL Persistence)
            │
            ▼
USER SELECTS REAL TARGET COMPANY
            │
            ▼
AGENT 1: COMPANY RESEARCH AGENT (Scrapes web info, projects, Why Now signals, source URLs)
            │
            ▼
AGENT 2: OPPORTUNITY QUALIFICATION AGENT (ICP Fit Scoring, PURSUE/REVIEW/REJECT)
            │
            ▼
AGENT 3: CONTACT DISCOVERY & RANKING AGENT (Ranks decision makers, public source links)
            │
            ▼
HUMAN-IN-THE-LOOP APPROVAL GATE (Approve / Reject Outbound Draft)
            │
  ┌─────────┴─────────┐
  ▼                   ▼
REJECT             APPROVE
  │                   │
Archive               ▼
           HUMAN OUTREACH & LINKEDIN TASK (Human contacts prospect)
                      │
                      ▼
           HUMAN SCHEDULES GOOGLE MEET (Provides Meet link & date)
                      │
                      ▼
           MEETING OCCURS (Human conducts call)
                      │
                      ▼
           HUMAN PASTES / UPLOADS TRANSCRIPT
                      │
                      ▼
AGENT 4: MEETING INTELLIGENCE AGENT (Extracts summary, pain points, buying intent, deal signals)
                      │
                      ▼
HUMAN CONFIRMS RECOMMENDED NEXT ACTION → UPDATE PIPELINE / RECORD
```

---

## 🤖 Active AI Agents vs Human Boundaries

| Component | Responsibility | Type |
| :--- | :--- | :--- |
| **Company Research Agent** | Firmographic enrichment, project discovery, Why-Now signals | **AI Agent** |
| **Opportunity Qualification Agent** | Explainable ICP fit scoring (PURSUE / REVIEW / REJECT) | **AI Agent** |
| **Contact Ranking Agent** | Ranks decision maker roles & public links | **AI Agent** |
| **Outreach Draft Generation** | Drafts candidate messaging for human review | **AI Agent** |
| **LinkedIn Prospecting & Messaging** | Sending InMails, connection requests, messaging | **Human Task** |
| **Meeting Scheduling** | Scheduling Google Meet & setting call time | **Human Task** |
| **Meeting Transcript Analysis** | Extracting pain points, deal signals, buying intent | **AI Agent** |
| **Final Pursuit Decision** | Advancing stage to Closed/Won or archiving | **Human Task** |

---

## 🚦 Workflow States

1. `IDENTIFIED`: Imported from workbook.
2. `RESEARCHED`: Company Research Agent completed.
3. `QUALIFIED`: Qualification Agent evaluated fit.
4. `HUMAN_REVIEW`: Draft holding in Approval Center.
5. `APPROVED`: Human approved outreach draft.
6. `CONTACTED`: Human dispatched message / LinkedIn outreach.
7. `MEETING_SCHEDULED`: Human scheduled Google Meet call.
8. `TRANSCRIPT_ANALYZED`: Meeting Intelligence Agent analyzed transcript.
9. `WON`: Closed / Deal Won.
