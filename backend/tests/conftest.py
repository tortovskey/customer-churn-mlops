import os
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

TEST_ROOT = Path(tempfile.mkdtemp(prefix="churn-tests-"))
TEST_DB_PATH = TEST_ROOT / "test.db"
TEST_MODEL_DIR = TEST_ROOT / "models"
TEST_MLFLOW_DIR = TEST_ROOT / "mlruns"
TEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)
TEST_MLFLOW_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "false"
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["MLFLOW_TRACKING_URI"] = TEST_MLFLOW_DIR.resolve().as_uri()
os.environ["MODEL_STORAGE_DIR"] = str(TEST_MODEL_DIR)
os.environ["TRAINING_ROWS"] = "500"
os.environ["TRAINING_RANDOM_STATE"] = "7"
os.environ["ALLOW_AUTO_TRAIN"] = "true"
os.environ["LOG_LEVEL"] = "WARNING"

from fastapi.testclient import TestClient  # noqa: E402
import pytest  # noqa: E402

import app.models  # noqa: F401,E402
from app.database.base import Base  # noqa: E402
from app.database.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services.ml_service import ml_service  # noqa: E402

engine = create_engine(
    f"sqlite+pysqlite:///{TEST_DB_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ml_service._predictor = None
    ml_service._predictor_path = None


def create_test_client() -> TestClient:
    reset_database()
    return TestClient(app)


@pytest.fixture()
def client() -> TestClient:
    return create_test_client()
