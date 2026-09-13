from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from app.ml.preprocessing import client_to_dataframe


@dataclass(frozen=True)
class PredictionOutput:
    probability: float
    label: str
    model_version: str
    explanation: dict[str, float | str | bool]


class ChurnPredictor:
    """Thin serving wrapper around the trained sklearn pipeline."""

    def __init__(self, model_path: str | Path):
        artifact = joblib.load(model_path)
        self.model = artifact["model"]
        self.model_name = artifact["model_name"]
        self.model_version = artifact["model_version"]
        self.metrics = artifact.get("metrics", {})

    @staticmethod
    def risk_label(probability: float) -> str:
        if probability >= 0.65:
            return "высокий риск"
        if probability >= 0.35:
            return "средний риск"
        return "низкий риск"

    def predict(self, client: Any) -> PredictionOutput:
        features = client_to_dataframe(client)
        probability = float(self.model.predict_proba(features)[:, 1][0])
        rounded_probability = round(probability, 4)
        return PredictionOutput(
            probability=rounded_probability,
            label=self.risk_label(probability),
            model_version=self.model_version,
            explanation={
                "age": int(features.loc[0, "age"]),
                "tenure_months": int(features.loc[0, "tenure_months"]),
                "monthly_payment": float(features.loc[0, "monthly_payment"]),
                "support_requests": int(features.loc[0, "support_requests"]),
                "tariff_type": str(features.loc[0, "tariff_type"]),
                "last_month_activity": float(features.loc[0, "last_month_activity"]),
                "has_debt": bool(features.loc[0, "has_debt"]),
            },
        )

