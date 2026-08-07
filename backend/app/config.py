from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Single source of truth for allowed field values. Storage (models.py) uses
# plain strings; Step 3's Pydantic schemas import these to build Literal
# types, so validation happens at the API layer with a proper 422, not as
# a DB-level CHECK constraint that would need the DB file deleted to change.
ANALYSIS_TYPES = ("classification", "vehicle_detection", "image_quality")
IMAGE_SOURCES = ("static_camera", "drone", "manual_upload")
ANALYSIS_STATUSES = ("completed", "failed")


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:5173"
    db_filename: str = "analyzer.db"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def data_dir(self) -> Path:
        # Anchored to this file's location, not the process cwd, so paths
        # are the same regardless of where uvicorn is launched from.
        data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.data_dir / self.db_filename}"

    @property
    def uploads_dir(self) -> Path:
        uploads_dir = self.data_dir / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        return uploads_dir


settings = Settings()
