# Repository Structure

This document describes the current repository layout and the intended responsibility boundaries.

## Current reality

The repository contains a working local MVP with local `PostgreSQL` persistence.

Implemented now:
- `app/main.py`
- `app/api/routes/*`
- `app/api/deps/*`
- `app/core/*`
- `app/db/*`
- `app/schemas/*`
- `app/services/*`
- `consumers/*`
- `docker/Dockerfile.meal-analysis-consumer`
- `docker/Dockerfile.food-reference-import-consumer`
- `app/ml/*`
- `app/utils/*`
- `migrations/*`
- `tests/api/test_api.py`
- `tests/conftest.py`
- `scripts/run-api.sh`
- `scripts/migrate.sh`
- `docs/queue-contract.md`
- `docs/dev-workflow.md`
- `uv.lock`
- `docker-compose.yml` for local RabbitMQ

Planned but not implemented yet:
- `infra/*`

Meaning for future threads:
- do not assume the repo is only a plan
- do not rescan the whole tree before making simple backend changes
- the current code already supports local API flow with `PostgreSQL`
- storage is switchable between local filesystem and S3
- RabbitMQ publishing is implemented in the API
- RabbitMQ consuming is implemented as two separate microservice entrypoints in this repository
- local Python workflow is already standardized around `uv`

## Top-level layout

```text
aws-pet-proj/
  README.md
  docs/
    project-context.md
    mvp-backlog.md
    repo-structure.md
    dev-workflow.md
    queue-contract.md
    food-data-sources.md
  app/
    main.py
    api/
      routes/
        auth.py
        meals.py
        summary.py
        health.py
      deps/
        auth.py
        common.py
    core/
      config.py
      security.py
      logging.py
    db/
      base.py
      session.py
      models/
        user.py
        meal_entry.py
        meal_prediction.py
        food_reference.py
      repositories/
        users.py
        meals.py
        summaries.py
    schemas/
      auth.py
      meal.py
      summary.py
      common.py
    services/
      auth.py
      meal_ingestion.py
      meal_analysis.py
      calorie_estimator.py
      summary.py
      storage.py
      queue.py
    ml/
      classifier.py
    utils/
      datetime.py
      ids.py
  consumers/
    rabbitmq.py
    meal_analysis/
      main.py
    food_reference_import/
      main.py
  docker/
    Dockerfile.meal-analysis-consumer
    Dockerfile.food-reference-import-consumer
  migrations/
    versions/
  tests/
    api/
      test_api.py
    services/
  scripts/
    run-api.sh
    run-worker.sh
    migrate.sh
  data/
    uploads/
  alembic.ini
  .env.example
  pyproject.toml
  uv.lock
  docker-compose.yml
```

## File-by-file intent

### `README.md`
Primary project overview. Should explain what the product is, which stack is chosen, and where to find deeper docs.

### `docs/project-context.md`
Short durable memory file for future threads. It should capture the product goal, MVP boundaries, architecture decisions, and current priorities.

### `docs/mvp-backlog.md`
Execution-oriented backlog. It should contain milestones, feature slices, and acceptance criteria for the MVP.

### `docs/repo-structure.md`
This file. It defines intended responsibility boundaries and highlights what already exists.

### `docs/dev-workflow.md`
Explains the chosen Python tooling standard, including `uv`, local environment expectations, and command conventions.

### `docs/queue-contract.md`
Defines the RabbitMQ message contract between this API producer and the RabbitMQ consumer microservices.

### `docs/food-data-sources.md`
Records external food/nutrition data sources for the food-reference import consumer.

## Application files

### `app/main.py`
FastAPI entrypoint. Initializes the application, registers routers, seeds local database reference data, and closes queue publisher resources on shutdown.

### `app/api/routes/auth.py`
Authentication endpoints such as register and login.

### `app/api/routes/meals.py`
Endpoints for photo upload, meal retrieval, meal details, and manual meal correction if added later.

### `app/api/routes/food_reference.py`
Endpoint for requesting asynchronous `food_reference` imports through RabbitMQ.

### `app/api/routes/summary.py`
Endpoints that return daily calorie summaries and meal aggregates.

### `app/api/routes/health.py`
Health and readiness checks for local runs and deployment environments. It includes a live database connectivity check.

### `app/api/deps/auth.py`
Reusable authentication dependencies, such as current-user resolution.

### `app/api/deps/db.py`
FastAPI database session dependency. It wraps the lower-level `get_db_session()` context manager for request-scoped API usage.

### `app/api/deps/repositories.py`
Repository factory dependencies. They bind repositories to the request-scoped SQLAlchemy `Session`.

### `app/api/deps/services.py`
Service factory dependencies. They compose repositories and services through FastAPI dependency injection.

### `app/api/deps/common.py`
Shared route dependencies, pagination helpers, and request-level utilities.

### `app/core/config.py`
Centralized application settings loaded from environment variables.

### `app/core/security.py`
Password hashing, token generation, and token verification logic.

### `app/core/logging.py`
Application logging configuration and structured log setup.

### `app/schemas/auth.py`
Pydantic schemas for authentication requests and responses.

### `app/schemas/meal.py`
Pydantic schemas for meal upload, meal detail, and meal list responses.

### `app/schemas/summary.py`
Pydantic schemas for summary endpoints.

### `app/schemas/common.py`
Shared response envelopes, pagination schemas, and common API models.

### `app/services/auth.py`
Business logic for registration and login flows. It receives its user repository through dependency injection.

