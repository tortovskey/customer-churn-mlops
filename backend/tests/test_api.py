from fastapi.testclient import TestClient


def sample_client_payload() -> dict:
    return {
        "full_name": "Иван Петров",
        "age": 36,
        "tenure_months": 14,
        "monthly_payment": 3200.0,
        "support_requests": 5,
        "tariff_type": "standard",
        "last_month_activity": 42.0,
        "has_debt": True,
    }


def create_client(client: TestClient) -> dict:
    response = client.post("/clients", json=sample_client_payload())
    assert response.status_code == 201
    return response.json()


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_client(client: TestClient) -> None:
    created = create_client(client)

    assert created["id"] > 0
    assert created["full_name"] == "Иван Петров"
    assert created["tariff_type"] == "standard"


def test_get_client(client: TestClient) -> None:
    created = create_client(client)

    response = client.get(f"/clients/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["monthly_payment"] == 3200.0


def test_ml_prediction(client: TestClient) -> None:
    created = create_client(client)

    response = client.post(f"/predictions/{created['id']}")

    assert response.status_code == 201
    payload = response.json()
    assert 0 <= payload["prediction"]["prediction_value"] <= 1
    assert payload["prediction"]["prediction_label"] in [
        "низкий риск",
        "средний риск",
        "высокий риск",
    ]
    assert payload["prediction"]["model_version"]


def test_api_response_structure(client: TestClient) -> None:
    created = create_client(client)
    client.post(f"/predictions/{created['id']}")

    response = client.get("/predictions")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert {"id", "client_id", "model_version", "prediction_value", "prediction_label", "created_at"} <= set(
        payload[0].keys()
    )
    assert payload[0]["client"]["full_name"] == "Иван Петров"
