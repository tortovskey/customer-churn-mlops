from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float | None = None
    train_size: int | None = None
    test_size: int | None = None


class ModelVersionResponse(BaseModel):
    model_name: str
    model_version: str | None
    model_path: str | None
    is_active: bool
    created_at: datetime | None = None


class TrainResponse(BaseModel):
    model_name: str
    model_version: str
    model_path: str
    metrics: ModelMetrics
    mlflow_run_id: str | None = None


class MLLogRead(BaseModel):
    id: int
    event_type: str
    message: str
    details: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MLDashboardResponse(BaseModel):
    version: ModelVersionResponse
    metrics: ModelMetrics | None
    logs: list[MLLogRead]

