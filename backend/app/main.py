from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 — import needed so Base.metadata knows about Analysis
from app.routers import analysis, dashboard, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.data_dir  # creates backend/data/ if missing
    settings.uploads_dir  # creates backend/data/uploads/ if missing
    Base.metadata.create_all(bind=engine)
    yield
    # Nothing to release on shutdown: SQLite sessions are closed per-request
    # via app.database.get_db(), not held open at the app level.


app = FastAPI(
    title="AI Site Analyzer API",
    description="Analyzes images captured from field sites, cameras and drones.",
    version="0.1.0",
    lifespan=lifespan,
)

# The React dev server runs on a different origin (port 5173), so the browser
# blocks requests unless the API explicitly allows that origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
