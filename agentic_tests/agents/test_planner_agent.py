"""
Generates the list of test cases that the Orchestrator will execute.

Most test cases are created automatically from the backend configuration
and the API contract, while scenarios that cannot be generated (such as
dashboard behavior or AI edge cases) are added manually.

Each test case has two separate pieces, for two separate audiences:
  steps  -> plain English, for humans reading the report.
  action -> structured data, for the Execution Agent. Never prose - the
            Executor should never need to "read" steps to know what to do.
"""

from backend_link import ALLOWED_CONTENT_TYPES, ANALYSIS_TYPES, IMAGE_SOURCES, MAX_FILE_SIZE_BYTES
from requirements_spec import API_CONTRACT

DEFAULT_FORM = {
    "site_name": "Test Site",
    "capture_datetime": "2026-01-01T00:00:00",
}


class TestPlannerAgent:
    def __init__(self):
        # Used to generate sequential test case IDs
        self._next_id = 1

    def generate_test_cases(self):
        # Build the complete list of test cases. The empty-database case
        # must run first, before anything else creates data - see its
        # own comment below for why.
        cases = []
        cases.append(self._empty_state_case())
        cases += self._functional_cases()
        cases += self._negative_cases()
        cases += self._api_cases()
        cases += self._dashboard_cases()
        cases += self._ai_algorithm_cases()
        return cases

    def coverage_report(self, test_cases):
        # Group test IDs by category for coverage reporting.
        coverage = {}
        for case in test_cases:
            coverage.setdefault(case["category"], []).append(case["id"])
        return coverage

    def _new_case(self, name, category, priority, steps, action, preconditions=None):
        # Create a test case with a unique ID
        case = {
            "id": f"TC-{self._next_id:03d}",
            "name": name,
            "category": category,
            "type": action["type"],
            "priority": priority,
            "preconditions": preconditions or ["The application is running"],
            "steps": steps,
            "action": action,
        }
        self._next_id += 1
        return case

    # --- Empty state: must run before any other test creates data ---

    def _empty_state_case(self):
        # This can only genuinely test "no data" if the database really is
        # empty when it runs - which is only true if it runs first, before
        # any other test creates an analysis. Ordering IS the precondition.
        return self._new_case(
            name="Dashboard behaves correctly with no data",
            category="dashboard",
            priority="medium",
            steps=["Query the dashboard on an empty database"],
            preconditions=["The database has no analyses yet (this test must run first)"],
            action={
                "type": "api", "method": "GET", "path": "/api/dashboard", "fixture": None, "form": None,
                "expect": {"status": 200, "json_field_values": {"total_analyses": 0}},
            },
        )

    # --- Functional: one case per analysis type + one per image source ---

    def _functional_cases(self):
        cases = []
        for analysis_type in ANALYSIS_TYPES:
            cases.append(self._new_case(
                name=f"Run {analysis_type} analysis on a valid image",
                category="functional",
                priority="high",
                steps=[
                    "Upload a valid JPG image",
                    f"Select analysis type: {analysis_type}",
                    "Submit the analysis",
                ],
                action={
                    "type": "api",
                    "method": "POST",
                    "path": "/api/analysis",
                    "fixture": "valid_jpeg",
                    "form": {**DEFAULT_FORM, "analysis_type": analysis_type, "image_source": "drone"},
                    "expect": {"status": 201, "json_fields": ["id", "status", "result"]},
                },
            ))

        for image_source in IMAGE_SOURCES:
            cases.append(self._new_case(
                name=f"Submit an analysis with image source: {image_source}",
                category="functional",
                priority="medium",
                steps=[f"Submit a valid analysis with image_source={image_source}"],
                action={
                    "type": "api",
                    "method": "POST",
                    "path": "/api/analysis",
                    "fixture": "valid_jpeg",
                    "form": {**DEFAULT_FORM, "analysis_type": "classification", "image_source": image_source},
                    "expect": {"status": 201},
                },
            ))

        # Not derivable from config - these describe user-facing flows.
        # "flow" is a symbolic name the UI Executor looks up and runs as a
        # small procedure - these cover several steps, not one request.
        cases += [
            self._new_case(
                name="Display the analysis result after a successful run",
                category="functional",
                priority="high",
                steps=["Run a valid analysis", "Check that the result card appears with data"],
                action={"type": "ui", "flow": "display_result"},
            ),
            self._new_case(
                name="Open the dashboard",
                category="functional",
                priority="medium",
                steps=["Click the Dashboard link in the nav bar"],
                action={"type": "ui", "flow": "open_dashboard"},
            ),
            self._new_case(
                name="Review a previous analysis from the dashboard",
                category="functional",
                priority="medium",
                steps=["Open the dashboard", "Click a row in the recent analyses table"],
                action={"type": "ui", "flow": "review_previous_analysis"},
            ),
        ]
        return cases

    # --- Negative: derived from the actual file-validation limits ---

    def _negative_cases(self):
        unsupported_type = "text/plain"
        assert unsupported_type not in ALLOWED_CONTENT_TYPES

        valid_form = {**DEFAULT_FORM, "analysis_type": "classification", "image_source": "drone"}

        return [
            self._new_case(
                name="Upload a non-image file",
                category="negative",
                priority="high",
                steps=[f"Submit an analysis with a {unsupported_type} file"],
                action={
                    "type": "api", "method": "POST", "path": "/api/analysis",
                    "fixture": "text_file_renamed_jpg", "form": valid_form,
                    "expect": {"status": 400},
                },
            ),
            self._new_case(
                name="Upload a corrupted image",
                category="negative",
                priority="high",
                steps=["Submit an analysis with truncated/broken image bytes"],
                action={
                    "type": "api", "method": "POST", "path": "/api/analysis",
                    "fixture": "corrupted_image", "form": valid_form,
                    "expect": {"status": 400},
                },
            ),
            self._new_case(
                name="Upload an oversized file",
                category="negative",
                priority="high",
                steps=[f"Submit a file larger than {MAX_FILE_SIZE_BYTES} bytes"],
                action={
                    "type": "api", "method": "POST", "path": "/api/analysis",
                    "fixture": "oversized_file", "form": valid_form,
                    "expect": {"status": 400},
                },
            ),
            self._new_case(
                name="Submit missing required fields",
                category="negative",
                priority="high",
                steps=["Submit an analysis request with site_name omitted"],
                action={
                    "type": "api", "method": "POST", "path": "/api/analysis",
                    "fixture": "valid_jpeg",
                    "form": {"analysis_type": "classification", "image_source": "drone"},  # site_name omitted
                    "expect": {"status": 422},
                },
            ),
            self._new_case(
                name="Request analysis without an image",
                category="negative",
                priority="high",
                steps=["Submit an analysis request with no file attached"],
                action={
                    "type": "api", "method": "POST", "path": "/api/analysis",
                    "fixture": None, "form": valid_form,
                    "expect": {"status": 422},
                },
            ),
            self._new_case(
                name="Submit an unsupported analysis_type value",
                category="negative",
                priority="medium",
                steps=["Submit an analysis with analysis_type=spaceship"],
                action={
                    "type": "api", "method": "POST", "path": "/api/analysis",
                    "fixture": "valid_jpeg",
                    "form": {**DEFAULT_FORM, "analysis_type": "spaceship", "image_source": "drone"},
                    "expect": {"status": 422},
                },
            ),
        ]

    # --- API: one case per entry in the endpoint contract ---

    def _api_cases(self):
        cases = [
            self._new_case(
                name=entry["description"],
                category="api",
                priority="high",
                steps=[f"{entry['method']} {entry['path']}"],
                action={
                    "type": "api",
                    "method": entry["method"],
                    "path": entry["path"],
                    "fixture": "valid_jpeg" if entry["method"] == "POST" else None,
                    "form": {**DEFAULT_FORM, "analysis_type": "classification", "image_source": "drone"}
                            if entry["method"] == "POST" else None,
                    "expect": {"status": entry["expected_status"], "json_fields": entry["required_response_fields"]},
                },
            )
            for entry in API_CONTRACT
        ]

        # Not derivable from static config - needs a live simulated failure.
        # How to actually simulate these is unresolved - flagged for Step 9.
        cases += [
            self._new_case(
                name="Validate timeout behavior",
                category="api",
                priority="low",
                steps=["Submit an analysis while the backend is unresponsive"],
                action={"type": "api", "flow": "simulate_timeout", "expect": {"status": 504}},
            ),
            self._new_case(
                name="Validate algorithm-service failure handling",
                category="api",
                priority="medium",
                steps=["Trigger an analyzer failure", "Confirm the analysis is saved with status=failed"],
                action={"type": "api", "flow": "simulate_analyzer_failure",
                        "expect": {"status": "failed", "error_message_present": True}},
            ),
        ]
        return cases

    # --- Dashboard: explicit, per spec section 10 ---

    def _dashboard_cases(self):
        return [
            self._new_case(
                name="Dashboard analysis count updates after a new analysis",
                category="dashboard",
                priority="high",
                steps=["Note total_analyses", "Run one analysis", "Check total_analyses increased by 1"],
                action={"type": "api", "flow": "count_increases_after_analysis"},
            ),
            self._new_case(
                name="Failed analysis is visible on the dashboard",
                category="dashboard",
                priority="high",
                steps=["Cause an analysis to fail", "Check it appears in failed_analyses"],
                action={"type": "api", "flow": "failed_analysis_visible"},
            ),
            self._new_case(
                name="Average processing time is calculated correctly",
                category="dashboard",
                priority="medium",
                steps=["Run a few analyses", "Compare average_processing_time_ms to a manual average"],
                action={"type": "api", "flow": "average_processing_time_matches"},
            ),
            self._new_case(
                name="Dashboard supports filtering and sorting",
                category="dashboard",
                priority="medium",
                steps=["Open the dashboard", "Try to filter or sort the analyses table"],
                action={"type": "ui", "flow": "dashboard_filters"},
            ),
        ]

    # --- AI/algorithm: explicit, per spec section 10 ---

    def _ai_algorithm_cases(self):
        return [
            self._new_case(
                name="Vehicle detection with no relevant objects",
                category="ai_algorithm",
                priority="medium",
                steps=["Run vehicle_detection until a result with total_count=0 occurs"],
                action={"type": "api", "flow": "vehicle_detection_zero_count"},
            ),
            self._new_case(
                name="Vehicle detection with several vehicles",
                category="ai_algorithm",
                priority="medium",
                steps=["Run vehicle_detection until a result with total_count>3 occurs"],
                action={"type": "api", "flow": "vehicle_detection_several"},
            ),
            self._new_case(
                name="Image quality flags a dark or blurred image",
                category="ai_algorithm",
                priority="high",
                steps=["Run image_quality on a deliberately dark/blurred image"],
                action={
                    "type": "api", "method": "POST", "path": "/api/analysis",
                    "fixture": "dark_image",
                    "form": {**DEFAULT_FORM, "analysis_type": "image_quality", "image_source": "drone"},
                    "expect": {"json_fields": ["result"]},
                },
            ),
            self._new_case(
                name="Classification returns 'unclassified' for an unsupported scene",
                category="ai_algorithm",
                priority="medium",
                steps=["Run classification until a result with category=unclassified occurs"],
                action={"type": "api", "flow": "classification_unclassified"},
            ),
            self._new_case(
                name="Classification returns a low-confidence result",
                category="ai_algorithm",
                priority="medium",
                steps=["Run classification until a result with confidence<0.6 occurs"],
                action={"type": "api", "flow": "classification_low_confidence"},
            ),
            self._new_case(
                name="Same image submitted twice gives the same result",
                category="ai_algorithm",
                priority="high",
                steps=["Submit the same image twice with the same analysis_type", "Compare the two results"],
                action={"type": "api", "flow": "determinism_check"},
            ),
        ]
