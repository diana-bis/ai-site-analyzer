"""
Hand-written procedures for UI test cases. Each drives a real browser page
via Playwright against the running frontend - these test what a user
actually sees and can click, not just what an API response contains.
"""

import tempfile
from pathlib import Path

import requests

from fixtures import build_fixture


def _seed_analysis(runner):
    # Creates a real analysis via the real API - not through the UI - so
    # tests that need "a previous analysis to exist" don't also depend on
    # the Upload page working correctly.
    file_bytes, content_type, filename = build_fixture("valid_jpeg")
    response = requests.post(
        f"{runner.backend_url}/api/analysis",
        data={
            "site_name": "UI Seed",
            "capture_datetime": "2026-01-01T00:00:00",
            "image_source": "drone",
            "analysis_type": "classification",
        },
        files={"file": (filename, file_bytes, content_type)},
    )
    return response.json()["id"]


def open_dashboard(runner, page):
    # Seed a previous analysis so the dashboard has something to show, instead of being empty
    _seed_analysis(runner)

    page.goto(runner.frontend_url)
    page.get_by_role("link", name="Dashboard").click()
    page.wait_for_url(f"{runner.frontend_url}/dashboard")

    # Wait for the dashboard page to load
    heading = page.get_by_role("heading", name="Dashboard")
    try:
        heading.wait_for(state="visible", timeout=10000)
        page_loaded = True
    except Exception:
        page_loaded = False

    return {"status": 200, "body": {"page_loaded": page_loaded}}


def display_result(runner, page):
    file_bytes, _, _ = build_fixture("valid_jpeg")
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(file_bytes)
        temp_path = f.name

    try:
        page.goto(runner.frontend_url)
        page.get_by_label("Site Name").fill("UI Test Site")
        page.get_by_label("Capture Date & Time").fill("2026-01-01T10:00")
        page.get_by_label("Image Source").click()
        page.get_by_role("option", name="Drone").click()
        page.get_by_label("Analysis Type").click()
        page.get_by_role("option", name="Image Classification").click()
        page.set_input_files('input[type="file"]', temp_path)
        page.get_by_role("button", name="Run Analysis").click()

        page.wait_for_selector("text=Analyze another", timeout=10000)
        result_visible = page.get_by_role("button", name="Analyze another").is_visible()
    finally:
        Path(temp_path).unlink()

    return {"status": 200, "body": {"result_visible": result_visible}}


def review_previous_analysis(runner, page):
    _seed_analysis(runner)

    page.goto(f"{runner.frontend_url}/dashboard")
    page.wait_for_selector("table")
    # Click the first row in the table to navigate to the analysis details page
    page.locator("table tbody tr").first.click()
    page.wait_for_url(lambda url: "/analysis/" in url, timeout=10000)

    return {"status": 200, "body": {"navigated_to_details": "/analysis/" in page.url}}


def dashboard_filters(runner, page):
    _seed_analysis(runner)

    page.goto(f"{runner.frontend_url}/dashboard")
    page.wait_for_selector("table")

    # No filter/sort controls exist anywhere on the dashboard today - this
    # genuinely checks for their absence, it is not rigged to fail.
    filter_controls_present = page.locator(
        'input[placeholder*="filter" i], input[placeholder*="search" i], '
        'button:has-text("Sort"), select'
    ).count() > 0

    return {"status": 200, "body": {"filter_controls_present": filter_controls_present}}
