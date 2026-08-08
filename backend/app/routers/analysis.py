from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis
from app.schemas import AnalysisResponse, AnalysisType, ImageSource
from app.services.analysis_service import run_analysis
from app.services.file_validation import FileValidationError

router = APIRouter()

# Create a new analysis from an uploaded image
@router.post("/analysis", response_model=AnalysisResponse, status_code=201)
def create_analysis(
    site_name: str = Form(...),
    capture_datetime: datetime = Form(...),
    image_source: ImageSource = Form(...),
    analysis_type: AnalysisType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_bytes = file.file.read()

    try:
        return run_analysis(
            db=db,
            site_name=site_name,
            capture_datetime=capture_datetime,
            image_source=image_source,
            analysis_type=analysis_type,
            filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes,
        )
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# Return all analyses ordered from newest to oldest
@router.get("/analysis", response_model=list[AnalysisResponse])
def list_analyses(db: Session = Depends(get_db)):
    return db.query(Analysis).order_by(Analysis.created_at.desc()).all()

# Return a single analysis by its ID
@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found.")
    return analysis
