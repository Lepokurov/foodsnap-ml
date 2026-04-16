# FoodSnap ML

FoodSnap ML is a pet project focused on food photo recognition and approximate calorie tracking.

The chosen MVP stack:
- `FastAPI` for the backend API
- `PostgreSQL` as the primary database
- `AWS S3` for photo storage
- `AWS RDS PostgreSQL` for production database hosting
- `AWS ECS Fargate` for running API and background workers
- `RabbitMQ` as the background task queue
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
4. The API publishes a meal-analysis task to `RabbitMQ`.
5. The meal-analysis consumer microservice consumes the task and processes the image.
6. The worker stores the recognized label, confidence, and estimated calories.
7. The user retrieves meal history and daily summary through the API.

## Architecture at a glance

Main components:
- `API service` handles authentication, uploads, meal history, and summaries.
- `Consumer services` handle background meal analysis and food-reference imports.
- `PostgreSQL` stores users, meal entries, prediction metadata, and reference food data.
- `S3` stores uploaded meal photos.
- `RabbitMQ` decouples upload requests from background processing.

Detailed file-by-file project planning lives in:
- [docs/repo-structure.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/repo-structure.md)
- [docs/mvp-backlog.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/mvp-backlog.md)
- [docs/project-context.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/project-context.md)
- [docs/dev-workflow.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/dev-workflow.md)
- [docs/queue-contract.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/queue-contract.md)
- [docs/food-data-sources.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/food-data-sources.md)

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
- switchable storage backend: local files for development and S3 for AWS runs
- RabbitMQ publisher for meal-analysis and food-reference import tasks
- RabbitMQ consumer microservices under `consumers/`
- switchable meal classifier: filename-based stub for local tests or AWS Rekognition for AWS-backed runs
- DB-backed food label resolution and rule-based calorie estimation through `food_reference`
- `uv`-managed local environment and lockfile for reproducible setup

Current status:
- the main API producer side is functionally complete for the current MVP architecture
- the API owns auth, meal upload, history, summary, PostgreSQL writes, and RabbitMQ task publishing
- the API does not consume RabbitMQ tasks
- meal analysis and food-reference importing are implemented as separate RabbitMQ consumer microservices under `consumers/`
- AWS-backed upload and recognition works through S3 plus Rekognition when the relevant env vars and IAM permissions are configured
- the main remaining data task is expanding `food_reference` with enough labels and calorie estimates for the foods Rekognition commonly returns

Implemented API endpoints:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/health`
- `POST /api/v1/meals`
- `GET /api/v1/meals`
- `GET /api/v1/meals/{meal_id}`
- `GET /api/v1/summary/daily`
- `POST /api/v1/food-reference/imports`

Run locally:

```bash
createdb foodsnap_ml
cp .env.example .env
uv sync --extra dev
docker compose up -d rabbitmq
uv run ./scripts/migrate.sh
uv run ./scripts/run-api.sh
```

The default local setup expects PostgreSQL running on your current machine and uses the local database `foodsnap_ml` through the default socket connection.

Environment setup:

```bash
cp .env.example .env
```

`docker-compose.yml` currently provides local RabbitMQ. Local-on-machine PostgreSQL is still the primary database debug setup for now.

Run consumer microservices with Docker Compose:

```bash
docker compose up --build meal-analysis-consumer food-reference-import-consumer
```

Build the consumer images directly:

```bash
docker build -f docker/Dockerfile.meal-analysis-consumer -t foodsnap-meal-analysis-consumer:local .
docker build -f docker/Dockerfile.food-reference-import-consumer -t foodsnap-food-reference-import-consumer:local .
```

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

## RabbitMQ workflow

Start RabbitMQ locally:

```bash
docker compose up -d rabbitmq
```

The API publishes meal-analysis messages to:

```text
foodsnap.meal_analysis
```

The API publishes food-reference import messages to:

```text
foodsnap.food_reference_import
```

Message contract details are documented in [docs/queue-contract.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/queue-contract.md).

## Remaining Work

Remaining API-side work:
- add an API Dockerfile for deployment
- add RabbitMQ connectivity to health/readiness checks
- consider an outbox pattern for stronger DB plus queue consistency
- restrict food-reference imports to admin/internal users later

Next major work outside the HTTP API:
- add production retry/dead-letter handling for the consumer microservices
- expand and curate `food_reference` using USDA FoodData Central import jobs
- add deployment infrastructure for API, workers, database, broker, and storage

## Storage Workflow

Local development uses:

```text
STORAGE_BACKEND=local
```

AWS-backed runs can use:

```text
STORAGE_BACKEND=s3
S3_BUCKET_NAME=your-bucket-name
S3_UPLOAD_PREFIX=meal-uploads
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_SESSION_TOKEN=
```

The S3 backend stores uploads through `boto3` and saves meal image URLs as `s3://bucket/key`, which the meal-analysis consumer can later load.

For the current pet-project setup, local AWS credentials can live in the ignored `.env` file. Keep `AWS_SESSION_TOKEN` empty for long-lived IAM user keys, or fill it when using temporary session credentials. For production-style ECS runs, prefer task roles instead of static access keys.

## Recognition and Food Reference Workflow

Local runs can keep using:

```text
MEAL_CLASSIFIER_BACKEND=stub
```

AWS-backed recognition uses:

```text
MEAL_CLASSIFIER_BACKEND=aws_rekognition
```

The Rekognition classifier returns all detected labels as candidates. `CalorieEstimatorService` then resolves those candidates against `food_reference` with a database query, preserving the candidate order returned by Rekognition. If none of the candidates exist in `food_reference`, the meal falls back to `unknown`.

The initial seed data is intentionally small: burger, pizza, salad, pasta, sushi, steak, soup, banana, and unknown. The next useful data step is to import or curate more `food_reference` rows for common Rekognition labels.
