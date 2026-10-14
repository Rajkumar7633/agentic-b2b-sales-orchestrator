import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), default="SALES_REP")  # ADMIN, SALES_MANAGER, SALES_REP, REVIEWER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g., 500-1000, Enterprise
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revenue: Mapped[str | None] = mapped_column(String(64), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hq_focus: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active_upcoming_work: Mapped[str | None] = mapped_column(Text, nullable=True)
    why_now_signal: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_service: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lead_service: Mapped[str | None] = mapped_column(String(255), nullable=True)
    named_contacts_str: Mapped[str | None] = mapped_column(Text, nullable=True)
    relationship_stage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    timing: Mapped[str | None] = mapped_column(String(128), nullable=True)
    recommended_next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    coverage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    research_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    raw_source_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    pipeline_stage: Mapped[str] = mapped_column(String(64), default="IDENTIFIED", index=True)
    owner_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    projects = relationship("CompanyProject", back_populates="company", cascade="all, delete-orphan")
    signals = relationship("CompanySignal", back_populates="company", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="company", cascade="all, delete-orphan")


class CompanyProject(Base):
    __tablename__ = "company_projects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), index=True, nullable=False)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_type: Mapped[str | None] = mapped_column(String(128), nullable=True)  # e.g., Expansion, Infrastructure, Software
    budget: Mapped[str | None] = mapped_column(String(64), nullable=True)
    timeframe: Mapped[str | None] = mapped_column(String(64), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scale_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_completion: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lead_quality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="PLANNING")
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    company = relationship("Company", back_populates="projects")


class CompanySignal(Base):
    __tablename__ = "company_signals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), index=True, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(64), nullable=False)  # HIRING, FUNDING, EXPANSION, TECH_STACK, NEWS
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.8)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    company = relationship("Company", back_populates="signals")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(64), nullable=True)  # C-Level, VP, Director, Head, Manager
    influence_score: Mapped[float] = mapped_column(Float, default=0.5)
    relationship_status: Mapped[str] = mapped_column(String(64), default="NEW")  # NEW, CONTACTED, ENGAGED, WARM, COLD
    why_this_person: Mapped[str | None] = mapped_column(Text, nullable=True)
    public_profile: Mapped[str | None] = mapped_column(String(512), nullable=True)
    public_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(64), nullable=True)
    suggested_channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    opening_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_intro: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_sent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    date_sent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    accepted: Mapped[str | None] = mapped_column(String(64), nullable=True)
    followup_due: Mapped[str | None] = mapped_column(String(64), nullable=True)
    relationship_stage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    next_best_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_status: Mapped[str] = mapped_column(String(64), default="NOT_STARTED", index=True) # NOT_STARTED, IN_PROGRESS, CONTACTED, RESPONSE_RECEIVED, COMPLETED
    source: Mapped[str] = mapped_column(String(64), default="EXCEL_IMPORT")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    company = relationship("Company", back_populates="contacts")
    leads = relationship("Lead", back_populates="contact")
    outreach_messages = relationship("OutreachMessage", back_populates="contact")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), index=True, nullable=False)
    contact_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("contacts.id"), index=True, nullable=True)
    pipeline_stage: Mapped[str] = mapped_column(String(64), default="IDENTIFIED", index=True)
    fit_score: Mapped[int] = mapped_column(Integer, default=0)
    fit_classification: Mapped[str] = mapped_column(String(32), default="LOW")  # HIGH, MEDIUM, LOW
    score_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    positive_signals: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    negative_signals: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    score_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    linkedin_status: Mapped[str] = mapped_column(String(64), default="NOT_STARTED")
    meeting_status: Mapped[str] = mapped_column(String(64), default="NOT_SCHEDULED")
    meeting_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    meeting_date: Mapped[str | None] = mapped_column(String(128), nullable=True)
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    owner_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.id"), nullable=True)
    last_interaction_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    company = relationship("Company", back_populates="leads")
    contact = relationship("Contact", back_populates="leads")
    outreach_messages = relationship("OutreachMessage", back_populates="lead")
    followups = relationship("Followup", back_populates="lead")
    meetings = relationship("Meeting", back_populates="lead")


class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    lead_id: Mapped[str] = mapped_column(String(64), ForeignKey("leads.id"), index=True, nullable=False)
    contact_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("contacts.id"), index=True, nullable=True)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)  # LINKEDIN, EMAIL, MEETING_INVITE
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_context: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, EDIT_REQUIRED
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    lead = relationship("Lead", back_populates="outreach_messages")
    contact = relationship("Contact", back_populates="outreach_messages")


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # OUTREACH, MEETING, EMAIL, PRICING
    entity_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)  # SEND_LINKEDIN, SEND_EMAIL, BOOK_MEETING
    draft_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="MEDIUM")  # LOW, MEDIUM, HIGH
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, EDIT_REQUIRED, EXPIRED
    requested_by_agent: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by_user_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    audit_changes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)  # captures pre/post edit diff
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Followup(Base):
    __tablename__ = "followups"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    lead_id: Mapped[str] = mapped_column(String(64), ForeignKey("leads.id"), index=True, nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="SCHEDULED", index=True)  # SCHEDULED, DUE, DRAFTED, SENT, CANCELLED
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    current_attempt: Mapped[int] = mapped_column(Integer, default=1)
    cadence_days: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    lead = relationship("Lead", back_populates="followups")


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    lead_id: Mapped[str] = mapped_column(String(64), ForeignKey("leads.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposed_slots: Mapped[list[str]] = mapped_column(JSON, default=list)
    selected_slot: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PROPOSED", index=True)  # PROPOSED, PENDING_APPROVAL, BOOKED, CANCELLED
    calendar_provider: Mapped[str] = mapped_column(String(64), default="MOCK_CALENDAR")
    provider_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    meeting_date: Mapped[str | None] = mapped_column(String(128), nullable=True)
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    booked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    lead = relationship("Lead", back_populates="meetings")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class DomainEventLog(Base):
    __tablename__ = "domain_event_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    event_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    causation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(16), default="1.0")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class AgentRegistryItem(Base):
    __tablename__ = "agent_registry"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g., company_research_agent
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    status: Mapped[str] = mapped_column(String(32), default="HEALTHY")  # HEALTHY, DEGRADED, UNHEALTHY
    capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    supported_tasks: Mapped[list[str]] = mapped_column(JSON, default=list)
    model: Mapped[str] = mapped_column(String(64), default="grok-beta")
    total_invocations: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(64), nullable=False)  # PLAYBOOK, PAST_DEAL, RFP, MESSAGING
    content: Mapped[Text] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_documents.id"), index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_json: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)  # Stores vector embedding array

    document = relationship("KnowledgeDocument", back_populates="chunks")


class WorkbookImport(Base):
    __tablename__ = "workbook_imports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    sheet_names: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    rows_processed: Mapped[int] = mapped_column(Integer, default=0)
    companies_imported: Mapped[int] = mapped_column(Integer, default=0)
    contacts_imported: Mapped[int] = mapped_column(Integer, default=0)
    projects_imported: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED")  # COMPLETED, WARNINGS, FAILED
    warnings: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    errors: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class CadenceWorkflow(Base):
    __tablename__ = "cadence_workflows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), index=True, nullable=False)
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), index=True, nullable=False)
    contact_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("contacts.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")  # ACTIVE, PAUSED, COMPLETED, WAITING_APPROVAL, FAILED
    current_step_index: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, default=4)
    steps_config: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    execution_history: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

