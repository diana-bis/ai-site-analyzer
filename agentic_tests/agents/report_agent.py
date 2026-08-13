"""
Aggregates all test results into the final report 
"""

import html
import json

KNOWN_LIMITATIONS = [
    "Validate timeout behavior (TC-023) is permanently blocked - client-side timeout, out of scope.",
    "Dashboard filtering/sorting (TC-029) is a known, real gap in the frontend.",
    "classification and vehicle_detection are deterministic mocks, not real ML models. "
    "Only image_quality runs a real algorithm.",
    "'cause' text and the narrative summary come from a mock LLM, swappable via LLM_PROVIDER.",
]


class ReportAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate(self, results, coverage):
        report = self._aggregate(results, coverage)
        report["narrative"] = self._generate_narrative(report)
        return report

    def to_json(self, report):
        return json.dumps(report, indent=2)

    def to_html(self, report):
        return self._render_html(report)

    def _aggregate(self, results, coverage):
        total = len(results)
        passed = sum(1 for r in results if r["status"] == "passed")
        failures = [r for r in results if r["status"] == "failed"]
        blocked = sum(1 for r in results if r["status"] == "blocked")

        by_severity, by_component = {}, {}
        for f in failures:
            severity = f.get("severity", "unknown")
            component = f.get("suggested_fix", {}).get("component", "unknown")
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_component[component] = by_component.get(component, 0) + 1

        slowest = sorted(results, key=lambda r: r["duration_ms"], reverse=True)[:5]

        return {
            "total": total,
            "passed": passed,
            "failed": len(failures),
            "blocked": blocked,
            "pass_rate": round(passed / total * 100, 1) if total else 0.0,
            "results": results,
            "failures": failures,
            "by_severity": by_severity,
            "by_component": by_component,
            "slowest": [
                {"id": r["test_case_id"], "name": r["name"], "duration_ms": r["duration_ms"]}
                for r in slowest
            ],
            "coverage": coverage,
            "known_limitations": KNOWN_LIMITATIONS,
        }

    def _generate_narrative(self, report):
        if not report["failures"]:
            return None

        try:
            narrative = self.llm_client.complete(self._build_narrative_prompt(report))
        except Exception:
            narrative = None
        return narrative or None

    def _build_narrative_prompt(self, report):
        lines = [
            f"{f['test_case_id']} ({f.get('suggested_fix', {}).get('component', 'unknown')}, "
            f"severity={f.get('severity', 'unknown')}): {f['error_message']}"
            for f in report["failures"]
        ]
        return (
            "The following test failures occurred in one automated test run:\n"
            + "\n".join(lines)
            + "\n\nSummarize what these failures mean together (shared component, "
            "likely common cause, whether this looks like a regression or a gap), "
            "and suggest what regression testing should follow once fixed."
        )

    def _render_html(self, report):
        def esc(value):
            return html.escape(str(value)) if value is not None else ""

        rows = "".join(
            f"<tr class='{r['status']}'><td>{esc(r['test_case_id'])}</td><td>{esc(r['name'])}</td>"
            f"<td>{esc(r['status'])}</td><td>{esc(r['duration_ms'])}ms</td></tr>"
            for r in report["results"]
        )

        failure_cards = "".join(
            f"""<div class="failure-card">
<h3>{esc(f['test_case_id'])} - {esc(f['name'])} <span class="severity {esc(f.get('severity'))}">{esc(f.get('severity'))}</span></h3>
<p><strong>Expected:</strong> {esc(f['expected_result'])}</p>
<p><strong>Actual:</strong> {esc(f['actual_result'])}</p>
{f'<img src="{esc(f["screenshot"][len("artifacts/"):])}" class="screenshot">' if f.get('screenshot') else ''}
<p><strong>Component:</strong> {esc(f.get('suggested_fix', {}).get('component'))}</p>
<p><strong>Cause:</strong> {esc(f.get('suggested_fix', {}).get('cause'))}</p>
<p><strong>Recommendation:</strong> {esc(f.get('suggested_fix', {}).get('recommendation'))}</p>
<p><strong>Regression test:</strong> {esc(f.get('suggested_fix', {}).get('regression_test'))}</p>
</div>"""
            for f in report["failures"]
        )

        severity_rows = "".join(
            f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in report["by_severity"].items()
        )
        component_rows = "".join(
            f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in report["by_component"].items()
        )
        slowest_rows = "".join(
            f"<tr><td>{esc(s['id'])}</td><td>{esc(s['name'])}</td><td>{esc(s['duration_ms'])}ms</td></tr>"
            for s in report["slowest"]
        )
        coverage_rows = "".join(
            f"<tr><td>{esc(cat)}</td><td>{len(ids)}</td><td>{esc(', '.join(ids))}</td></tr>"
            for cat, ids in report["coverage"].items()
        )
        limitations_items = "".join(f"<li>{esc(item)}</li>" for item in report["known_limitations"])

        narrative_html = (
            f"<section class='narrative'><h2>Summary</h2><p>{esc(report['narrative'])}</p></section>"
            if report.get("narrative") else ""
        )

        return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Agentic Test Report</title>
