import pytest

from app.agents.company_research import CompanyResearchAgent
from app.integrations.llm.provider import BaseLLMProvider


class MalformedLLMProvider(BaseLLMProvider):
    async def generate_json(self, prompt: str, schema=None):
        # Return incomplete / unexpected JSON structure
        return {"garbage_key": 12345}


@pytest.mark.asyncio
async def test_agent_recovers_from_malformed_llm_output():
    agent = CompanyResearchAgent()
    agent.llm = MalformedLLMProvider()

    # Execution should not crash; normalization fallback fills default fields
    res = await agent.execute({"company_name": "Test Enterprise Solutions"})
    assert res is not None
    assert res["company_name"] == "Test Enterprise Solutions"
    assert "confidence" in res
    assert isinstance(res["projects"], list)
    assert len(res["projects"]) > 0
