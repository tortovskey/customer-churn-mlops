from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.prediction_schema import PredictionRead, PredictionResult, PredictionWithClient
from app.services import prediction_service

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/{client_id}", response_model=PredictionResult, status_code=status.HTTP_201_CREATED)
def predict_client_churn(client_id: int, db: Session = Depends(get_db)):
    prediction, explanation = prediction_service.create_prediction(db, client_id)
    return {"prediction": prediction, "explanation": explanation}


@router.get("", response_model=list[PredictionWithClient])
def get_predictions(db: Session = Depends(get_db)) -> list:
    return prediction_service.list_predictions(db)


@router.get("/{client_id}", response_model=list[PredictionRead])
def get_predictions_for_client(client_id: int, db: Session = Depends(get_db)) -> list:
    return prediction_service.list_predictions_for_client(db, client_id)

