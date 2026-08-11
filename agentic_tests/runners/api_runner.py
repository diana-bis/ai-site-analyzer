"""
Executes one "api" action for real - sends an actual HTTP request to the
running backend and reports back what happened. Never touches backend
code directly, only talks to it over the network, same as any real client.

The two flow methods below are the exception: they also touch the disk
directly (backend_link.UPLOADS_DIR), since this test suite runs on the
same host as the backend and the uploaded file is a real external
resource - same reasoning as any test that manipulates a shared file or
database the system under test also uses.
"""

import os

import requests

from backend_link import UPLOADS_DIR
from fixtures import build_fixture

# Used for "should return 404" cases - no analysis will ever have this id.
PLACEHOLDER_ANALYSIS_ID = 999999


class ApiRunner:
    def __init__(self, base_url):
        self.base_url = base_url
        self._flows = {
            "failed_analysis_visible": self._flow_failed_analysis_visible,
            "missing_image_file_handling": self._flow_missing_image_file_handling,
        }

    def run(self, action):
        if "flow" not in action:
            return self._run_direct(action)

        handler = self._flows.get(action["flow"])
        if handler is None:
            # Not implemented yet - raising lets the Orchestrator report
            # this as "blocked" instead of silently skipping it.
            raise NotImplementedError(f"API flow '{action['flow']}' is not implemented yet")
        return handler()

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
        real_id = self._create_analysis("valid_jpeg", "classification")
        return path.replace("{id}", str(real_id))

    # Create a real analysis and return its id
    def _create_analysis(self, fixture_name, analysis_type):
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

    def _flow_failed_analysis_visible(self):
        # Create an analysis that will fail (image_quality analyzer fully decodes the image and will fail on a truncated JPEG)
        failed_id = self._create_analysis("truncated_jpeg_passes_verify", "image_quality")

        dashboard_response = requests.get(f"{self.base_url}/api/dashboard")
        failed_ids = [entry["id"] for entry in dashboard_response.json()["failed_analyses"]]

        return {
            "status": dashboard_response.status_code,
            # Check that the failed analysis appears in the dashboard's failed_analyses list
            "body": {"analysis_visible_in_failed_list": failed_id in failed_ids},
        }

    def _flow_missing_image_file_handling(self):
        # Create an analysis and then delete its uploaded file to simulate a disk failure
        before = set(os.listdir(UPLOADS_DIR))
        analysis_id = self._create_analysis("valid_jpeg", "classification")
        new_files = set(os.listdir(UPLOADS_DIR)) - before

        if len(new_files) != 1:
            raise RuntimeError(f"Expected exactly one new upload file, found {new_files}")

        (UPLOADS_DIR / new_files.pop()).unlink()  # delete the new file to simulate the file being lost

        # Request the missing image
        image_response = requests.get(f"{self.base_url}/api/analysis/{analysis_id}/image")
        return {"status": image_response.status_code, "body": None}
