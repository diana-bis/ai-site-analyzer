from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Liveness probe. The agentic test suite calls this before running tests."""
    return {"status": "ok"}
