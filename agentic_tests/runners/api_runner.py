"""
Executes one "api" action for real - sends an actual HTTP request to the
running backend and reports back what happened. Never touches backend
code directly, only talks to it over the network, same as any real client.
"""

import requests

from fixtures import build_fixture

# Used for "should return 404" cases - no analysis will ever have this id.
PLACEHOLDER_ANALYSIS_ID = 999999


class ApiRunner:
    def __init__(self, base_url):
        self.base_url = base_url

    def run(self, action):
        if "flow" not in action:
            return self._run_direct(action)

        # Flow-based actions (retry-until, before/after comparisons, etc.)
        # aren't implemented yet - raising here lets the Orchestrator
        # report this as "blocked" instead of silently skipping it.
        raise NotImplementedError(f"API flow '{action['flow']}' is not implemented yet")

    # Send one HTTP request and return its status code and response body
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

        return {"status": response.status_code, "body": body}

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
        real_id = self._create_real_analysis()
        return path.replace("{id}", str(real_id))

    # Create a temporary analysis and return its ID for tests that need an existing record
    def _create_real_analysis(self):
        file_bytes, content_type, filename = build_fixture("valid_jpeg")
        response = requests.post(
            f"{self.base_url}/api/analysis",
            data={
                "site_name": "Setup Fixture",
                "capture_datetime": "2026-01-01T00:00:00",
                "image_source": "drone",
                "analysis_type": "classification",
            },
            files={"file": (filename, file_bytes, content_type)},
        )
        return response.json()["id"]
