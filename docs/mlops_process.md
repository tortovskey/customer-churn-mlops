# MLOps-процессы

## 1. Data Collection

Данные клиентов собираются через frontend и endpoint `POST /clients`. После валидации они сохраняются в таблицу `clients`.

## 2. Data Validation

Валидация реализована через Pydantic v2:

- возраст от 18 до 100;
- срок использования от 0 до 360 месяцев;
- ежемесячный платеж не отрицательный;
- активность от 0 до 100;
- тариф из фиксированного списка.

Это предотвращает попадание некорректных данных в ML pipeline.

## 3. Model Training

Модуль `backend/app/ml/train_model.py`:

- генерирует синтетический dataset;
- строит preprocessing pipeline;
- обучает `RandomForestClassifier`;
- считает accuracy, precision, recall, f1-score, ROC-AUC;
- сохраняет модель через `joblib`.

## 4. Experiment Tracking

MLflow логирует:

- параметры обучения;
- метрики качества;
- sklearn model artifact;
- JSON с метриками.

Tracking server запускается отдельным сервисом в `docker-compose.yml`.

## 5. Model Versioning

Версия модели создается при каждом обучении на основе UTC timestamp.

Версия хранится в:

- `model_registry.model_version`;
- `predictions.model_version`;
- имени файла модели;
- `latest.json`.

## 6. Model Serving

Serving реализован через FastAPI endpoint:

- `POST /predictions/{client_id}`.

Модель загружается один раз и кэшируется в `MLService`, пока не появится новая активная версия.

## 7. Monitoring

Реализовано базовое логирование:

- HTTP-запросов через middleware;
- событий обучения;
- ошибок обучения;
- созданных прогнозов.

ML-события сохраняются в таблицу `ml_logs` и доступны на `GET /ml/logs`.

## 8. CI/CD

Пример pipeline находится в `.github/workflows/ci.yml`.

Он выполняет:

- установку Python 3.12;
- установку зависимостей;
- запуск pytest;
- сборку Docker image backend.

## 9. Retraining

Переобучение запускается endpoint:

- `POST /ml/train`.

После успешного обучения:

- старая модель деактивируется;
- новая запись попадает в `model_registry`;
- новая версия становится активной;
- прогнозы начинают выполняться новой моделью.

## Что можно добавить в будущем

- drift detection;
- мониторинг качества на реальных label после факта;
- approval workflow перед активацией модели;
- A/B testing моделей;
- feature store;
- автоматическое расписание retraining;
- алерты при деградации метрик;
- MLflow Model Registry stages.

