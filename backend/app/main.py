from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Site Analyzer API",
    description="Analyzes images captured from field sites, cameras and drones.",
    version="0.1.0",
)

# The React dev server runs on a different origin (port 5173), so the browser
# blocks requests unless the API explicitly allows that origin.
# TODO(step 1): move to config.py (pydantic-settings) once it exists.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    """Liveness probe. The agentic test suite calls this before running tests."""
    return {"status": "ok"}
