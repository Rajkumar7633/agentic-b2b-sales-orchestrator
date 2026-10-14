from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# AUTH & USER SCHEMAS
# ==========================================
class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    tenant_id: str


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# COMPANY & RESEARCH SCHEMAS
# ==========================================
class ProjectSchema(BaseModel):
    id: str | None = None
    project_name: str
    project_type: str | None = "Expansion"
    budget: str | None = "$500k - $2M"
    timeframe: str | None = "Q3-Q4 2026"
    description: str | None = None
    status: str | None = "PLANNING"
    source_url: str | None = None
    verified: bool = True


class SignalSchema(BaseModel):
    id: str | None = None
    signal_type: str  # HIRING, FUNDING, EXPANSION, TECH_STACK, NEWS
    title: str
    summary: str
    source_url: str | None = None
    confidence: float = 0.85
    detected_at: datetime | None = None


class CompanyResearchOutput(BaseModel):
    company_name: str
    domain: str | None = None
    industry: str
    size: str
    location: str
    revenue: str | None = None
    why_now_signal: str
    recommended_service: str
    research_summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    projects: list[ProjectSchema] = Field(default_factory=list)
    signals: list[SignalSchema] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)


class CompanyResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    domain: str | None = None
    industry: str | None = None
    size: str | None = None
    location: str | None = None
    revenue: str | None = None
    why_now_signal: str | None = None
    recommended_service: str | None = None
    research_summary: str | None = None
    research_confidence: float = 0.0
    pipeline_stage: str = "TARGET"
    created_at: datetime
    projects: list[ProjectSchema] = Field(default_factory=list)
    signals: list[SignalSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CompanyPursueRequest(BaseModel):
    company_id: str | None = None
    company_name: str | None = None
    domain: str | None = None
    custom_instructions: str | None = None


# ==========================================
# CONTACT & LEAD DISCOVERY SCHEMAS
# ==========================================
class ContactSchema(BaseModel):
    id: str | None = None
    company_id: str | None = None
    tenant_id: str | None = None
    first_name: str
    last_name: str
    title: str
    email: str | None = None
    public_email: str | None = None
    linkedin_url: str | None = None
    public_profile: str | None = None
    seniority: str | None = None
    influence_score: float | None = None
    relationship_status: str | None = None
    source: str | None = None
    priority: str | None = None
    why_this_person: str | None = None
    suggested_channel: str | None = None
    opening_context: str | None = None
    linkedin_intro: str | None = None
    linkedin_status: str | None = "NOT_STARTED"
    next_best_action: str | None = None
    notes: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)



class LeadDiscoveryOutput(BaseModel):
    company_id: str
    company_name: str
    discovered_contacts: list[ContactSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# LEAD SCORING SCHEMAS
# ==========================================
class LeadScoringOutput(BaseModel):
    company_id: str
    contact_id: str | None = None
    fit_score: int = Field(ge=0, le=100)
    fit_classification: str  # HIGH, MEDIUM, LOW
    reasoning_summary: str
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class LeadResponse(BaseModel):
    id: str
    tenant_id: str
    company_id: str
    contact_id: str | None = None
    pipeline_stage: str
    fit_score: int
    fit_classification: str
    score_reasoning: str | None = None
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# OUTREACH SCHEMAS
# ==========================================
class OutreachDraftOutput(BaseModel):
    lead_id: str
    contact_id: str | None = None
    channel: str  # LINKEDIN, EMAIL, MEETING_INVITE
    subject: str | None = None
    body_text: str
    reasoning: str
    source_context: dict[str, Any] = Field(default_factory=dict)
    approval_status: str = "PENDING"


class OutreachResponse(BaseModel):
    id: str
    tenant_id: str
    lead_id: str
    contact_id: str | None = None
    channel: str
    subject: str | None = None
    body_text: str
    reasoning: str | None = None
    approval_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# APPROVAL SCHEMAS (HITL)
# ==========================================
class ApprovalResponse(BaseModel):
    id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    action_type: str
    draft_payload: dict[str, Any]
    risk_level: str
    status: str
    requested_by_agent: str
    approved_by_user_id: str | None = None
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalActionRequest(BaseModel):
    rejection_reason: str | None = None
    edited_payload: dict[str, Any] | None = None


# ==========================================
# PLANNER & SUPERVISOR SCHEMAS
# ==========================================
class TaskStep(BaseModel):
    step_id: int
    agent_name: str
    task_name: str
    description: str
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    output: dict[str, Any] | None = None


class GoalExecutionPlan(BaseModel):
    goal: str
    company_name: str
    tasks: list[TaskStep] = Field(default_factory=list)
    status: str = "CREATED"


# ==========================================
# MEETINGS & FOLLOWUP SCHEMAS
# ==========================================
class MeetingProposeRequest(BaseModel):
    lead_id: str
    proposed_slots: list[str]


class MeetingResponse(BaseModel):
    id: str
    tenant_id: str
    lead_id: str
    title: str
    description: str | None = None
    proposed_slots: list[str]
    selected_slot: str | None = None
    status: str
    calendar_provider: str
    meeting_link: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FollowupResponse(BaseModel):
    id: str
    tenant_id: str
    lead_id: str
    sequence_number: int
    status: str
    due_at: datetime
    current_attempt: int
    max_attempts: int
    cadence_days: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ANALYTICS SCHEMAS
# ==========================================
class AnalyticsResponse(BaseModel):
    total_target_accounts: int
    qualified_leads: int
    high_value_leads: int
    outreach_sent: int
    approvals_pending: int
    followups_due: int
    response_rate: float
    meeting_conversion_rate: float
    meetings_booked: int
    pipeline_value_usd: float
    total_contacts: int = 0
    industry_breakdown: dict[str, int] = Field(default_factory=dict)
    pipeline_stage_distribution: dict[str, int] = Field(default_factory=dict)
    weekly_recommendations: list[str] = Field(default_factory=list)


# ==========================================
# AGENT REGISTRY & EVALUATION SCHEMAS
# ==========================================
class AgentRegistryResponse(BaseModel):
    id: str
    name: str
    version: str
    status: str
    capabilities: list[str]
    supported_tasks: list[str]
    model: str
    total_invocations: int
    total_tokens_used: int
    estimated_cost_usd: float
    last_heartbeat: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationRunResponse(BaseModel):
    timestamp: datetime
    lead_quality_score: float
    research_factuality_score: float
    hallucination_rate: float
    outreach_quality_score: float
    approval_rate: float
    meeting_conversion: float
    agent_latency_ms: float
    overall_system_rating: str
