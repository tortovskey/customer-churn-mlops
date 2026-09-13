from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.ml_schema import MLDashboardResponse, MLLogRead, ModelMetrics, ModelVersionResponse, TrainResponse
from app.services.ml_service import ml_service

router = APIRouter(prefix="/ml", tags=["mlops"])


@router.post("/train", response_model=TrainResponse)
def train_model(db: Session = Depends(get_db)):
    return ml_service.train(db)


@router.get("/metrics", response_model=ModelMetrics | None)
def get_model_metrics(db: Session = Depends(get_db)):
    return ml_service.get_metrics(db)


@router.get("/version", response_model=ModelVersionResponse)
def get_model_version(db: Session = Depends(get_db)):
    return ml_service.get_version(db)


@router.get("/logs", response_model=list[MLLogRead])
def get_ml_logs(db: Session = Depends(get_db), limit: int = 20):
    return ml_service.get_latest_logs(db, limit=limit)


@router.get("/dashboard", response_model=MLDashboardResponse)
def get_ml_dashboard(db: Session = Depends(get_db)):
    return {
        "version": ml_service.get_version(db),
        "metrics": ml_service.get_metrics(db),
        "logs": ml_service.get_latest_logs(db, limit=20),
    }

