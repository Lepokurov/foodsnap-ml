# Project Context

This file is a durable short-form briefing for future threads. It is meant to be read quickly before making product, backend, or infrastructure decisions.

## Current status

As of `2026-04-06`, the repository is no longer empty.

Implemented locally:
- `FastAPI` app scaffold
- auth endpoints: register and login
- protected meal endpoints: upload, list, detail
- daily summary endpoint
- background meal processing flow
- stub classifier and rule-based calorie estimation
- `uv` workflow with committed `uv.lock` and project-local `.venv`

Current temporary replacements:
- `PostgreSQL` -> in-memory store
- `S3` -> local file storage in `data/uploads`
- `SQS` -> in-memory async queue

Important note for future threads:
- the API pipeline works end-to-end locally
- current goal is not scaffolding anymore
- next work should build on the existing code, not recreate structure from scratch
- local Python setup should use `uv sync` and `uv run`, not ad-hoc `pip`

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
- `AWS SQS`
- `AWS CloudWatch`

Current decision:
- do not use `RabbitMQ` in MVP
- do not require `Redis` in MVP
- use local stubs first before wiring real AWS services and database
- use `uv` as the standard Python workflow tool

Reasoning:
- `SQS` fits the AWS learning goal better
- the system stays simpler operationally
- Redis can be introduced later when caching or throttling becomes useful
- `uv` gives a modern and practical standard for env, deps, lockfile, and command execution

## MVP scope

Included:
- user registration and login
- upload food photo
- store image in `S3` or local stub during development
- create meal entry in `PostgreSQL` or in-memory stub during development
- process meal asynchronously through a worker
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
- `Worker service` for async meal processing
- `PostgreSQL` for primary data in target architecture
- `S3` for original image storage in target architecture
- `SQS` for background jobs in target architecture

Current local implementation:
- in-memory state for users, meals, predictions, and food reference data
- local file storage stub for uploaded images
- in-memory queue plus background task worker

Flow:
1. user uploads a meal photo
2. API stores image in `S3`
3. API creates a `meal_entry` with status `pending`
4. API sends a task to `SQS`
5. worker consumes the task
6. worker runs recognition and calorie estimation
7. worker updates the meal record
8. user reads meal history and daily summary

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

## Current planning artifacts

Primary docs to read next:
- [README.md](/Users/andreylepokurov/projects/work/aws-pet-proj/README.md)
- [repo-structure.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/repo-structure.md)
- [mvp-backlog.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/mvp-backlog.md)
- [dev-workflow.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/dev-workflow.md)

## Immediate next step

The next implementation phase should continue from the current working stub MVP:
- replace in-memory persistence with database repositories
- introduce real `S3` integration behind the storage abstraction
- introduce real `SQS` integration behind the queue abstraction
- keep the existing API contract stable while swapping implementations
- keep `uv`, `pyproject.toml`, and `uv.lock` as the default local Python workflow
