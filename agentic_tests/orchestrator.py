"""
Runs every test case, one by one. A single failure never stops the rest -
each test case is wrapped in its own try/except.
"""

import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

SCREENSHOTS_DIR = Path(__file__).resolve().parent / "artifacts" / "screenshots"


class Orchestrator:
    def __init__(self, execution_agent, validation_agent, fix_agent):
        self.execution_agent = execution_agent
        self.validation_agent = validation_agent
        self.fix_agent = fix_agent

    def run(self, test_cases):
        results = []

        for test_case in test_cases:
            timestamp = datetime.now(timezone.utc).isoformat()
            start = time.perf_counter()
            try:
                execution_result = self.execution_agent.run(test_case)
                validation_result = self.validation_agent.validate(test_case, execution_result)

                result = {
                    "test_case_id": test_case["id"],
                    "name": test_case["name"],
                    "status": validation_result["status"],
                    "expected_result": validation_result["expected_result"],
                    "actual_result": validation_result["actual_result"],
                    "timestamp": timestamp,
                    "duration_ms": int((time.perf_counter() - start) * 1000),
                    "error_message": "; ".join(validation_result["deviations"]) or None,
                    "screenshot": None,
                    "logs": execution_result.get("logs"),
                }

                if validation_result["status"] == "failed":
                    # Analyze the failed test case and provide recommendations for fixing it
                    fix = self.fix_agent.analyze(
                        test_case=test_case,
                        execution_result=execution_result,
                        validation_result=validation_result,
                    )
                    # Add the fix recommendations to the result
                    result["severity"] = fix["severity"]
                    result["suggested_fix"] = {
                        "component": fix["component"],
                        "cause": fix["cause"],
                        "recommendation": fix["recommendation"],
                        "regression_test": fix["regression_test"],
                    }

                self._finalize_screenshot(result, test_case)
                results.append(result)
            # Handle any exceptions that occur during test execution
            except Exception as error:
                result = {
                    "test_case_id": test_case["id"],
                    "name": test_case["name"],
                    "status": "blocked",
                    "expected_result": None,
                    "actual_result": None,
                    "timestamp": timestamp,
                    "duration_ms": int((time.perf_counter() - start) * 1000),
                    "error_message": str(error),
                    "screenshot": None,
                    "logs": traceback.format_exc(),
                }
                self._finalize_screenshot(result, test_case)
                results.append(result)

        return results

    def _finalize_screenshot(self, result, test_case):
        # UiRunner always captures a screenshot, unconditionally - it
        # doesn't know pass/fail, that's this component's job. A passed
        # test's screenshot is deleted; a failed or blocked one is kept
        # and renamed so its filename is findable from the report.
        if test_case["type"] != "ui":
            return

        working_path = SCREENSHOTS_DIR / f"{test_case['id']}.png"
        if not working_path.exists():
            return

        if result["status"] == "passed":
            working_path.unlink()
            return

        final_path = SCREENSHOTS_DIR / f"{test_case['id']}_{result['status']}.png"
        # .replace(), not .rename(): on Windows, rename() raises if the
        # destination already exists (e.g. a screenshot left over from a
        # previous run) - replace() overwrites it, cross-platform.
        working_path.replace(final_path)
        result["screenshot"] = f"artifacts/screenshots/{final_path.name}"
