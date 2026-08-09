from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DashboardResponse
from app.services.dashboard_service import get_dashboard_data

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    return get_dashboard_data(db)
