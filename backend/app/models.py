from sqlalchemy import Column, DateTime, Float, Integer, String, JSON
from sqlalchemy.sql import func

from app.database import Base


class Analysis(Base):
    # Database model for an analysis record. Each row corresponds to a single analysis request and its outcome.

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())  # UTC, DB-generated

    # Request metadata
    site_name = Column(String, nullable=False)
    capture_datetime = Column(DateTime, nullable=False)  # user-supplied, stored as given
    image_source = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)

    # Uploaded file (bytes live on disk under settings.uploads_dir, never in the DB)
    stored_filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)

    # Outcome
    status = Column(String, nullable=False)
    error_message = Column(String, nullable=True)

    # Full analyzer output, shape varies per analysis_type
    result = Column(JSON, nullable=True)

    # Duplicated out of `result` so the dashboard can aggregate in SQL
    # instead of looping over rows in Python. Records are write-once, so
    # the duplication cannot drift out of sync with `result`.
    primary_category = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    detections_count = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