<style>
body {{ font-family: -apple-system, Segoe UI, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
h1, h2, h3 {{ color: #111; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #ddd; font-size: 14px; }}
th {{ background: #f5f5f5; }}
tr.passed td:nth-child(3) {{ color: #1a7f37; font-weight: 600; }}
tr.failed td:nth-child(3) {{ color: #cf222e; font-weight: 600; }}
tr.blocked td:nth-child(3) {{ color: #9a6700; font-weight: 600; }}
.kpis {{ display: flex; gap: 1rem; margin: 1rem 0; }}
.kpi {{ background: #f5f5f5; border-radius: 8px; padding: 1rem; flex: 1; text-align: center; }}
.kpi .value {{ font-size: 1.8rem; font-weight: 700; }}
.narrative {{ background: #eef6ff; border-left: 4px solid #1976d2; padding: 1rem; border-radius: 4px; }}
.failure-card {{ border: 1px solid #eee; border-radius: 8px; padding: 1rem; margin: 1rem 0; background: #fffaf8; }}
.severity {{ font-size: 0.75rem; padding: 2px 8px; border-radius: 10px; color: white; }}
.severity.high {{ background: #cf222e; }}
.severity.medium {{ background: #9a6700; }}
.severity.low {{ background: #57606a; }}
.screenshot {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin: 0.5rem 0; }}
ul {{ padding-left: 1.2rem; }}
</style>
</head>
<body>
<h1>Agentic Test Report</h1>
{narrative_html}
<div class="kpis">
<div class="kpi"><div class="value">{report['total']}</div>Total</div>
<div class="kpi"><div class="value">{report['passed']}</div>Passed</div>
<div class="kpi"><div class="value">{report['failed']}</div>Failed</div>
<div class="kpi"><div class="value">{report['blocked']}</div>Blocked</div>
<div class="kpi"><div class="value">{report['pass_rate']}%</div>Pass rate</div>
</div>
<h2>Results</h2>
<table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Duration</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Failures</h2>
{failure_cards or '<p>No failures.</p>'}
<h2>Defects by Severity</h2>
<table><thead><tr><th>Severity</th><th>Count</th></tr></thead><tbody>{severity_rows or "<tr><td colspan=2>None</td></tr>"}</tbody></table>
<h2>Defects by Component</h2>
<table><thead><tr><th>Component</th><th>Count</th></tr></thead><tbody>{component_rows or "<tr><td colspan=2>None</td></tr>"}</tbody></table>
<h2>Slowest Tests</h2>
<table><thead><tr><th>ID</th><th>Name</th><th>Duration</th></tr></thead><tbody>{slowest_rows}</tbody></table>
<h2>Coverage by Category</h2>
<table><thead><tr><th>Category</th><th>Count</th><th>Test IDs</th></tr></thead><tbody>{coverage_rows}</tbody></table>
<h2>Known Limitations</h2>
<ul>{limitations_items}</ul>
</body></html>"""
