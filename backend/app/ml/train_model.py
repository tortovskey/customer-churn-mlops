from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.config.settings import Settings
from app.ml.dataset_generator import generate_customer_churn_dataset
from app.ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN, build_preprocessor


def _build_pipeline(random_state: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=180,
                    max_depth=9,
                    min_samples_leaf=4,
                    class_weight="balanced",
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def _evaluate_model(model: Pipeline, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)[:, 1]
    return {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
    }


def train_customer_churn_model(
    settings: Settings,
    rows: int = 2500,
    random_state: int = 42,
) -> dict[str, Any]:
    """Train a RandomForest churn model, store artifacts and log MLflow experiment."""
    settings.model_storage_dir.mkdir(parents=True, exist_ok=True)
    dataset = generate_customer_churn_dataset(rows=rows, random_state=random_state)
    x = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.22,
        random_state=random_state,
        stratify=y,
    )

    model = _build_pipeline(random_state=random_state)
    version = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")

    mlflow_run_id: str | None = None
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

    with mlflow.start_run(run_name=f"{settings.model_name}-{version}") as run:
        mlflow_run_id = run.info.run_id
        mlflow.log_params(
            {
                "model_type": "RandomForestClassifier",
                "rows": rows,
                "random_state": random_state,
                "n_estimators": 180,
                "max_depth": 9,
                "min_samples_leaf": 4,
            }
        )

        model.fit(x_train, y_train)
        metrics = _evaluate_model(model, x_test, y_test)
        metrics["train_size"] = int(len(x_train))
        metrics["test_size"] = int(len(x_test))
        mlflow.log_metrics(metrics)

        artifact = {
            "model": model,
            "model_name": settings.model_name,
            "model_version": version,
            "feature_columns": FEATURE_COLUMNS,
            "metrics": metrics,
        }
        model_path = Path(settings.model_storage_dir) / f"{settings.model_name}_{version}.joblib"
        metrics_path = Path(settings.model_storage_dir) / f"{settings.model_name}_{version}_metrics.json"
        latest_path = Path(settings.model_storage_dir) / "latest.json"
        joblib.dump(artifact, model_path)

        metrics_payload = {
            "model_name": settings.model_name,
            "model_version": version,
            "model_path": str(model_path),
            "metrics": metrics,
            "mlflow_run_id": mlflow_run_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
        metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
        latest_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

        mlflow.sklearn.log_model(model, artifact_path="model")
        mlflow.log_artifact(str(metrics_path))

    return metrics_payload


if __name__ == "__main__":
    from app.config.settings import get_settings

    training_result = train_customer_churn_model(get_settings())
    print(json.dumps(training_result, ensure_ascii=False, indent=2))
