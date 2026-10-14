import json
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseLLMProvider:
    async def generate_json(self, prompt: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM provider that returns realistic structured responses
    conforming to expected agent Pydantic schemas.
    """
    async def generate_json(self, prompt: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        prompt_lower = prompt.lower()

        # Company Research Agent Prompt
        if "research" in prompt_lower or "company overview" in prompt_lower:
            company_name = "Acme Construction"
            if "acme" in prompt_lower:
                company_name = "Acme Construction & Infrastructure"
            elif "nexora" in prompt_lower:
                company_name = "Nexora Global Partners"

            return {
                "company_name": company_name,
                "domain": f"{company_name.lower().replace(' ', '').replace('&', '')}.com",
                "industry": "Enterprise Construction & Engineering",
                "size": "1,000 - 5,000 employees",
                "location": "San Francisco, CA / Global",
                "revenue": "$250M - $500M",
                "why_now_signal": "Secured $85M Series C expansion funding and announced 5 new regional data center projects.",
                "recommended_service": "NEXORA Pursuit Engine Enterprise Platform & Technical Advisory",
                "research_summary": f"{company_name} is actively accelerating digital transformation and infrastructure scaling. They are aggressively hiring engineering leads and procuring automated sales pursuit tools.",
                "confidence": 0.94,
                "projects": [
                    {
                        "project_name": "Regional Data Center Expansion Project Alpha",
                        "project_type": "Infrastructure Modernization",
                        "budget": "$12.5M",
                        "timeframe": "Q3 2026 - Q2 2027",
                        "description": "Constructing high-efficiency edge data center nodes across West Coast markets.",
                        "status": "PLANNING",
                        "source_url": "https://news.acme-infra-demo.com/expansion-announcement",
                        "verified": True
                    },
                    {
                        "project_name": "Automated Logistics & Procurement Hub",
                        "project_type": "Software & Process Automation",
                        "budget": "$4.0M",
                        "timeframe": "Q4 2026",
                        "description": "Upgrading legacy supplier procurement systems with automated vendor vetting.",
                        "status": "RFPOpen",
                        "source_url": "https://news.acme-infra-demo.com/procurement-rfp",
                        "verified": True
                    }
                ],
                "signals": [
                    {
                        "signal_type": "FUNDING",
                        "title": "$85M Growth Funding Raised",
                        "summary": "Closed Series C growth round led by Apex Capital to expand operations.",
                        "source_url": "https://techcrunch-mock.com/acme-growth-funding",
                        "confidence": 0.96
                    },
                    {
                        "signal_type": "HIRING",
                        "title": "Hiring Vice President of Engineering & Procurement",
                        "summary": "14 new open positions in technical operations and strategic vendor sourcing.",
                        "source_url": "https://careers.acme-infra-demo.com/openings",
                        "confidence": 0.92
                    }
                ],
                "sources": [
                    {"title": "Company Press Release", "url": "https://news.acme-infra-demo.com/press"},
                    {"title": "Market Tech Index", "url": "https://marketindex-demo.com/acme"}
                ]
            }

        # Lead Scoring Agent Prompt
        elif "score" in prompt_lower or "fit score" in prompt_lower:
            return {
                "fit_score": 88,
                "fit_classification": "HIGH",
                "reasoning_summary": "High alignment due to active $12.5M infrastructure expansion project, strong Series C funding, hiring C-suite leads, and explicit need for NEXORA enterprise pursuit automation.",
                "positive_signals": [
                    "Recent $85M growth funding raised",
                    "Active project budget matching ICP ($4M+)",
                    "Target decision maker identified (VP Procurement)",
                    "High organizational growth velocity"
                ],
                "negative_signals": [
                    "Longer procurement security review cycle (60 days)"
                ],
                "confidence": 0.91
            }

        # Outreach Agent Prompt
        elif "outreach" in prompt_lower or "personalized" in prompt_lower or "linkedin" in prompt_lower:
            return {
                "lead_id": "lead_001",
                "channel": "LINKEDIN",
                "subject": "Strategic Alignment: Acme's Data Center Expansion",
                "body_text": "Hi Marcus,\n\nCongratulations on Acme's recent Series C funding and the launch of your West Coast Data Center Expansion project! \n\nGiven Acme's rapid scaling, NEXORA's Pursuit Engine platform has helped peer engineering leaders streamline enterprise sales pursuits by 40% while keeping strict human approval control.\n\nWould you be open to a brief 15-minute introductory exchange next Tuesday?\n\nBest regards,\nNEXORA Team",
                "reasoning": "Personalized based on verified Data Center Expansion project and Series C funding signal. References direct VP role relevance.",
                "source_context": {
                    "matched_signal": "$85M Growth Funding Raised",
                    "matched_project": "Regional Data Center Expansion Project Alpha"
                },
                "approval_status": "PENDING"
            }

        # Fallback generic structured JSON
        return {
            "lead_id": "lead_001",
            "channel": "LINKEDIN",
            "subject": "Introductory Discussion",
            "body_text": "Hello, reaching out regarding strategic alignment.",
            "reasoning": "Standard introductory outreach.",
            "approval_status": "PENDING"
        }


class GrokProvider(BaseLLMProvider):
    """
    High-Performance LLM Provider supporting Grok (xAI) and Groq API keys.
    Auto-detects API endpoint based on key format (gsk_ -> Groq, xai- -> xAI).
    Falls back gracefully to MockLLMProvider if API Key is invalid or call fails.
    """
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key if api_key is not None else settings.GROK_API_KEY
        self.mock_fallback = MockLLMProvider()

    async def generate_json(self, prompt: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.api_key:
            logger.info("GROK_API_KEY not set. Using MockLLMProvider fallback.")
            return await self.mock_fallback.generate_json(prompt, schema)

        # Detect Groq vs xAI based on key prefix
        if self.api_key.startswith("gsk_"):
            endpoint = "https://api.groq.com/openai/v1/chat/completions"
            model_name = "llama-3.3-70b-versatile"
            provider_label = "Groq (Llama-3.3-70b)"
        else:
            endpoint = "https://api.x.ai/v1/chat/completions"
            model_name = "grok-beta"
            provider_label = "xAI Grok"

        max_retries = 2
        import asyncio
        import time

        start_time = time.time()
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        endpoint,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": "You are NEXORA Pursuit AI Engine. Respond STRICTLY with valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "response_format": {"type": "json_object"}
                        }
                    )
                    latency_ms = (time.time() - start_time) * 1000
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        usage = data.get("usage", {})
                        tokens = usage.get("total_tokens", 0)
                        logger.info(f"Successfully generated response via {provider_label} in {latency_ms:.2f}ms (Tokens: {tokens})")
                        return json.loads(content)
                    elif response.status_code in [429, 500, 502, 503, 504] and attempt < max_retries:
                        backoff = (2 ** attempt) * 0.5
                        logger.warning(f"{provider_label} API returned {response.status_code}. Retrying in {backoff}s (Attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(backoff)
                    else:
                        logger.warning(f"{provider_label} API returned status {response.status_code}. Falling back to MockLLM.")
                        return await self.mock_fallback.generate_json(prompt, schema)
            except Exception as exc:
                if attempt < max_retries:
                    backoff = (2 ** attempt) * 0.5
                    logger.warning(f"{provider_label} invocation error: {exc!s}. Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"{provider_label} API invocation error after retries: {exc!s}. Falling back to MockLLM.")
                    return await self.mock_fallback.generate_json(prompt, schema)


def get_llm_provider() -> BaseLLMProvider:
    if settings.GROK_API_KEY or settings.LLM_PROVIDER.lower() in ["grok", "groq"]:
        return GrokProvider()
    return MockLLMProvider()
