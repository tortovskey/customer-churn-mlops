# Customer Churn MLOps System

An educational project demonstrating how to integrate machine learning into an
information system, including the application architecture and MLOps workflow.

The system estimates customer churn probability, stores predictions in PostgreSQL,
and exposes the model lifecycle: training, metrics, versioning, serving, event
logging, and retraining.

## Project goal

Demonstrate a complete application workflow around a machine learning model:

`Customer data -> FastAPI -> ML model -> Prediction -> PostgreSQL -> History -> MLOps monitoring`

## Technology stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2, Uvicorn.
- Machine learning: scikit-learn, pandas, NumPy, joblib, MLflow.
- Database: PostgreSQL, Alembic.
- Frontend: HTML5, CSS3, vanilla JavaScript, Fetch API.
- DevOps/MLOps: Docker, Docker Compose, MLflow Tracking Server, pytest, GitHub Actions, loguru, pre-commit.

## Architecture

The application is organized into layers:

- Frontend: pages in `frontend/*.html`, styles, and JavaScript API clients.
- API: FastAPI routers in `backend/app/routers`.
- Business logic: services in `backend/app/services`.
- ML service: model loading and inference in `backend/app/ml`.
- Data access: SQLAlchemy models and sessions in `backend/app/models` and `backend/app/database`.
- MLOps: training, MLflow tracking, registry records, metrics, and event logging.

## Quick start with Docker Compose

```bash
cd project
docker compose up --build
```

Services are available at:

| Service | Address |
|---|---|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| PostgreSQL | `localhost:5432` |

The backend container runs Alembic migrations before starting Uvicorn.

## Run the backend locally

```powershell
cd project/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

You can run PostgreSQL and MLflow through Docker Compose while developing the
backend locally.

## Frontend

The frontend is static. Docker Compose serves it through nginx at
`http://localhost:8080`.

JavaScript requests use `http://localhost:8000` as the default API address.
To change it:

```js
localStorage.setItem("apiBaseUrl", "http://localhost:8000")
```

## API endpoints

### Customers

- `GET /clients`: list customers.
- `POST /clients`: create a customer.
- `GET /clients/{client_id}`: retrieve a customer.
- `PUT /clients/{client_id}`: update a customer.
- `DELETE /clients/{client_id}`: delete a customer.

### Predictions

- `POST /predictions/{client_id}`: predict churn and save the result.
- `GET /predictions`: retrieve prediction history.
- `GET /predictions/{client_id}`: retrieve a customer's prediction history.

### ML and MLOps

- `POST /ml/train`: train a model and activate its version.
- `GET /ml/metrics`: retrieve active-model metrics.
- `GET /ml/version`: retrieve the current model version.
- `GET /ml/logs`: retrieve ML event logs.
- `GET /ml/dashboard`: retrieve MLOps dashboard data.
- `GET /health`: check the backend and database.

## Example workflow

1. Open `http://localhost:8080/clients.html`.
2. Add a customer and open their details.
3. Use the prediction action to estimate churn.
4. The result is saved in the `predictions` table.
5. Open `predictions.html` to inspect prediction history.
6. Open `ml_dashboard.html` to view the model version, metrics, and ML event log.

If no model is active, the backend trains the initial model when the first
prediction is requested. You can also start training with `POST /ml/train`.

## Model training

Training uses a synthetic dataset with a consistent churn signal:

- Frequent support requests increase risk.
- Outstanding debt increases risk.
- Low activity increases risk.
- Longer customer tenure reduces risk.
- The subscription plan affects churn probability.

Start training through the API:

```bash
curl -X POST http://localhost:8000/ml/train
```

Alternatively, run the training module without writing a registry record:

```bash
cd project/backend
python -m app.ml.train_model
```

The application's main training workflow uses `/ml/train` because it writes both
a `model_registry` record and ML event logs.

## Make a prediction

```bash
curl -X POST http://localhost:8000/predictions/1
```

The response includes churn probability (`prediction_value`), risk class
(`prediction_label`), model version (`model_version`), and the input features.

## MLflow tracking

The MLflow Tracking Server is available at `http://localhost:5000`.
Training records:

- Model parameters.
- Accuracy, precision, recall, F1 score, and ROC-AUC.
- Training and test set sizes.
- The scikit-learn model artifact.
- Metrics in JSON format.

## Model versioning

Each training run creates a version from a UTC timestamp with microseconds,
for example `20260510204111012345`.

The version is recorded in the `joblib` artifact filename, `latest.json`, the
`model_registry` table, and each prediction record. This identifies the model
that produced a particular prediction.

## Tests

```bash
cd project/backend
pytest -q
```

Tests use SQLite and a local file-based MLflow store. PostgreSQL and Docker Compose
are not required for the test suite.

## Possible extensions

- Move inference into a dedicated service.
- Add a training queue such as Celery or RQ.
- Use MLflow Model Registry as the source of the active model.
- Add drift monitoring and evaluation against observed outcomes.
- Store real datasets in object storage.
- Add authentication and user roles.
- Deploy the frontend through a separate CDN or nginx service.
- Separate database read and write workloads.

## Project structure

```text
project/
  backend/
    app/
      main.py
      config/
      database/
      models/
      schemas/
      routers/
      services/
      ml/
      core/
      utils/
    alembic/
    tests/
    requirements.txt
    Dockerfile
    .env.example
  frontend/
    index.html
    clients.html
    client_detail.html
    predictions.html
    ml_dashboard.html
    css/
    js/
  docs/
  docker-compose.yml
```

## Security note

Credentials in `docker-compose.yml` and `.env.example` are development-only defaults
for the local demo stack. Replace them before deployment outside a local development
environment. Runtime `.env`, database files, trained-model artifacts, and experiment
data are excluded from Git.
