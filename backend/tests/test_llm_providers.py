import pytest

from app.integrations.llm.provider import GrokProvider, MockLLMProvider


@pytest.mark.asyncio
async def test_mock_llm_returns_company_research_schema():
    provider = MockLLMProvider()
    result = await provider.generate_json("Research company Acme Construction. Return company overview.")
    assert "why_now_signal" in result
    assert "projects" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_mock_llm_returns_scoring_schema():
    provider = MockLLMProvider()
    result = await provider.generate_json("Calculate lead score and fit_score for this company.")
    assert "fit_score" in result
    assert isinstance(result["fit_score"], int)
    assert 0 <= result["fit_score"] <= 100
    assert result["fit_classification"] in ["HIGH", "MEDIUM", "LOW"]


@pytest.mark.asyncio
async def test_mock_llm_returns_outreach_schema():
    provider = MockLLMProvider()
    result = await provider.generate_json("Draft personalized linkedin outreach message to Marcus.")
    assert "body_text" in result
    assert "channel" in result
    assert result["approval_status"] == "PENDING"
    assert result["channel"] in ["LINKEDIN", "EMAIL"]


@pytest.mark.asyncio
async def test_grok_provider_falls_back_to_mock_without_api_key():
    """GrokProvider with no API key must fall back to MockLLMProvider."""
    provider = GrokProvider(api_key="")
    result = await provider.generate_json("Research target account.")
    assert "why_now_signal" in result
    assert result["confidence"] >= 0.0
