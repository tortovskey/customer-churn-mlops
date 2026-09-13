# Customer Churn MLOps System

Учебно-практический проект по теме «Интеграция моделей машинного обучения в информационную систему: архитектура и процессы MLOps».

Система прогнозирует вероятность оттока клиента, сохраняет результат в PostgreSQL и показывает жизненный цикл ML-модели: обучение, метрики, версию, serving, журнал событий и переобучение.

## Цель проекта

Показать не notebook с обучением модели, а полноценную информационную систему:

`данные клиента -> FastAPI -> ML-модель -> прогноз -> PostgreSQL -> история -> MLOps monitoring`

## Стек

- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2, Uvicorn.
- ML: scikit-learn, pandas, numpy, joblib, MLflow.
- Database: PostgreSQL, Alembic.
- Frontend: HTML5, CSS3, Vanilla JavaScript, Fetch API.
- DevOps/MLOps: Docker, Docker Compose, MLflow Tracking Server, pytest, GitHub Actions, loguru, pre-commit.

## Архитектура

Проект разделен на слои:

- Frontend Layer: страницы `frontend/*.html`, стили и JS-клиенты API.
- API Layer: FastAPI routers в `backend/app/routers`.
- Business Logic Layer: сервисы в `backend/app/services`.
- ML Service Layer: загрузка модели и inference в `backend/app/ml`.
- Data Access Layer: SQLAlchemy модели и сессии в `backend/app/models`, `backend/app/database`.
- MLOps Layer: обучение, MLflow tracking, registry, метрики и журнал событий.

## Быстрый запуск через Docker Compose

```bash
cd project
docker compose up --build
```

После запуска:

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- MLflow: http://localhost:5000
- PostgreSQL: `localhost:5432`

Миграции Alembic запускаются в контейнере backend перед стартом Uvicorn.

## Локальный запуск backend

```bash
cd project/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Для локального запуска PostgreSQL и MLflow можно использовать Docker Compose, а backend запускать отдельно.

## Frontend

Frontend статический. При Docker Compose его отдает nginx на `http://localhost:8080`.

По умолчанию JavaScript обращается к API `http://localhost:8000`. Если нужен другой адрес:

```js
localStorage.setItem("apiBaseUrl", "http://localhost:8000")
```

## API endpoints

### Клиенты

- `GET /clients` - список клиентов.
- `POST /clients` - создать клиента.
- `GET /clients/{client_id}` - получить клиента.
- `PUT /clients/{client_id}` - обновить клиента.
- `DELETE /clients/{client_id}` - удалить клиента.

### Предсказания

- `POST /predictions/{client_id}` - сделать прогноз оттока и сохранить его.
- `GET /predictions` - история всех прогнозов.
- `GET /predictions/{client_id}` - история прогнозов клиента.

### ML/MLOps

- `POST /ml/train` - обучить новую модель и активировать версию.
- `GET /ml/metrics` - метрики активной модели.
- `GET /ml/version` - текущая версия модели.
- `GET /ml/logs` - журнал ML-событий.
- `GET /ml/dashboard` - данные для MLOps-панели.
- `GET /health` - проверка backend и БД.

## Пример работы

1. Откройте `http://localhost:8080/clients.html`.
2. Добавьте клиента.
3. Откройте карточку клиента.
4. Нажмите «Сделать прогноз».
5. Результат сохранится в таблицу `predictions`.
6. Откройте `predictions.html`, чтобы увидеть историю.
7. Откройте `ml_dashboard.html`, чтобы увидеть версию модели, метрики и ML-журнал.

Если активной модели нет, backend автоматически обучит первую модель при первом прогнозе. Также модель можно обучить вручную через `POST /ml/train`.

## Обучение модели

Модель обучается на синтетическом датасете с устойчивым сигналом оттока:

- высокая частота обращений в поддержку повышает риск;
- задолженность повышает риск;
- низкая активность повышает риск;
- долгий срок использования снижает риск;
- тип тарифа влияет на вероятность оттока.

Команда через API:

```bash
curl -X POST http://localhost:8000/ml/train
```

Альтернативно можно запустить обучающий модуль без записи в registry:

```bash
cd project/backend
python -m app.ml.train_model
```

Основной production-путь обучения в проекте - endpoint `/ml/train`, потому что он сохраняет запись в `model_registry` и ML-журнал.

## Как сделать прогноз

```bash
curl -X POST http://localhost:8000/predictions/1
```

Ответ содержит:

- вероятность оттока `prediction_value`;
- класс риска `prediction_label`;
- версию модели `model_version`;
- признаки, переданные в модель.

## MLflow

MLflow Tracking Server доступен по адресу `http://localhost:5000`.

При обучении логируются:

- параметры модели;
- accuracy, precision, recall, f1-score, ROC-AUC;
- размер train/test выборок;
- sklearn model artifact;
- JSON с метриками.

## Model versioning

Каждое обучение создает версию по UTC timestamp с микросекундами, например `20260510204111012345`.

Версия сохраняется:

- в имени `joblib`-артефакта;
- в `latest.json`;
- в таблице `model_registry`;
- в каждой записи прогноза.

Это позволяет понять, какой именно моделью был сделан прогноз.

## Тестирование

```bash
cd project/backend
pytest -q
```

Тесты используют SQLite и локальный file-based MLflow store, поэтому им не нужен PostgreSQL или Docker Compose.

## Масштабирование

Систему можно развивать так:

- вынести ML inference в отдельный сервис;
- добавить очередь задач для обучения, например Celery/RQ;
- подключить Model Registry MLflow как основной источник активной модели;
- добавить мониторинг drift и качества после факта;
- хранить реальные датасеты в object storage;
- добавить авторизацию и роли пользователей;
- вынести frontend в отдельный CDN/nginx deployment;
- разделить read/write БД-нагрузку.

## Структура проекта

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

Credentials present in `docker-compose.yml` and `.env.example` are development-only defaults for the local demo stack. Replace them before deploying the project outside a local development environment. Runtime `.env`, database files, trained-model artifacts and experiment data are excluded from Git.
