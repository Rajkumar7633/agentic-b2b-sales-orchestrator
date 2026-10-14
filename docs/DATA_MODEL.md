# Data Model Specification

The **NEXORA Pursuit Engine** data model is powered by **Async SQLAlchemy ORM** backed by **PostgreSQL**.
All business records are dynamically ingested from user-uploaded XLSX workbooks and associated with the `tenant_id` for strict multi-tenant isolation.

---

## Core Entities

### 1. `WorkbookImport`
Tracks workbook upload jobs and import lineage.
- `id`: UUID (Primary Key)
- `tenant_id`: Foreign Key to `tenants.id`
- `filename`: String (Original uploaded filename)
- `sheet_names`: JSON array of detected sheets
- `rows_processed`: Integer
- `companies_imported`: Integer
- `contacts_imported`: Integer
- `projects_imported`: Integer
- `status`: String (`PROCESSING`, `COMPLETED`, `WARNINGS`, `FAILED`)
- `warnings`: JSON array of warnings
- `errors`: JSON array of errors

### 2. `Company`
Target accounts ingested from *Master Pipeline*, *Pursuit Profiles*, or *Role Coverage* sheets.
- `id`: UUID (Primary Key)
- `tenant_id`: Foreign Key to `tenants.id`
- `name`: String (Company Name)
- `domain`: String (Corporate Domain)
- `industry` / `sector`: String
- `priority`: String (`High`, `Medium`, `Low`)
- `hq_focus` / `location`: String
- `active_upcoming_work`: Text
- `why_now_signal`: Text
- `recommended_service` / `lead_service`: String
- `named_contacts_str`: Text
- `relationship_stage`: String (`IDENTIFIED`, `RESEARCHED`, `QUALIFIED`, `CONTACTED`, `MEETING_SCHEDULED`, `TRANSCRIPT_ANALYZED`, `WON`)
- `timing`: String
- `recommended_next_action`: Text
- `company_source` / `project_source`: String
- `notes`: Text

### 3. `Contact`
Decision-makers ingested from *Named Contacts* or *Role Coverage* sheets.
- `id`: UUID (Primary Key)
- `tenant_id`: Foreign Key to `tenants.id`
- `company_id`: Foreign Key to `companies.id`
- `first_name` & `last_name`: String
- `title`: String (Executive Role)
- `email` & `public_email`: String
- `linkedin_url` & `public_profile`: String
- `why_this_person`: Text
- `priority`: String
- `suggested_channel`: String (`LINKEDIN`, `EMAIL`)
- `opening_context`: Text
- `linkedin_intro`: Text
- `linkedin_status`: String (`NOT_STARTED`, `IN_PROGRESS`, `CONTACTED`, `RESPONSE_RECEIVED`, `COMPLETED`)
- `next_best_action`: Text

### 4. `Lead`
Pipeline opportunity tracker.
- `id`: UUID (Primary Key)
- `tenant_id`: Foreign Key to `tenants.id`
- `company_id`: Foreign Key to `companies.id`
- `contact_id`: Foreign Key to `contacts.id`
- `pipeline_stage`: String (`IDENTIFIED`, `RESEARCHED`, `QUALIFIED`, `HUMAN_REVIEW`, `CONTACTED`, `MEETING_SCHEDULED`, `TRANSCRIPT_ANALYZED`, `WON`)
- `fit_score`: Integer (0-100)
- `fit_classification`: String (`HIGH`, `MEDIUM`, `LOW`)
- `score_reasoning`: Text
- `positive_signals`: JSON array
- `linkedin_status`: String
- `meeting_status`: String (`NOT_SCHEDULED`, `SCHEDULED`, `COMPLETED`, `TRANSCRIPT_PENDING`, `ANALYZED`)
- `meeting_link`: String
- `meeting_date`: String
- `transcript_text`: Text
- `transcript_analysis`: JSON metadata (summary, pain_points, requirements, objections, buying_intent, deal_signals, next_actions)

### 5. `Meeting`
Human-scheduled calls and AI transcript intelligence records.
- `id`: UUID (Primary Key)
- `tenant_id`: Foreign Key to `tenants.id`
- `lead_id`: Foreign Key to `leads.id`
- `title`: String
- `status`: String (`NOT_SCHEDULED`, `SCHEDULED`, `COMPLETED`, `TRANSCRIPT_PENDING`, `ANALYZED`)
- `calendar_provider`: String (`HUMAN_CALENDAR`)
- `meeting_link`: String (Human Google Meet URL)
- `meeting_date`: String
- `transcript_text`: Text
- `transcript_analysis`: JSON metadata
