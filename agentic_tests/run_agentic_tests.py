"""
The real entry point for the agentic test suite: generates test cases,
runs every one against a live backend/frontend, and writes the final report.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agents.execution_agent import ExecutionAgent
from agents.fix_recommendation_agent import FixRecommendationAgent
from agents.report_agent import ReportAgent
from agents.test_planner_agent import TestPlannerAgent
from agents.validation_agent import ValidationAgent
from llm.llm_client import MockLLMClient
from orchestrator import Orchestrator
from runners.api_runner import ApiRunner
from runners.ui_runner import UiRunner

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


def main():
    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")

    planner = TestPlannerAgent()
    llm_client = MockLLMClient()

    test_cases = planner.generate_test_cases()
    # Save the generated test cases
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    (ARTIFACTS_DIR / "test_cases.json").write_text(json.dumps(test_cases, indent=2))
    print(f"Generated {len(test_cases)} test cases -> artifacts/test_cases.json")

    orchestrator = Orchestrator(
        execution_agent=ExecutionAgent(
            api_runner=ApiRunner(base_url),
            ui_runner=UiRunner(frontend_url, base_url),
        ),
        validation_agent=ValidationAgent(),
        fix_agent=FixRecommendationAgent(llm_client=llm_client),
    )
    print(f"Running {len(test_cases)} test cases against {base_url} / {frontend_url}...")
    results = orchestrator.run(test_cases)

    report_agent = ReportAgent(llm_client=llm_client)
    coverage = planner.coverage_report(test_cases)
    report = report_agent.generate(results, coverage)

    (ARTIFACTS_DIR / "report.json").write_text(report_agent.to_json(report))
    (ARTIFACTS_DIR / "report.html").write_text(report_agent.to_html(report))

    print()
    print(
        f"{report['passed']}/{report['total']} passed ({report['pass_rate']}%), "
        f"{report['failed']} failed, {report['blocked']} blocked"
    )
    print("Report written to artifacts/report.json and artifacts/report.html")


if __name__ == "__main__":
    main()
