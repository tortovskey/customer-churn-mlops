from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.models.ml_log import MLLog
from app.models.prediction import Prediction
from app.services.client_service import get_client
from app.services.ml_service import ml_service


def create_prediction(db: Session, client_id: int) -> tuple[Prediction, dict]:
    client = get_client(db, client_id)
    predictor = ml_service.get_predictor(db)
    output = predictor.predict(client)

    prediction = Prediction(
        client_id=client.id,
        model_version=output.model_version,
        prediction_value=output.probability,
        prediction_label=output.label,
    )
    db.add(prediction)
    db.add(
        MLLog(
            event_type="prediction_created",
            message=f"Prediction for client {client.id} saved",
            details={
                "client_id": client.id,
                "model_version": output.model_version,
                "prediction_value": output.probability,
                "prediction_label": output.label,
            },
        )
    )
    db.commit()
    db.refresh(prediction)
    return prediction, output.explanation


def list_predictions(db: Session) -> list[Prediction]:
    statement = (
        select(Prediction)
        .options(selectinload(Prediction.client))
        .order_by(Prediction.created_at.desc())
    )
    return list(db.scalars(statement).all())


def list_predictions_for_client(db: Session, client_id: int) -> list[Prediction]:
    client = get_client(db, client_id)
    statement = (
        select(Prediction)
        .where(Prediction.client_id == client.id)
        .order_by(Prediction.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_prediction(db: Session, prediction_id: int) -> Prediction:
    prediction = db.get(Prediction, prediction_id)
    if prediction is None:
        raise NotFoundError(f"Prediction {prediction_id} was not found")
    return prediction

