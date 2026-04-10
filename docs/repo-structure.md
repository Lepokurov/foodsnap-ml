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
- `app/workers/meal_analysis_worker.py`
- `app/ml/*`
- `app/utils/*`
- `migrations/*`
- `tests/api/test_api.py`
- `tests/conftest.py`
- `scripts/run-api.sh`
- `scripts/migrate.sh`
- `docs/dev-workflow.md`
- `uv.lock`

Planned but not implemented yet:
- `infra/*`
- `docker/*`

Meaning for future threads:
- do not assume the repo is only a plan
- do not rescan the whole tree before making simple backend changes
- the current code already supports a local end-to-end flow with `PostgreSQL`
- local file storage and in-memory queue are still stubs
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
    workers/
      meal_analysis_worker.py
    ml/
      classifier.py
      label_mapping.py
    utils/
      datetime.py
      ids.py
  migrations/
    versions/
  tests/
    api/
      test_api.py
    services/
    workers/
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

## Application files

### `app/main.py`
FastAPI entrypoint. Initializes the application, registers routers, seeds local database reference data, and starts/stops the in-memory worker loop.

### `app/api/routes/auth.py`
Authentication endpoints such as register and login.

### `app/api/routes/meals.py`
Endpoints for photo upload, meal retrieval, meal details, and manual meal correction if added later.

### `app/api/routes/summary.py`
Endpoints that return daily calorie summaries and meal aggregates.

### `app/api/routes/health.py`
Health and readiness checks for local runs and deployment environments. It includes a live database connectivity check.

### `app/api/deps/auth.py`
Reusable authentication dependencies, such as current-user resolution.

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
Business logic for registration and login flows backed by the user repository.

### `app/services/meal_ingestion.py`
Coordinates upload flow: stores image locally, persists the meal record in `PostgreSQL`, and enqueues a background task.

### `app/services/meal_analysis.py`
Coordinates prediction logic and persists recognition results in `PostgreSQL`.

### `app/services/calorie_estimator.py`
Converts recognized dish labels into approximate calorie estimates using the `food_reference` table.

### `app/services/summary.py`
Computes and formats daily calorie summaries through aggregate database queries.

### `app/services/storage.py`
Abstraction over file storage. Right now it writes to local disk as a stub and should later switch to `S3`.

### `app/services/queue.py`
Queue abstraction for sending meal-analysis tasks. Right now it uses an in-memory async queue and should later switch to `SQS`.

### `app/workers/meal_analysis_worker.py`
Background worker process that consumes queued jobs, loads images, runs recognition, estimates calories, and updates `PostgreSQL`.

### `app/ml/classifier.py`
Recognition entrypoint. The current version is a placeholder heuristic classifier based on filename patterns.

### `app/ml/label_mapping.py`
Maps raw classifier output into normalized internal dish labels.

### `app/utils/datetime.py`
Date and timezone helpers, especially for daily summaries.

### `app/utils/ids.py`
Optional helper utilities for object keys and internal identifiers.

## Database files

### `app/db/base.py`
Base SQLAlchemy metadata import point for models and migrations.

### `app/db/session.py`
Database engine, session management, local schema bootstrap helpers, reference-data seeding, and database connectivity checks.

### `app/db/models/user.py`
Database model for users.

### `app/db/models/meal_entry.py`
Database model for meal entries created from uploaded food photos.

### `app/db/models/meal_prediction.py`
Database model for storing ML-related prediction metadata, model version, and raw details if needed.

### `app/db/models/food_reference.py`
Reference nutrition table for known dishes and baseline calorie estimates.

### `app/db/repositories/users.py`
Database access helpers for user operations.

### `app/db/repositories/meals.py`
Database access helpers for meal entry CRUD and filtered reads.

### `app/db/repositories/summaries.py`
Aggregate query helpers for daily summary and reporting endpoints.

## Infrastructure files

### `migrations/versions/`
Alembic migration history for schema evolution.

### `tests/conftest.py`
Shared test fixtures and test environment bootstrap.

### `tests/api/`
API endpoint tests.

### `tests/services/`
Service-layer tests for business logic.

### `tests/workers/`
Worker processing tests for asynchronous flows.

### `infra/terraform/environments/dev/`
Terraform root configuration for the development environment.

### `infra/terraform/environments/prod/`
Terraform root configuration for the production-like environment.

### `infra/terraform/modules/ecs_service/`
Reusable ECS service definition for API and worker containers.

### `infra/terraform/modules/rds/`
Reusable `RDS PostgreSQL` module.

### `infra/terraform/modules/s3/`
Reusable `S3` bucket module for image storage.

### `infra/terraform/modules/sqs/`
Reusable `SQS` module for async tasks.

### `docker/api.Dockerfile`
Container build definition for the API service.

### `docker/worker.Dockerfile`
Container build definition for the background worker.

### `scripts/run-api.sh`
Local helper script to run the API service.

### `scripts/run-worker.sh`
Local helper script to run the background worker.

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
- Calorie estimation should remain rule-based in MVP and become more advanced later only if needed.
- Summary endpoints should read from canonical meal data instead of maintaining separate precomputed tables in the first version.
