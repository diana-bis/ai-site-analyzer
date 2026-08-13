"""
Executes "ui" actions for real - drives an actual browser via Playwright
against the running frontend. Used for tests that are about what a user
actually sees and can click, not just what an API response contains.
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

from runners import ui_flows

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "screenshots"


class UiRunner:
    def __init__(self, frontend_url, backend_url):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self._flows = {
            "display_result": ui_flows.display_result,
            "open_dashboard": ui_flows.open_dashboard,
            "review_previous_analysis": ui_flows.review_previous_analysis,
            "dashboard_filters": ui_flows.dashboard_filters,
        }

    def run(self, test_id, action):
        handler = self._flows.get(action["flow"])
        if handler is None:
            raise NotImplementedError(f"UI flow '{action['flow']}' is not implemented yet")

        # Set UI_HEADED=1 to watch the browser instead of running invisibly -
        # a debugging convenience, doesn't affect normal/automated runs.
        headed = os.environ.get("UI_HEADED") == "1"

        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        # Working filename, no status yet - UiRunner doesn't know pass/fail,
        # that's ValidationAgent's job. The Orchestrator renames this (or
        # deletes it, for a pass) once it knows the real outcome.
        screenshot_path = SCREENSHOTS_DIR / f"{test_id}.png"

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not headed, slow_mo=800 if headed else 0)
            page = browser.new_page()
            try:
                result = handler(self, page)
                page.screenshot(path=str(screenshot_path))
                if headed:
                    # Opens the Inspector, paused on the final page state -
                    # stays open until you click Resume, so the window
                    # doesn't just flash and close the instant the flow ends.
                    page.pause()
                return result
            except Exception:
                # Capture page state at the moment of failure before
                # re-raising, so a crash still leaves visual evidence behind.
                try:
                    page.screenshot(path=str(screenshot_path))
                except Exception:
                    pass  # the page itself may already be unusable/closed
                raise
            finally:
                browser.close()
