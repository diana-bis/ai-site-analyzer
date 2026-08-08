import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.analyzers.registry import get_analyzer
from app.config import settings
from app.models import Analysis
from app.services.file_validation import validate_image_file


def _extract_dashboard_fields(analysis_type: str, result: dict) -> dict:
    """Extract the fields that the dashboard stores separately for
    filtering, aggregation, and reporting."""
    fields = {"processing_time_ms": result.get("processing_time_ms")}

    if analysis_type == "classification":
        fields["primary_category"] = result.get("category")
        fields["confidence_score"] = result.get("confidence")
    elif analysis_type == "vehicle_detection":
        fields["detections_count"] = result.get("total_count")
    elif analysis_type == "image_quality":
        fields["primary_category"] = result.get("quality")

    return fields


def run_analysis(
    db: Session,
    site_name: str,
    capture_datetime: datetime,
    image_source: str,
    analysis_type: str,
    filename: str,
    content_type: str,
    file_bytes: bytes,
) -> Analysis:
    """Complete analysis workflow:
    validate -> save image -> analyze -> store results.
    """
    # Validate the uploaded file before processing
    validate_image_file(content_type, file_bytes)  # raises FileValidationError

    # Generate a unique filename to avoid collisions
    extension = Path(filename or "").suffix
    stored_filename = f"{uuid.uuid4().hex}{extension}"
    # Save the uploaded image to disk
    stored_path = settings.uploads_dir / stored_filename
    stored_path.write_bytes(file_bytes)

    # Create the database record
    analysis = Analysis(
        site_name=site_name,
        capture_datetime=capture_datetime,
        image_source=image_source,
        analysis_type=analysis_type,
        stored_filename=stored_filename,
        original_filename=filename or stored_filename,
        file_size_bytes=len(file_bytes),
        content_type=content_type,
    )
    # Select the requested analyzer.
    analyzer = get_analyzer(analysis_type)  

    try:
        result = analyzer.analyze(stored_path)
    except Exception as exc:
        # Store the failure so it appears in the dashboard
        analysis.status = "failed"
        analysis.error_message = str(exc)
    else:
        # Store the successful analysis results
        analysis.status = "completed"
        analysis.result = result
        for key, value in _extract_dashboard_fields(analysis_type, result).items():
            setattr(analysis, key, value)

    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
