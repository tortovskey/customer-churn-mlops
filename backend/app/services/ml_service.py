from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config.settings import Settings, get_settings
from app.core.exceptions import ModelNotReadyError
from app.core.logger import logger
from app.ml.predict import ChurnPredictor
from app.ml.train_model import train_customer_churn_model
from app.models.ml_log import MLLog
from app.models.model_registry import ModelRegistry


class MLService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._predictor: ChurnPredictor | None = None
        self._predictor_path: str | None = None

    def _log(self, db: Session, event_type: str, message: str, details: dict | None = None) -> None:
        db.add(MLLog(event_type=event_type, message=message, details=details))
        db.commit()

    def get_active_model(self, db: Session) -> ModelRegistry | None:
        statement = (
            select(ModelRegistry)
            .where(ModelRegistry.is_active.is_(True))
            .order_by(ModelRegistry.created_at.desc())
        )
        return db.scalars(statement).first()

    def get_latest_logs(self, db: Session, limit: int = 20) -> list[MLLog]:
        statement = select(MLLog).order_by(MLLog.created_at.desc()).limit(limit)
        return list(db.scalars(statement).all())

    def get_metrics(self, db: Session) -> dict | None:
        active_model = self.get_active_model(db)
        if active_model is not None:
            return active_model.metrics

        latest_path = Path(self.settings.model_storage_dir) / "latest.json"
        if latest_path.exists():
            return json.loads(latest_path.read_text(encoding="utf-8")).get("metrics")
        return None

    def get_version(self, db: Session) -> dict:
        active_model = self.get_active_model(db)
        if active_model is None:
            latest_path = Path(self.settings.model_storage_dir) / "latest.json"
            if latest_path.exists():
                payload = json.loads(latest_path.read_text(encoding="utf-8"))
                return {
                    "model_name": payload.get("model_name", self.settings.model_name),
                    "model_version": payload.get("model_version"),
                    "model_path": payload.get("model_path"),
                    "is_active": False,
                    "created_at": None,
                }
            return {
                "model_name": self.settings.model_name,
                "model_version": None,
                "model_path": None,
                "is_active": False,
                "created_at": None,
            }
        return {
            "model_name": active_model.model_name,
            "model_version": active_model.model_version,
            "model_path": active_model.model_path,
            "is_active": active_model.is_active,
            "created_at": active_model.created_at,
        }

    def train(self, db: Session) -> dict:
        logger.info("Starting customer churn model training")
        try:
            result = train_customer_churn_model(
                self.settings,
                rows=self.settings.training_rows,
                random_state=self.settings.training_random_state,
            )
        except Exception as exc:
            self._log(
                db,
                "training_failed",
                "Model training failed",
                {"error": str(exc)},
            )
            logger.exception("Model training failed")
            raise

        db.execute(update(ModelRegistry).values(is_active=False))
        registry = ModelRegistry(
            model_name=result["model_name"],
            model_version=result["model_version"],
            model_path=result["model_path"],
            metrics=result["metrics"],
            is_active=True,
        )
        db.add(registry)
        db.add(
            MLLog(
                event_type="model_trained",
                message=f"Model version {result['model_version']} trained and activated",
                details={"metrics": result["metrics"], "mlflow_run_id": result.get("mlflow_run_id")},
            )
        )
        db.commit()
        self._predictor = None
        self._predictor_path = None
        logger.info(f"Activated model version {result['model_version']}")
        return result

    def _ensure_active_model(self, db: Session) -> ModelRegistry:
        active_model = self.get_active_model(db)
        if active_model is None:
            if not self.settings.allow_auto_train:
                raise ModelNotReadyError("No active model is registered")
            logger.info("No active model found; starting automatic training")
            self.train(db)
            active_model = self.get_active_model(db)

        if active_model is None:
            raise ModelNotReadyError("Model training did not produce an active model")
        if not Path(active_model.model_path).exists():
            raise ModelNotReadyError(f"Model artifact does not exist: {active_model.model_path}")
        return active_model

    def get_predictor(self, db: Session) -> ChurnPredictor:
        active_model = self._ensure_active_model(db)
        if self._predictor is None or self._predictor_path != active_model.model_path:
            self._predictor = ChurnPredictor(active_model.model_path)
            self._predictor_path = active_model.model_path
            logger.info(f"Loaded model version {active_model.model_version}")
        return self._predictor


ml_service = MLService()
