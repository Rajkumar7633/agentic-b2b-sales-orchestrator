# AI Quality & Evaluation Framework (`docs/EVALUATION.md`)

## 1. Evaluation Engine Overview

The `EvaluationEngine` (`app/evaluation/evaluator.py`) measures system quality against ground truth pursuit datasets (`EVALUATION_BENCHMARK_DATASET`).

## 2. Metric Specifications

1. **Lead Quality Match Score (%)**:
   - Compares AI predicted ICP fit classification (`HIGH`, `MEDIUM`, `LOW`) against ground truth benchmarks.

2. **Research Factuality Score (%)**:
   - Verifies ratio of factual claims backed by source citations.
   - Threshold: >= 70.0% required for `PRODUCTION_APPROVED` status.

3. **Hallucination Rate (%)**:
   - Calculates frequency of ungrounded signals (confidence rating < 0.5).
   - Target: < 5.0%.

4. **Agent Latency (ms)**:
   - Measures average execution latency per agent step.

## 3. Running Evaluation Suite

- **API Endpoint**: `POST /api/v1/eval/run`
- **UI Studio**: `http://localhost:3000/evaluation`
- **Command Line**:
  ```bash
  pytest tests/test_evaluation.py -v
  ```
