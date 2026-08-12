"""
Runs the full Orchestrator loop against a live backend and prints a
summary. Standalone for now - gets folded into run_agentic_tests.py
once the Fix Recommendation and Report agents exist (Step 10).
"""

import os

from dotenv import load_dotenv

load_dotenv()

from agents.execution_agent import ExecutionAgent
from agents.test_planner_agent import TestPlannerAgent
from agents.validation_agent import ValidationAgent
from orchestrator import Orchestrator
from runners.api_runner import ApiRunner
from runners.ui_runner import UiRunner

if __name__ == "__main__":
    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")

    orchestrator = Orchestrator(
        planner=TestPlannerAgent(),
        execution_agent=ExecutionAgent(
            api_runner=ApiRunner(base_url),
            ui_runner=UiRunner(frontend_url, base_url),
        ),
        validation_agent=ValidationAgent(),
    )
    results = orchestrator.run()

    counts = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1

    print(f"Ran {len(results)} test cases against {base_url}")
    print(counts)
    print()
    for result in results:
        line = f"  {result['test_case_id']} [{result['status']}] {result['name']}"
        if result["status"] == "failed":
            line += f" - {result['validation']['deviations']}"
        elif result["status"] == "blocked":
            line += f" - {result['error']}"
        print(line)
