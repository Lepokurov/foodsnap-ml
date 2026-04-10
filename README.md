# FoodSnap ML

FoodSnap ML is a pet project focused on food photo recognition and approximate calorie tracking.

The chosen MVP stack:
- `FastAPI` for the backend API
- `PostgreSQL` as the primary database
- `AWS S3` for photo storage
- `AWS RDS PostgreSQL` for production database hosting
- `AWS ECS Fargate` for running API and background workers
- `AWS SQS` as the background task queue
- `AWS CloudWatch` for logs and basic observability

Optional components for later iterations:
- `Redis` for caching and rate limiting
- a dedicated ML model service if the prediction layer grows in complexity

Development tooling baseline:
- `uv` for Python version management, virtual environment workflow, dependency installation, locking, and command execution
- `pyproject.toml` as the single project configuration entrypoint
- `uv.lock` as the committed dependency lockfile
- `ruff` is the preferred future choice for linting and formatting
- `pytest` for tests

## MVP goal

Build a backend service that:
- accepts a food photo,
- stores it,
- runs asynchronous dish recognition,
- estimates calories,
- saves meal history,
- provides a daily calorie summary.

The MVP is intentionally not positioned as a medically accurate nutrition tool. It should provide a practical and believable approximation workflow.

## Product scope

Core user flow:
1. A user uploads a food photo.
2. The API stores the original image in `S3`.
3. The system creates a meal entry with status `pending`.
4. A worker consumes a task from `SQS` and processes the image.
5. The worker stores the recognized label, confidence, and estimated calories.
6. The user retrieves meal history and daily summary through the API.

## Architecture at a glance

Main components:
- `API service` handles authentication, uploads, meal history, and summaries.
- `Worker service` handles background meal analysis.
- `PostgreSQL` stores users, meal entries, prediction metadata, and reference food data.
- `S3` stores uploaded meal photos.
- `SQS` decouples upload requests from background processing.

Detailed file-by-file project planning lives in:
- [docs/repo-structure.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/repo-structure.md)
- [docs/mvp-backlog.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/mvp-backlog.md)
- [docs/project-context.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/project-context.md)
- [docs/dev-workflow.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/dev-workflow.md)

## MVP principles

- Prefer a complete working pipeline over high ML accuracy.
- Keep calorie estimation approximate and transparent.
- Store enough metadata to improve the ML pipeline later.
- Use AWS services that are practical for a backend-focused pet project.
- Defer non-essential complexity until after the first end-to-end version works.

## Current local MVP

The repository now contains a first API implementation focused on speed of iteration:
- `FastAPI` application scaffold under `app/`
- `PostgreSQL` persistence for users, meals, predictions, and food reference data
- `Alembic` migration baseline for schema evolution
- local file storage stub under `data/uploads` instead of `S3`
- in-memory async queue plus background worker instead of `SQS`
- stub classifier and rule-based calorie estimator for end-to-end meal processing
- `uv`-managed local environment and lockfile for reproducible setup

Implemented API endpoints:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/health`
- `POST /api/v1/meals`
- `GET /api/v1/meals`
- `GET /api/v1/meals/{meal_id}`
- `GET /api/v1/summary/daily`

Run locally:

```bash
createdb foodsnap_ml
cp .env.example .env
uv sync --extra dev
uv run ./scripts/migrate.sh
uv run ./scripts/run-api.sh
```

The default local setup expects PostgreSQL running on your current machine and uses the local database `foodsnap_ml` through the default socket connection.

Environment setup:

```bash
cp .env.example .env
```

`docker-compose.yml` is kept in the repo as an optional fallback, but local-on-machine PostgreSQL is the primary development path for now.

## Local PostgreSQL setup

Recommended local database contract:
- local database name: `foodsnap_ml`
- connection string: `postgresql+psycopg:///foodsnap_ml`
- authentication: default local PostgreSQL user and socket connection

Suggested one-time setup order:

```bash
createdb foodsnap_ml
cp .env.example .env
uv sync --extra dev
uv run ./scripts/migrate.sh
```

Verify the schema:

```bash
psql -d foodsnap_ml -c '\dt'
```

## Alembic workflow

Important note:
- `Alembic` is already initialized in this repository
- you do not need to run `alembic init` for normal work
- for day-to-day development, only create new revisions and apply them

Create a new migration after model changes:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Rollback one step:

```bash
uv run alembic downgrade -1
```

If you specifically want to see the manual initialization command for a brand-new repo, it would be:

```bash
uv run alembic init migrations
```

For this project, that step has already been done and the generated files are committed.

Run tests locally:

```bash
uv run pytest
```
