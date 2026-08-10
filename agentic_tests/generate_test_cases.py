"""
Runs the Test Planner and saves its output. The
Orchestrator will call this agent as part of the full run.
"""

import json
from pathlib import Path

from agents.test_planner_agent import TestPlannerAgent

if __name__ == "__main__":
    planner = TestPlannerAgent()
    test_cases = planner.generate_test_cases()
    coverage = planner.coverage_report(test_cases)

    output_path = Path(__file__).parent / "artifacts" / "test_cases.json"
    output_path.write_text(json.dumps(test_cases, indent=2))

    print(f"Generated {len(test_cases)} test cases -> {output_path}")
    print("\nCoverage by category:")
    for category, ids in coverage.items():
        print(f"  {category}: {len(ids)} cases ({', '.join(ids)})")
