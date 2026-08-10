"""
Dispatches a test case to the right runner based on its action type.
Doesn't know how to actually run anything itself - that's the runners' job.
"""


class ExecutionAgent:
    def __init__(self, api_runner, ui_runner=None):
        self.api_runner = api_runner
        self.ui_runner = ui_runner

    def run(self, test_case):
        action = test_case["action"]

        if action["type"] == "api":
            return self.api_runner.run(action)

        if action["type"] == "ui":
            if self.ui_runner is None:
                raise NotImplementedError("UI runner is not implemented yet")
            return self.ui_runner.run(action)

        raise ValueError(f"Unknown action type: {action['type']}")
