"""
Analyzes a failed test case and suggests a fix.
"""


class FixRecommendationAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    # Analyze a failed test case and provide recommendations for fixing it
    def analyze(self, test_case, execution_result, validation_result):
        component = self._identify_component(test_case)

        return {
            "component": component,
            "severity": test_case["priority"],
            # Use the LLM to generate a cause for the failure based on the test case, execution result, and validation result
            "cause": self.llm_client.complete(
                self._build_cause_prompt(test_case, execution_result, validation_result)
            ),
            "recommendation": self._suggest_recommendation(test_case, component, validation_result),
            "regression_test": self._suggest_regression_test(test_case),
        }

    def _identify_component(self, test_case):
        category = test_case["category"]
        action = test_case["action"]
        is_ui = test_case["type"] == "ui"

        if category == "negative":
            return "Backend - Upload API (file validation)"
        if category == "dashboard":
            return "Frontend - Dashboard page" if is_ui else "Backend - Dashboard aggregation"
        if category == "ai_algorithm":
            analysis_type = (action.get("form") or {}).get("analysis_type", "unknown")
            return f"Backend - Analyzer ({analysis_type})"
        if category == "functional":
            return "Frontend - Upload/Result flow" if is_ui else "Backend - Analysis API"
        if category == "api":
            path = action.get("path") or ""
            if "dashboard" in path:
                return "Backend - Dashboard API"
            if "analysis" in path:
                return "Backend - Analysis API"
            if "health" in path:
                return "Backend - Health Check API"
            return "Backend - API"
        return "Unknown component"

    def _suggest_recommendation(self, test_case, component, validation_result):
        deviations = validation_result.get("deviations", [])
        if not deviations:
            return f"Investigate {component}."

        shapes = {self._deviation_shape(d) for d in deviations}

        if "status" in shapes:
            return (
                f"Check the route handler in {component} - it's returning "
                f"the wrong HTTP status for what this contract requires."
            )
        if "missing_field" in shapes:
            return (
                f"Check the response schema in {component} - a field "
                f"required by the contract is missing from the response."
            )

        target = "UI element or flow step" if test_case["type"] == "ui" else "response field"
        return f"Check the {target} in {component} that produced the unexpected value."

    @staticmethod
    def _deviation_shape(deviation):
        if deviation.startswith("expected status"):
            return "status"
        if deviation.startswith("missing response fields"):
            return "missing_field"
        return "value_mismatch"

    def _suggest_regression_test(self, test_case):
        suggestions = {
            "negative": "Re-run the negative/file-validation test cases after the fix.",
            "dashboard": "Re-run the dashboard aggregation and UI test cases after the fix.",
            "ai_algorithm": "Re-run the analyzer-specific test cases after the fix.",
            "functional": "Re-run the core upload/analysis functional flow after the fix.",
            "api": "Re-run the full API contract test suite after the fix.",
        }
        return suggestions.get(test_case["category"], "Re-run this test case after the fix.")

    def _build_cause_prompt(self, test_case, execution_result, validation_result):
        deviations = "; ".join(validation_result.get("deviations", [])) or "unspecified deviation"
        return f"Test '{test_case['name']}' failed with: {deviations}. Actual result: {execution_result}."