### `app/services/meal_ingestion.py`
Coordinates upload flow: stores image through the injected storage backend, persists the meal record through an injected repository, and publishes a RabbitMQ meal-analysis task.

### `app/services/meal_analysis.py`
Coordinates prediction logic and persists recognition results through injected repository and calorie-estimator dependencies.

### `app/services/calorie_estimator.py`
Resolves classifier candidate labels against `food_reference` and converts the resolved label into an approximate calorie estimate using an injected SQLAlchemy `Session`.

### `app/services/summary.py`
Computes and formats daily calorie summaries through an injected summary repository.

### `app/services/storage.py`
Abstraction over file storage. Supports local filesystem storage and S3 storage selected by `STORAGE_BACKEND`.

### `app/services/queue.py`
Queue abstraction for publishing meal-analysis tasks. The default backend is RabbitMQ; the in-memory backend is retained for tests.

### `app/services/food_reference_import.py`
Business logic used by the food-reference import consumer. It validates import source/mode, normalizes requested labels, and upserts `food_reference` rows.

## Consumer microservices

### `consumers/rabbitmq.py`
Shared RabbitMQ consumer runner. It connects to RabbitMQ, declares a durable queue, consumes one message at a time, parses JSON, and delegates valid object payloads to a service-specific handler.

### `consumers/meal_analysis/main.py`
Entry point for the meal-analysis consumer microservice. It consumes `foodsnap.meal_analysis`, validates the message contract, runs `MealAnalysisService`, and updates `PostgreSQL`.

### `consumers/food_reference_import/main.py`
Entry point for the food-reference import consumer microservice. It consumes `foodsnap.food_reference_import`, validates the message contract, and runs `FoodReferenceImportService`.

## Docker files

### `docker/Dockerfile.meal-analysis-consumer`
Builds the deployable image for the meal-analysis consumer microservice.

### `docker/Dockerfile.food-reference-import-consumer`
Builds the deployable image for the food-reference import consumer microservice.

### `app/ml/classifier.py`
Recognition entrypoint. Supports a filename-based stub backend for local tests and an AWS Rekognition backend for AWS-backed runs. Classifiers return ordered candidate labels with confidence values; downstream services resolve them through `food_reference`.

### `app/utils/datetime.py`
Date and timezone helpers, especially for daily summaries.

### `app/utils/ids.py`
Optional helper utilities for object keys and internal identifiers.

## Database files

### `app/db/base.py`
Base SQLAlchemy metadata import point for models and migrations.

### `app/db/session.py`
Database engine, session management, local schema bootstrap helpers, reference-data seeding, and database connectivity checks. The `get_db_session()` context manager remains the shared low-level building block for API dependencies and non-FastAPI consumers.

### `app/db/models/user.py`
Database model for users.

### `app/db/models/meal_entry.py`
Database model for meal entries created from uploaded food photos.

### `app/db/models/meal_prediction.py`
Database model for storing ML-related prediction metadata, model version, and raw details if needed.

### `app/db/models/food_reference.py`
Reference nutrition table for known dishes and baseline calorie estimates.

### `app/db/repositories/users.py`
Database access helpers for user operations. Repositories receive a SQLAlchemy `Session` from the caller and do not open sessions themselves.

### `app/db/repositories/meals.py`
Database access helpers for meal entry CRUD and filtered reads. Repositories receive a SQLAlchemy `Session` from the caller and do not open sessions themselves.

### `app/db/repositories/summaries.py`
Aggregate query helpers for daily summary and reporting endpoints. Repositories receive a SQLAlchemy `Session` from the caller and do not open sessions themselves.

## Infrastructure files

### `migrations/versions/`
Alembic migration history for schema evolution.

### `tests/conftest.py`
Shared test fixtures and test environment bootstrap.

### `tests/api/`
API endpoint tests.

### `tests/services/`
Service-layer tests for business logic.

### `infra/terraform/environments/dev/`
Terraform root configuration for the development environment.

### `infra/terraform/environments/prod/`
Terraform root configuration for the production-like environment.

### `infra/terraform/modules/ecs_service/`
Reusable ECS service definition for API containers and future related services.

### `infra/terraform/modules/rds/`
Reusable `RDS PostgreSQL` module.

### `infra/terraform/modules/s3/`
Reusable `S3` bucket module for image storage.

### `infra/terraform/modules/rabbitmq/`
Reusable RabbitMQ or broker module for async tasks if the broker is managed in this repo later.

### `docker/api.Dockerfile`
Container build definition for the API service.

### `scripts/run-api.sh`
Local helper script to run the API service.

### `scripts/run-worker.sh`
Informational helper explaining that the worker is now a separate microservice outside this API repo.

### `scripts/migrate.sh`
Local helper script to run migrations.

### `.env.example`
Example environment variables for local development.

### `pyproject.toml`
Python project configuration, dependencies, and tool settings.

### `uv.lock`
Resolved dependency lockfile managed by `uv`.

### `alembic.ini`
Alembic configuration file.

## Boundary decisions

- The API service should not contain heavy ML logic directly inside route handlers.
- Background processing should be isolated in the worker layer.
- Storage and queue integrations should be hidden behind service abstractions.
- API database access should flow through `Depends(get_db)` into repositories and services.
- Non-FastAPI consumers should use `get_db_session()` directly and manually compose repositories/services.
- Calorie estimation should remain rule-based in MVP and become more advanced later only if needed.
- Summary endpoints should read from canonical meal data instead of maintaining separate precomputed tables in the first version.
