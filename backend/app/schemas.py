from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict

from app.config import ANALYSIS_STATUSES, ANALYSIS_TYPES, IMAGE_SOURCES

AnalysisType = Literal[ANALYSIS_TYPES]
ImageSource = Literal[IMAGE_SOURCES]
AnalysisStatus = Literal[ANALYSIS_STATUSES]


class AnalysisCreateRequest(BaseModel):
    # Fields required to create a new analysis
    site_name: str
    capture_datetime: datetime
    image_source: ImageSource
    analysis_type: AnalysisType


class AnalysisResponse(BaseModel):
    # Fields returned in the API response for an analysis
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

    site_name: str
    capture_datetime: datetime
    image_source: str
    analysis_type: str

    original_filename: str
    file_size_bytes: int
    content_type: str

    status: AnalysisStatus
    error_message: Optional[str] = None

    result: Optional[dict[str, Any]] = None
    primary_category: Optional[str] = None
    confidence_score: Optional[float] = None
    detections_count: Optional[int] = None
    processing_time_ms: Optional[int] = None


class DashboardResponse(BaseModel):
    # Aggregated statistics displayed on the dashboard
    total_analyses: int
    total_images: int
    total_detections: int

    by_analysis_type: dict[str, int]
    by_category: dict[str, int]

    recent_analyses: list[AnalysisResponse]
    failed_analyses: list[AnalysisResponse]

    average_processing_time_ms: Optional[float] = None
    average_confidence_score: Optional[float] = None
