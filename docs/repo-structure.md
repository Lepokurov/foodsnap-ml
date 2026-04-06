# Repository Structure

This document describes the planned repository layout for the first implementation stage. It is intentionally written before code exists so the project can be built with clear boundaries.

## Top-level layout

```text
aws-pet-proj/
  README.md
  docs/
    project-context.md
    mvp-backlog.md
    repo-structure.md
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
    conftest.py
    api/
    services/
    workers/
  infra/
    terraform/
      environments/
        dev/
        prod/
      modules/
        ecs_service/
        rds/
        s3/
        sqs/
  docker/
    api.Dockerfile
    worker.Dockerfile
  scripts/
    run-api.sh
    run-worker.sh
    migrate.sh
  .env.example
  pyproject.toml
  alembic.ini
```

## File-by-file intent

### `README.md`
Primary project overview. Should explain what the product is, which stack is chosen, and where to find deeper docs.

### `docs/project-context.md`
Short durable memory file for future threads. It should capture the product goal, MVP boundaries, architecture decisions, and current priorities.

### `docs/mvp-backlog.md`
Execution-oriented backlog. It should contain milestones, feature slices, and acceptance criteria for the MVP.

### `docs/repo-structure.md`
This file. It defines intended responsibility boundaries before implementation starts.

## Application files

### `app/main.py`
FastAPI entrypoint. Will initialize the application, register routers, and connect startup/shutdown hooks.

### `app/api/routes/auth.py`
Authentication endpoints such as register and login.

### `app/api/routes/meals.py`
Endpoints for photo upload, meal retrieval, meal details, and manual meal correction if added later.

### `app/api/routes/summary.py`
Endpoints that return daily calorie summaries and meal aggregates.

### `app/api/routes/health.py`
Health and readiness checks for local runs and deployment environments.

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

### `app/db/base.py`
Base SQLAlchemy metadata import point for models and migrations.

### `app/db/session.py`
Database engine and session management.

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

### `app/schemas/auth.py`
Pydantic schemas for authentication requests and responses.

### `app/schemas/meal.py`
Pydantic schemas for meal upload, meal detail, and meal list responses.

### `app/schemas/summary.py`
Pydantic schemas for summary endpoints.

### `app/schemas/common.py`
Shared response envelopes, pagination schemas, and common API models.

### `app/services/auth.py`
Business logic for registration and login flows.

### `app/services/meal_ingestion.py`
Coordinates upload flow: persist record, store image, enqueue background task.

### `app/services/meal_analysis.py`
Coordinates prediction logic and persistence of recognition results.

### `app/services/calorie_estimator.py`
Converts recognized dish labels into approximate calorie estimates using reference data and simple rules.

### `app/services/summary.py`
Computes and formats daily calorie summaries.

### `app/services/storage.py`
Abstraction over file storage, initially targeting `S3`.

### `app/services/queue.py`
Queue abstraction for sending meal-analysis tasks to `SQS`.

### `app/workers/meal_analysis_worker.py`
Background worker process that consumes queued jobs, downloads images, runs recognition, estimates calories, and updates the database.

### `app/ml/classifier.py`
Recognition entrypoint. In the earliest version it may wrap a placeholder or heuristic classifier and later evolve into a real ML integration.

### `app/ml/label_mapping.py`
Maps raw classifier output into normalized internal dish labels.

### `app/utils/datetime.py`
Date and timezone helpers, especially for daily summaries.

### `app/utils/ids.py`
Optional helper utilities for object keys and internal identifiers.

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

### `alembic.ini`
Alembic configuration file.

## Boundary decisions

- The API service should not contain heavy ML logic directly inside route handlers.
- Background processing should be isolated in the worker layer.
- Storage and queue integrations should be hidden behind service abstractions.
- Calorie estimation should remain rule-based in MVP and become more advanced later only if needed.
- Summary endpoints should read from canonical meal data instead of maintaining separate precomputed tables in the first version.
