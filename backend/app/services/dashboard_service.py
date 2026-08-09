from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Analysis

RECENT_ANALYSES_LIMIT = 5


def get_dashboard_data(db: Session) -> dict:
    """Aggregation queries for GET /api/dashboard. Averages naturally skip
    NULLs (SQL AVG semantics): processing_time_ms is only set on completed
    analyses, confidence_score only on classification results — so no
    extra filtering is needed for either average to be meaningful."""

    total_analyses = db.query(func.count(Analysis.id)).scalar()

    total_detections = db.query(
        func.coalesce(func.sum(Analysis.detections_count), 0)
    ).scalar()

    by_analysis_type = dict(
        db.query(Analysis.analysis_type, func.count(Analysis.id))
        .group_by(Analysis.analysis_type)
        .all()
    )

    by_category = dict(
        db.query(Analysis.primary_category, func.count(Analysis.id))
        .filter(Analysis.primary_category.isnot(None))
        .group_by(Analysis.primary_category)
        .all()
    )

    recent_analyses = (
        db.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .limit(RECENT_ANALYSES_LIMIT)
        .all()
    )

    failed_analyses = (
        db.query(Analysis)
        .filter(Analysis.status == "failed")
        .order_by(Analysis.created_at.desc())
        .all()
    )

    avg_processing_time = db.query(func.avg(Analysis.processing_time_ms)).scalar()
    avg_confidence = db.query(func.avg(Analysis.confidence_score)).scalar()

    return {
        "total_analyses": total_analyses,
        "total_images": total_analyses,  # one image per analysis in this model
        "total_detections": total_detections,
        "by_analysis_type": by_analysis_type,
        "by_category": by_category,
        "recent_analyses": recent_analyses,
        "failed_analyses": failed_analyses,
        "average_processing_time_ms": round(avg_processing_time, 2) if avg_processing_time is not None else None,
        "average_confidence_score": round(avg_confidence, 2) if avg_confidence is not None else None,
    }
