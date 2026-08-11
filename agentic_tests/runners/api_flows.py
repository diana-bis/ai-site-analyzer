"""
Hand-written procedures for API test cases that need more than one HTTP
request.

failed_analysis_visible and missing_image_file_handling also touch the
disk directly (backend_link.UPLOADS_DIR), since this test suite runs on
the same host as the backend and the uploaded file is a real external
resource.
"""

import os

import requests

from backend_link import UPLOADS_DIR
from fixtures import build_fixture


def failed_analysis_visible(runner):
    # Create a deliberately failed analysis, then check that it shows up in the dashboard's failed_analyses list.
    failed_id = runner.create_analysis("truncated_jpeg_passes_verify", "image_quality")

    dashboard_response = requests.get(f"{runner.base_url}/api/dashboard")
    failed_ids = [entry["id"] for entry in dashboard_response.json()["failed_analyses"]]

    return {
        "status": dashboard_response.status_code,
        "body": {"analysis_visible_in_failed_list": failed_id in failed_ids},
    }


def missing_image_file_handling(runner):
    # Snapshot the uploads folder before/after creating one analysis to find the exact file it just saved
    before = set(os.listdir(UPLOADS_DIR))
    analysis_id = runner.create_analysis("valid_jpeg", "classification")
    new_files = set(os.listdir(UPLOADS_DIR)) - before

    if len(new_files) != 1:
        raise RuntimeError(f"Expected exactly one new upload file, found {new_files}")

    (UPLOADS_DIR / new_files.pop()).unlink()  # simulate the file being lost

    image_response = requests.get(f"{runner.base_url}/api/analysis/{analysis_id}/image")
    return {"status": image_response.status_code, "body": None}


def count_increases_after_analysis(runner):
    before = requests.get(f"{runner.base_url}/api/dashboard").json()["total_analyses"]
    runner.create_analysis("valid_jpeg", "classification")
    after = requests.get(f"{runner.base_url}/api/dashboard").json()

    return {
        "status": 200,
        "body": {"count_increased_by_one": after["total_analyses"] == before + 1},
    }


def average_processing_time_matches(runner):
    all_analyses = requests.get(f"{runner.base_url}/api/analysis").json()
    times = [a["processing_time_ms"] for a in all_analyses if a["processing_time_ms"] is not None]
    manual_average = round(sum(times) / len(times), 2) if times else None

    dashboard = requests.get(f"{runner.base_url}/api/dashboard").json()

    return {
        "status": 200,
        "body": {"averages_match": manual_average == dashboard["average_processing_time_ms"]},
    }


def determinism_check(runner):
    file_bytes, content_type, filename = build_fixture("valid_jpeg")
    form = {
        "site_name": "Determinism Fixture",
        "capture_datetime": "2026-01-01T00:00:00",
        "image_source": "drone",
        "analysis_type": "classification",
    }

    result_1 = requests.post(
        f"{runner.base_url}/api/analysis", data=form,
        files={"file": (filename, file_bytes, content_type)},
    ).json()["result"]
    result_2 = requests.post(
        f"{runner.base_url}/api/analysis", data=form,
        files={"file": (filename, file_bytes, content_type)},
    ).json()["result"]

    # processing_time_ms is not part of the determinism guarantee comparing it
    # would make this fail almost every run for a reason that isn't a bug.
    deterministic_fields = ("category", "confidence", "alternatives")
    results_match = all(result_1[field] == result_2[field] for field in deterministic_fields)

    return {"status": 200, "body": {"results_match": results_match}}
