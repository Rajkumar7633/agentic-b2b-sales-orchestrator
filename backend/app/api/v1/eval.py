from fastapi import APIRouter

from app.domain.schemas.schemas import EvaluationRunResponse
from app.evaluation.evaluator import evaluation_engine

router = APIRouter(prefix="/eval", tags=["AI Quality & Evaluation"])


@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation_suite():
    res = await evaluation_engine.run_evaluation_suite()
    return res
