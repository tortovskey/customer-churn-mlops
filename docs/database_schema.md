# Схема базы данных

## clients

Хранит клиентские признаки, которые используются информационной системой и ML-моделью.

| Поле | Тип | Описание |
| --- | --- | --- |
| id | integer | Первичный ключ |
| full_name | varchar(255) | Имя клиента |
| age | integer | Возраст |
| tenure_months | integer | Срок использования сервиса |
| monthly_payment | float | Ежемесячный платеж |
| support_requests | integer | Количество обращений в поддержку |
| tariff_type | varchar(50) | Тип тарифа |
| last_month_activity | float | Активность за последний месяц |
| has_debt | boolean | Наличие задолженности |
| created_at | timestamp | Дата создания |
| updated_at | timestamp | Дата обновления |

## predictions

Хранит результаты прогнозов.

| Поле | Тип | Описание |
| --- | --- | --- |
| id | integer | Первичный ключ |
| client_id | integer | FK на `clients.id` |
| model_version | varchar(120) | Версия модели |
| prediction_value | float | Вероятность оттока |
| prediction_label | varchar(50) | Класс риска |
| created_at | timestamp | Дата прогноза |

## model_registry

Хранит версии моделей.

| Поле | Тип | Описание |
| --- | --- | --- |
| id | integer | Первичный ключ |
| model_name | varchar(120) | Название модели |
| model_version | varchar(120) | Уникальная версия |
| model_path | varchar(500) | Путь к joblib-артефакту |
| metrics | json | Метрики качества |
| is_active | boolean | Используется ли версия для serving |
| created_at | timestamp | Дата регистрации |

## ml_logs

Хранит журнал MLOps-событий.

| Поле | Тип | Описание |
| --- | --- | --- |
| id | integer | Первичный ключ |
| event_type | varchar(80) | Тип события |
| message | text | Сообщение |
| details | json | Дополнительные данные |
| created_at | timestamp | Дата события |

## Связи

- `clients 1 -> N predictions`
- `model_registry` логически связан с `predictions.model_version`
- `ml_logs` хранит события обучения, ошибок и прогнозов

