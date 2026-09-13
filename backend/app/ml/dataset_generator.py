import numpy as np
import pandas as pd

from app.ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN


def generate_customer_churn_dataset(
    rows: int = 2500,
    random_state: int = 42,
) -> pd.DataFrame:
    """Generate deterministic synthetic customer data with a learnable churn signal."""
    rng = np.random.default_rng(random_state)
    tariff_values = np.array(["basic", "standard", "premium", "enterprise"])
    tariff_probabilities = np.array([0.38, 0.34, 0.2, 0.08])

    age = rng.integers(18, 75, size=rows)
    tenure_months = rng.integers(0, 96, size=rows)
    monthly_payment = np.round(rng.normal(2800, 1050, size=rows).clip(350, 9500), 2)
    support_requests = rng.poisson(2.2, size=rows).clip(0, 18)
    tariff_type = rng.choice(tariff_values, size=rows, p=tariff_probabilities)
    last_month_activity = np.round(rng.beta(2.4, 1.8, size=rows) * 100, 2)
    has_debt = rng.binomial(1, 0.17, size=rows)

    tariff_risk = np.select(
        [
            tariff_type == "basic",
            tariff_type == "standard",
            tariff_type == "premium",
            tariff_type == "enterprise",
        ],
        [0.28, 0.12, -0.08, -0.18],
        default=0,
    )

    logit = (
        -1.35
        + 0.055 * support_requests
        + 0.75 * has_debt
        - 0.028 * tenure_months
        - 0.032 * last_month_activity
        + 0.00018 * monthly_payment
        + 0.012 * np.maximum(age - 45, 0)
        + tariff_risk
        + rng.normal(0, 0.65, size=rows)
    )
    churn_probability = 1 / (1 + np.exp(-logit))
    churn = rng.binomial(1, churn_probability)

    dataset = pd.DataFrame(
        {
            "age": age,
            "tenure_months": tenure_months,
            "monthly_payment": monthly_payment,
            "support_requests": support_requests,
            "tariff_type": tariff_type,
            "last_month_activity": last_month_activity,
            "has_debt": has_debt.astype(bool),
            TARGET_COLUMN: churn,
        }
    )
    return dataset[FEATURE_COLUMNS + [TARGET_COLUMN]]

