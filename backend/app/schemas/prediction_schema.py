from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.client_schema import ClientRead


class PredictionBase(BaseModel):
    client_id: int
    model_version: str
    prediction_value: float = Field(..., ge=0, le=1)
    prediction_label: str


class PredictionRead(PredictionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PredictionWithClient(PredictionRead):
    client: ClientRead | None = None

    model_config = ConfigDict(from_attributes=True)


class PredictionResult(BaseModel):
    prediction: PredictionRead
    explanation: dict[str, float | str | bool]

