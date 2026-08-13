"""
Executes one "api" action for real - sends an actual HTTP request to the
running backend and reports back what happened. Never touches backend
code directly, only talks to it over the network, same as any real client.

Test cases that need more than one request live in api_flows.py
"""

import json

import requests

from fixtures import build_fixture
from runners import api_flows

# Used for "should return 404" cases - no analysis will ever have this id.
PLACEHOLDER_ANALYSIS_ID = 999999

# Sane cap so a huge JSON body doesn't bloat the report.
MAX_LOG_BODY_LENGTH = 2000


def build_evidence(method, path, form, response_status, response_body):
    """Compact, human-readable log entry for one HTTP request/response -
    what was sent, what came back. Shared by _run_direct and the flows in
    api_flows.py, so every "failed without raising" case leaves the same
    kind of evidence behind (spec section 12: "logs where relevant"), not
    just genuine crashes."""
    body_text = json.dumps(response_body) if response_body is not None else "null"
    if len(body_text) > MAX_LOG_BODY_LENGTH:
        body_text = body_text[:MAX_LOG_BODY_LENGTH] + "... (truncated)"

    request_text = f"{method} {path}"
    if form:
        request_text += f" form={form}"

    return f"Request: {request_text}\nResponse status: {response_status}\nResponse body: {body_text}"


class ApiRunner:
    def __init__(self, base_url):
        self.base_url = base_url
        self._flows = {
            "failed_analysis_visible": api_flows.failed_analysis_visible,
            "missing_image_file_handling": api_flows.missing_image_file_handling,
            "count_increases_after_analysis": api_flows.count_increases_after_analysis,
            "average_processing_time_matches": api_flows.average_processing_time_matches,
            "determinism_check": api_flows.determinism_check,
        }

    def run(self, action):
        if "flow" not in action:
            return self._run_direct(action)

        handler = self._flows.get(action["flow"])
        if handler is None:
            # Not implemented yet - raising lets the Orchestrator report
            # this as "blocked" instead of silently skipping it.
            raise NotImplementedError(f"API flow '{action['flow']}' is not implemented yet")
        return handler(self)

    # Send one HTTP request and return its status code, body, and evidence
    def _run_direct(self, action):
        path = self._resolve_path(action)
        url = f"{self.base_url}{path}"

        files = None
        if action.get("fixture"):
            file_bytes, content_type, filename = build_fixture(action["fixture"])
            files = {"file": (filename, file_bytes, content_type)}

        response = requests.request(
            action["method"],
            url,
            data=action.get("form"),
            files=files,
        )

        try:
            body = response.json()
        except ValueError:
            body = None

        return {
            "status": response.status_code,
            "body": body,
            "logs": build_evidence(
                action["method"], path, action.get("form"), response.status_code, body
            ),
        }

    # Replace {id} in the URL with either a real analysis ID or a fake one for 404 tests
    def _resolve_path(self, action):
        path = action["path"]
        if "{id}" not in path:
            return path

        expected_status = action.get("expect", {}).get("status")
        if expected_status == 404:
            return path.replace("{id}", str(PLACEHOLDER_ANALYSIS_ID))

        # This test needs a real analysis to look up - create one first,
        # self-contained, so this test doesn't depend on any other test
        # having already run.
        real_id = self.create_analysis("valid_jpeg", "classification")
        return path.replace("{id}", str(real_id))

    # Create a real analysis and return its id. (Public: used by api_flows.py too)
    def create_analysis(self, fixture_name, analysis_type):
        file_bytes, content_type, filename = build_fixture(fixture_name)
        response = requests.post(
            f"{self.base_url}/api/analysis",
            data={
                "site_name": "Setup Fixture",
                "capture_datetime": "2026-01-01T00:00:00",
                "image_source": "drone",
                "analysis_type": analysis_type,
            },
            files={"file": (filename, file_bytes, content_type)},
        )
        return response.json()["id"]
