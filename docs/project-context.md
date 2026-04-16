# Project Context

This file is a durable short-form briefing for future threads. It is meant to be read quickly before making product, backend, or infrastructure decisions.

## Current status

As of `2026-04-16`, the repository contains a working local MVP with real local `PostgreSQL` persistence, RabbitMQ publishing, and two RabbitMQ consumer microservices.

Implemented locally:
- `FastAPI` app scaffold
- auth endpoints: register and login
- protected meal endpoints: upload, list, detail
- daily summary endpoint
- meal-analysis task publishing flow
- `PostgreSQL` persistence for users, meals, predictions, and food reference data
- `SQLAlchemy` models and repository layer under `app/db/*`
- `Alembic` migrations under `migrations/*`
- local database health check in `GET /api/v1/health`
- RabbitMQ publisher for meal-analysis tasks
- RabbitMQ publisher for food-reference import tasks
- meal-analysis RabbitMQ consumer under `consumers/meal_analysis`
- food-reference import RabbitMQ consumer under `consumers/food_reference_import`
- Dockerfiles for both consumer images under `docker/`
- stub classifier and rule-based calorie estimation
- `uv` workflow with committed `uv.lock` and project-local `.venv`

Current temporary replacements:
- real nutrition provider calls -> deterministic local food-reference import stub

Important note for future threads:
- the API pipeline works end-to-end locally
- persistence is no longer in-memory; use the local `foodsnap_ml` PostgreSQL database
- the FastAPI service only publishes RabbitMQ tasks; consumers are separate microservice entrypoints in this repo
- the main API producer side is functionally complete for the current MVP architecture
- current goal is not scaffolding anymore
- next work should build on the existing code, not recreate structure from scratch
- local Python setup should use `uv sync` and `uv run`, not ad-hoc `pip`

API-side work still worth doing:
- add an API Dockerfile for deployment
- add RabbitMQ connectivity to health/readiness checks
- consider an outbox pattern for stronger DB plus queue consistency
- restrict food-reference imports to admin/internal users later
- configure real AWS bucket/IAM/lifecycle rules for S3 environments

## Project

Name: `FoodSnap ML`

Type: backend-focused pet project with AWS integration

Primary idea:
- a user uploads a food photo,
- the system tries to recognize the dish,
- the system estimates approximate calories,
- meal history is stored,
- the API returns daily calorie summaries.

## Chosen MVP variant

The selected implementation path is the practical AWS-first version:
- `FastAPI`
- `PostgreSQL`
- `AWS S3`
- `AWS RDS PostgreSQL`
- `AWS ECS Fargate`
- `RabbitMQ`
- `AWS CloudWatch`

Current decision:
- use `RabbitMQ` for meal-analysis task dispatch
- keep background work as separate consumer microservices under `consumers/`
- do not require `Redis` in MVP
- use local `PostgreSQL` directly on the development machine for debugging
- use `STORAGE_BACKEND=local` for local development and `STORAGE_BACKEND=s3` for AWS-backed upload storage
- use `uv` as the standard Python workflow tool

Reasoning:
- `RabbitMQ` is useful here to learn a real broker and keep the API/worker boundary explicit
- the API should not block HTTP requests while image analysis happens
- Redis can be introduced later when caching or throttling becomes useful
- `uv` gives a modern and practical standard for env, deps, lockfile, and command execution

## MVP scope

Included:
- user registration and login
- upload food photo
- store image in `S3` or local stub during development
- create meal entry in local `PostgreSQL`
- publish meal-analysis task to `RabbitMQ`
- publish food-reference import task to `RabbitMQ`
- let consumer microservices process tasks asynchronously
- store recognized label, confidence, and estimated calories
- fetch meal history
- fetch daily calorie summary

Explicitly out of scope for first version:
- accurate portion-size estimation from image alone
- advanced ML training pipeline
- recommendation system
- mobile client
- medically reliable nutrition output

## Product framing

The MVP should be presented as an approximate calorie tracker powered by photo-based dish recognition.

It should not claim:
- precise nutrition analysis
- medical accuracy
- guaranteed dish recognition

Preferred framing:
- "AI-assisted meal logging"
- "approximate calorie estimate"
- "daily food history and summary"

## Core architecture

Components:
- `API service` on `FastAPI`
- external `Worker service` for async meal processing
- `PostgreSQL` for primary data in target architecture
- `S3` for original image storage in target architecture
- `RabbitMQ` for background jobs in target architecture

Current local implementation:
- local `PostgreSQL` stores users, meals, predictions, and food reference data
- switchable storage backend with local filesystem for development and S3 for AWS-backed runs
- RabbitMQ publisher for meal-analysis and food-reference import tasks
- no embedded consumer inside the FastAPI service
- deployable RabbitMQ consumer entrypoints under `consumers/`

Flow:
1. user uploads a meal photo
2. API stores image through the configured storage backend
3. API creates a `meal_entry` in `PostgreSQL` with status `pending`
4. API publishes a JSON task to RabbitMQ
5. meal-analysis consumer microservice consumes the task
6. consumer runs recognition and calorie estimation
7. consumer updates the meal record and prediction metadata in `PostgreSQL`
8. user reads meal history and daily summary

## Local run

The current local database contract:
- database name: `foodsnap_ml`
- default connection string: `postgresql+psycopg:///foodsnap_ml`
- local machine `PostgreSQL`, not Docker, is the primary debug setup

Bootstrap and run:

```bash
createdb foodsnap_ml
cp .env.example .env
uv sync --extra dev
docker compose up -d rabbitmq
uv run ./scripts/migrate.sh
uv run ./scripts/run-api.sh
```

Run the consumer microservices with Docker Compose:

```bash
docker compose up --build meal-analysis-consumer food-reference-import-consumer
```

Verify database schema:

```bash
psql -d foodsnap_ml -c '\dt'
```

Run tests:

```bash
uv run pytest
```

## Data model summary

Planned key entities:
- `users`
- `meal_entries`
- `meal_predictions`
- `food_reference`

Important `meal_entries` fields:
- user reference
- image location
- processing status
- recognized label
- confidence
- estimated calories
- meal timestamp

## Engineering principles

- prefer complete end-to-end workflow over ML sophistication
- keep services separated by responsibility
- isolate AWS integrations behind service abstractions
- keep calorie estimation rule-based in MVP
- store metadata that will make later ML upgrades easier
- standardize local Python workflow around `uv`, `pyproject.toml`, and a project-local `.venv`
- use FastAPI dependency injection for API services, repositories, queue access, and request-scoped database sessions
- keep `get_db_session()` as the low-level database context manager for non-FastAPI consumers

## Current planning artifacts

Primary docs to read next:
- [README.md](/Users/andreylepokurov/projects/work/aws-pet-proj/README.md)
- [repo-structure.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/repo-structure.md)
- [mvp-backlog.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/mvp-backlog.md)
- [dev-workflow.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/dev-workflow.md)
- [queue-contract.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/queue-contract.md)
- [food-data-sources.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/food-data-sources.md)

## Immediate next step

The next implementation phase should continue from the current working local-Postgres MVP:
- replace the food-reference import stub with real provider clients
- add API Dockerfile and deployment baseline
- add retry/dead-letter handling for RabbitMQ consumers
- keep the existing API contract stable while swapping implementations
- keep `uv`, `pyproject.toml`, and `uv.lock` as the default local Python workflow
