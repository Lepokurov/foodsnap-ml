# Project Context

This file is a durable short-form briefing for future threads. It is meant to be read quickly before making product, backend, or infrastructure decisions.

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

Reasoning:
- `SQS` fits the AWS learning goal better
- the system stays simpler operationally
- Redis can be introduced later when caching or throttling becomes useful

## MVP scope

Included:
- user registration and login
- upload food photo
- store image in `S3`
- create meal entry in `PostgreSQL`
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
- `PostgreSQL` for primary data
- `S3` for original image storage
- `SQS` for background jobs

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

## Current planning artifacts

Primary docs to read next:
- [README.md](/Users/andreylepokurov/projects/work/aws-pet-proj/README.md)
- [repo-structure.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/repo-structure.md)
- [mvp-backlog.md](/Users/andreylepokurov/projects/work/aws-pet-proj/docs/mvp-backlog.md)

## Immediate next step

The next implementation phase should start from project scaffolding only:
- create the FastAPI application skeleton
- define models and migrations
- prepare local development setup

No application code has been created yet at the time of writing this document.
