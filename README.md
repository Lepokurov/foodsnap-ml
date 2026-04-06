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

## MVP principles

- Prefer a complete working pipeline over high ML accuracy.
- Keep calorie estimation approximate and transparent.
- Store enough metadata to improve the ML pipeline later.
- Use AWS services that are practical for a backend-focused pet project.
- Defer non-essential complexity until after the first end-to-end version works.

## Current local MVP

The repository now contains a first API implementation focused on speed of iteration:
- `FastAPI` application scaffold under `app/`
- in-memory persistence instead of `PostgreSQL`
- local file storage stub under `data/uploads` instead of `S3`
- in-memory async queue plus background worker instead of `SQS`
- stub classifier and rule-based calorie estimator for end-to-end meal processing

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
python3 -m pip install -e '.[dev]'
./scripts/run-api.sh
```
