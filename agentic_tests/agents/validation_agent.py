"""
Compares what a test case expected against what actually happened.
Doesn't run anything itself - just judges the result it's handed.
"""


class ValidationAgent:
    def validate(self, test_case, execution_result):
        expect = test_case["action"].get("expect", {})
        deviations = []
        expected_parts = []
        actual_parts = []

        # Compare the expected and actual results based on the test case's status expectations
        if "status" in expect:
            actual_status = execution_result.get("status")
            expected_parts.append(f"HTTP status {expect['status']}")
            actual_parts.append(f"HTTP status {actual_status}")
            if actual_status != expect["status"]:
                deviations.append(f"expected status {expect['status']}, got {actual_status}")

        # Compare expected JSON fields and their values if specified
        if "json_fields" in expect and expect["json_fields"]:
            body = execution_result.get("body") or {}
            fields = expect["json_fields"]
            missing = [field for field in fields if field not in body]
            expected_parts.append(f"response includes {', '.join(fields)}")
            actual_parts.append(
                "all expected fields present" if not missing
                else f"missing {', '.join(missing)}"
            )
            if missing:
                deviations.append(f"missing response fields: {missing}")

        if "json_field_values" in expect:
            body = execution_result.get("body") or {}
            values = expect["json_field_values"]
            expected_parts.append(
                "; ".join(f"{field}={value!r}" for field, value in values.items())
            )
            actual_parts.append(
                "; ".join(f"{field}={body.get(field)!r}" for field in values)
            )
            for field, expected_value in values.items():
                actual_value = body.get(field)
                if actual_value != expected_value:
                    deviations.append(
                        f"expected {field}={expected_value!r}, got {actual_value!r}"
                    )

        return {
            "status": "passed" if not deviations else "failed",
            "deviations": deviations,
            "expected_result": "; ".join(expected_parts) or "No specific checks defined.",
            "actual_result": "; ".join(actual_parts) or "No response data.",
        }
