"""
Compares what a test case expected against what actually happened.
Doesn't run anything itself - just judges the result it's handed.
"""


class ValidationAgent:
    def validate(self, test_case, execution_result):
        expect = test_case["action"].get("expect", {})
        deviations = []

        # Check the status code match
        if "status" in expect:
            actual_status = execution_result.get("status")
            if actual_status != expect["status"]:
                deviations.append(f"expected status {expect['status']}, got {actual_status}")

        # Check for required JSON fields in the response body
        if "json_fields" in expect:
            body = execution_result.get("body") or {}
            missing = [field for field in expect["json_fields"] if field not in body]
            if missing:
                deviations.append(f"missing response fields: {missing}")

        # Check for specific JSON field values in the response body
        if "json_field_values" in expect:
            body = execution_result.get("body") or {}
            for field, expected_value in expect["json_field_values"].items():
                actual_value = body.get(field)
                if actual_value != expected_value:
                    deviations.append(
                        f"expected {field}={expected_value!r}, got {actual_value!r}"
                    )

        return {
            "status": "passed" if not deviations else "failed",
            "deviations": deviations,
        }
