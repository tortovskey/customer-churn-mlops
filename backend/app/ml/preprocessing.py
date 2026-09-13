from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = [
    "age",
    "tenure_months",
    "monthly_payment",
    "support_requests",
    "last_month_activity",
    "has_debt",
]
CATEGORICAL_FEATURES = ["tariff_type"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "churn"


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def client_to_dataframe(client: Any) -> pd.DataFrame:
    """Convert ORM object or dict-like client data into a single-row feature frame."""
    if isinstance(client, dict):
        values = client
    else:
        values = {column: getattr(client, column) for column in FEATURE_COLUMNS}

    normalized = {
        "age": int(values["age"]),
        "tenure_months": int(values["tenure_months"]),
        "monthly_payment": float(values["monthly_payment"]),
        "support_requests": int(values["support_requests"]),
        "tariff_type": str(values["tariff_type"]),
        "last_month_activity": float(values["last_month_activity"]),
        "has_debt": int(bool(values["has_debt"])),
    }
    return pd.DataFrame([normalized], columns=FEATURE_COLUMNS)

