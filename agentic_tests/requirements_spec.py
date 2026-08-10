"""
Defines the expected API endpoints according to the assignment specification.

This file is intentionally independent from the backend implementation.
The automated tests use this contract to verify that the API behaves as
required, rather than relying on backend code that may contain bugs
"""

# Expected behavior of every public API endpoint
API_CONTRACT = [
    {
        "endpoint_id": "health-check",
        "method": "GET",
        "path": "/api/health",
        "description": "Liveness check",
        "expected_status": 200,
        "required_response_fields": ["status"],
    },
    {
        "endpoint_id": "create-analysis",
        "method": "POST",
        "path": "/api/analysis",
        "description": "Create a new analysis from an uploaded image",
        "expected_status": 201,
        "required_response_fields": ["id", "status", "result"],
    },
    {
        "endpoint_id": "list-analyses",
        "method": "GET",
        "path": "/api/analysis",
        "description": "List all analyses",
        "expected_status": 200,
        # Empty because the response is a JSON array
        "required_response_fields": [],  
    },
    {
        "endpoint_id": "get-analysis",
        "method": "GET",
        "path": "/api/analysis/{id}",
        "description": "Retrieve a single analysis by id",
        "expected_status": 200,
        "required_response_fields": ["id", "status"],
    },
    {
        "endpoint_id": "get-analysis-not-found",
        "method": "GET",
        "path": "/api/analysis/{id}",
        "description": "Retrieve a nonexistent analysis id",
        "expected_status": 404,
        "required_response_fields": ["detail"],
    },
    {
        "endpoint_id": "get-dashboard",
        "method": "GET",
        "path": "/api/dashboard",
        "description": "Aggregated dashboard statistics",
        "expected_status": 200,
        "required_response_fields": ["total_analyses", "by_analysis_type", "recent_analyses"],
    },
]
