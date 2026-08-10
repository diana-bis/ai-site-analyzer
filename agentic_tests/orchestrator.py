"""
Runs every test case, one by one. A single failure never stops the rest -
each test case is wrapped in its own try/except
"""


class Orchestrator:
    def __init__(self, planner, execution_agent, validation_agent):
        self.planner = planner
        self.execution_agent = execution_agent
        self.validation_agent = validation_agent

    def run(self):
        test_cases = self.planner.generate_test_cases()
        results = []

        for test_case in test_cases:
            try:
                execution_result = self.execution_agent.run(test_case)
                validation_result = self.validation_agent.validate(test_case, execution_result)
                results.append({
                    "test_case_id": test_case["id"],
                    "name": test_case["name"],
                    "status": validation_result["status"],
                    "actual_result": execution_result,
                    "validation": validation_result,
                })
            except Exception as error:
                results.append({
                    "test_case_id": test_case["id"],
                    "name": test_case["name"],
                    "status": "blocked",
                    "error": str(error),
                })

        return results
