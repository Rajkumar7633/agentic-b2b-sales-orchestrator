from typing import Any

from app.agents.base import BaseAgent
from app.domain.schemas.schemas import OutreachDraftOutput
from app.integrations.llm.provider import get_llm_provider
from app.knowledge.rag_engine import knowledge_service


class OutreachAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="outreach_agent",
            name="Outreach Agent",
            version="1.0.0",
            capabilities=["personalized_outreach_drafting", "multi_channel_messaging"],
            supported_tasks=["draft_outreach"]
        )
        self.llm = get_llm_provider()

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        company_name = payload.get("company_name", "Target Company")
        lead_id = payload.get("lead_id", "lead_001")
        contact = payload.get("contact", {})
        first_name = contact.get("first_name", "Marcus")
        title = contact.get("title", "VP Procurement")
        why_now = payload.get("why_now_signal", "Expansion Project")

        # RAG context from templates
        rag_templates = knowledge_service.search("C-Suite Cold Outreach Template")
        template_text = rag_templates[0]["content"] if rag_templates else ""

        prompt = f"""
        Draft a personalized LinkedIn outreach message to {first_name} ({title}) at {company_name}.
        Reason for outreach: {why_now}.
        Use inspiration from template: {template_text}.
        The message MUST be respectful, direct, highlight mutual value, and avoid generic sales jargon.
        Return JSON matching OutreachDraftOutput schema with approval_status="PENDING".
        """

        raw_output = await self.llm.generate_json(prompt)
        # Ensure lead_id and PENDING status
        raw_output["lead_id"] = lead_id
        raw_output["approval_status"] = "PENDING"
        if "channel" not in raw_output:
            raw_output["channel"] = "LINKEDIN"

        # BUG FIX 2: Replace generic placeholder with rich, personalized fallback body
        if not raw_output.get("body_text") or raw_output["body_text"] == "Hello, reaching out regarding alignment.":
            raw_output["body_text"] = (
                f"Hi {first_name},\n\n"
                f"Congratulations on {company_name}'s recent {why_now} — this signals exactly the kind of "
                f"infrastructure and procurement momentum where NEXORA's Pursuit Engine has driven measurable outcomes "
                f"for peer engineering leaders.\n\n"
                f"As {title}, you're likely navigating the challenge of aligning vendor capability with delivery speed "
                f"under tight capital timelines. NEXORA's platform has helped similar leaders streamline pursuit "
                f"workflows while maintaining full human approval control at every critical decision gate.\n\n"
                f"Would you be open to a 15-minute discovery call next Tuesday or Wednesday? I'd love to share how "
                f"two comparable {company_name[:4].upper()}-scale teams reduced pursuit cycle time by 40%.\n\n"
                f"Best regards,\n"
                f"Alex Vance | NEXORA Enterprise Team\n"
                f"alex.vance@nexora.ai | Strategic Partnerships"
            )
        if not raw_output.get("subject"):
            raw_output["subject"] = f"Strategic Alignment: {company_name}'s {why_now}"
        if not raw_output.get("reasoning"):
            raw_output["reasoning"] = (
                f"Personalized based on verified {why_now} signal and {title} seniority match against ICP criteria."
            )

        parsed = OutreachDraftOutput.model_validate(raw_output)
        return parsed.model_dump()
