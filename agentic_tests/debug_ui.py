"""
Manually run one UI flow with a visible browser, for debugging selectors.
Requires the backend (:8000) and frontend (:5173) to already be running.

Usage:
    python debug_ui.py <flow_name>

Available flows: display_result, open_dashboard, review_previous_analysis,
dashboard_filters
"""

import os
import sys

os.environ["UI_HEADED"] = "1"

from runners.ui_runner import UiRunner

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_ui.py <flow_name>")
        print("Available: display_result, open_dashboard, review_previous_analysis, dashboard_filters")
        sys.exit(1)

    flow_name = sys.argv[1]
    runner = UiRunner("http://localhost:5173", "http://localhost:8000")
    result = runner.run({"type": "ui", "flow": flow_name})
    print("Result:", result)
