import pytest

from app.evaluation.evaluator import EvaluationEngine


@pytest.mark.asyncio
async def test_evaluation_suite_runs_and_returns_score():
    engine = EvaluationEngine()
    result = await engine.run_evaluation_suite()

    assert "lead_quality_score" in result
    assert "research_factuality_score" in result
    assert "hallucination_rate" in result
    assert "overall_system_rating" in result

    # Factuality should be above 70% for a production-ready agent
    assert result["research_factuality_score"] >= 70.0

    # Hallucination rate must be under 30%
    assert result["hallucination_rate"] < 30.0

    # Overall system rating must be either approved or needs refinement
    assert result["overall_system_rating"] in ["PRODUCTION_APPROVED", "NEEDS_REFINEMENT"]
