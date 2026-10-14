from typing import Any

from app.agents.base import BaseAgent
from app.domain.schemas.schemas import GoalExecutionPlan, TaskStep


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="planner_agent",
            name="Planner Agent",
            version="1.0.0",
            capabilities=["goal_decomposition", "structured_task_planning"],
            supported_tasks=["create_pursuit_plan"]
        )

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        company_name = payload.get("company_name", "Target Account")
        goal = payload.get("goal", f"Pursue account {company_name}")

        tasks: list[TaskStep] = [
            TaskStep(step_id=1, agent_name="Company Research Agent", task_name="research_company", description=f"Research web intelligence, projects, and why-now signals for {company_name}"),
            TaskStep(step_id=2, agent_name="Lead Discovery Agent", task_name="discover_leads", description=f"Identify key decision makers and C-suite roles for {company_name}"),
            TaskStep(step_id=3, agent_name="Lead Scoring Agent", task_name="score_lead", description="Calculate deterministic ICP fit score (0-100) and classification"),
            TaskStep(step_id=4, agent_name="Outreach Agent", task_name="draft_outreach", description="Draft personalized LinkedIn/Email outreach based on research"),
            TaskStep(step_id=5, agent_name="Human Approval Gate", task_name="request_approval", description="Hold for explicit human review before outbound dispatch"),
            TaskStep(step_id=6, agent_name="Follow-up Agent", task_name="schedule_followup", description="Queue 5-7 day follow-up state machine"),
            TaskStep(step_id=7, agent_name="Meeting Scheduler Agent", task_name="propose_meeting", description="Propose and schedule meeting slots upon prospect engagement"),
            TaskStep(step_id=8, agent_name="CRM / Pipeline Agent", task_name="update_pipeline", description="Sync pipeline stage and interaction audit records")
        ]

        plan = GoalExecutionPlan(
            goal=goal,
            company_name=company_name,
            tasks=tasks,
            status="READY"
        )
        return plan.model_dump()
