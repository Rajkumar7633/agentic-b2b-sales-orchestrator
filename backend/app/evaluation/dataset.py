from typing import Any

EVALUATION_BENCHMARK_DATASET: list[dict[str, Any]] = [
    {
        "test_case_id": "eval_001",
        "company_name": "Acme Infrastructure",
        "expected_industry": "Enterprise Construction & Engineering",
        "expected_fit_classification": "HIGH",
        "min_expected_score": 80,
        "ground_truth_claims": [
            "$85M Growth Funding Raised",
            "Regional Data Center Expansion Project Alpha"
        ]
    },
    {
        "test_case_id": "eval_002",
        "company_name": "Apex Global Energy",
        "expected_industry": "Energy & Utilities",
        "expected_fit_classification": "HIGH",
        "min_expected_score": 75,
        "ground_truth_claims": [
            "Solar Grid Modernization RFP",
            "VP Procurement Hiring"
        ]
    },
    {
        "test_case_id": "eval_003",
        "company_name": "Small Local Hardware Store",
        "expected_industry": "Retail",
        "expected_fit_classification": "LOW",
        "min_expected_score": 25,
        "ground_truth_claims": []
    }
]
