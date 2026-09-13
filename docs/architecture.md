# Архитектура системы

## Назначение

Customer Churn MLOps System - это информационная система, в которую встроена ML-модель для прогнозирования оттока клиентов. Главная идея: отделить пользовательский интерфейс, API, бизнес-сценарии, работу с БД и ML-жизненный цикл.

## Слои

### 1. Frontend Layer

Расположен в `frontend/`.

Отвечает за:

- формы добавления и редактирования клиентов;
- карточку клиента;
- запуск прогноза;
- просмотр истории прогнозов;
- MLOps-панель.

Frontend использует Vanilla JavaScript и Fetch API. Он не содержит ML-логики и не обращается к БД напрямую.

### 2. API Layer

Расположен в `backend/app/routers/`.

FastAPI принимает HTTP-запросы, валидирует payload через Pydantic и передает управление сервисам.

### 3. Business Logic Layer

Расположен в `backend/app/services/`.

Сервисы описывают сценарии:

- создать клиента;
- обновить клиента;
- получить активную модель;
- сделать прогноз;
- сохранить прогноз;
- запустить обучение;
- записать ML-событие.

### 4. ML Service Layer

Расположен в `backend/app/ml/`.

ML-модель вынесена в отдельный слой, потому что:

- API не должен знать детали preprocessing и sklearn pipeline;
- модель можно заменить без переписывания routers;
- inference можно вынести в отдельный сервис;
- проще тестировать и версионировать артефакты.

### 5. Data Access Layer

Расположен в `backend/app/models/` и `backend/app/database/`.

SQLAlchemy модели описывают таблицы:

- `clients`;
- `predictions`;
- `model_registry`;
- `ml_logs`.

### 6. MLOps Layer

Включает:

- `dataset_generator.py`;
- `preprocessing.py`;
- `train_model.py`;
- MLflow tracking;
- `model_registry`;
- `ml_logs`;
- endpoint `/ml/train`.

## Взаимодействие API и ML-модели

1. Пользователь нажимает «Сделать прогноз».
2. Frontend отправляет `POST /predictions/{client_id}`.
3. API вызывает `prediction_service.create_prediction`.
4. Сервис получает клиента из БД.
5. `MLService` загружает активный `joblib`-артефакт.
6. `ChurnPredictor` преобразует клиента в pandas DataFrame.
7. sklearn pipeline выполняет preprocessing и `predict_proba`.
8. Прогноз сохраняется в `predictions`.
9. Событие сохраняется в `ml_logs`.

## Замена модели

Модель можно заменить, если новый артефакт поддерживает тот же контракт:

- принимает признаки из `FEATURE_COLUMNS`;
- возвращает вероятность класса оттока;
- сохраняется через `joblib`;
- регистрируется в `model_registry`.

Поэтому API и frontend не зависят от конкретного алгоритма RandomForest.

## Масштабирование

Возможные направления:

- отдельный inference service;
- async training jobs;
- очередь для retraining;
- MLflow Model Registry;
- мониторинг data drift;
- feature store;
- object storage для артефактов;
- Prometheus/Grafana;
- авторизация и аудит.

