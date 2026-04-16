# MVP Backlog

This backlog reflects the selected MVP architecture:
- `FastAPI`
- `PostgreSQL`
- `AWS S3`
- `AWS RDS PostgreSQL`
- `AWS ECS Fargate`
- `RabbitMQ`
- `AWS CloudWatch`

The focus is an end-to-end backend MVP, not maximum prediction accuracy.

## Current implementation snapshot

MVP backend status:
- [x] FastAPI project skeleton
- [x] environment-based config
- [x] basic logging
- [x] health endpoint with live database connectivity check
- [x] registration and login
- [x] bearer-token protected meal and summary endpoints
- [x] meal upload with switchable local/S3 persistence
- [x] local `PostgreSQL` persistence for users, meals, predictions, and food reference data
- [x] `SQLAlchemy` models and repository layer
- [x] `Alembic` migration baseline
- [x] seeded `food_reference` data
- [x] RabbitMQ publisher for meal-analysis tasks
- [x] RabbitMQ publisher for food-reference import tasks
- [x] RabbitMQ consumer microservices for meal analysis and food-reference imports
- [x] Dockerfiles for both consumer images
- [x] filename-based stub classifier for local tests
- [x] AWS Rekognition classifier backend
- [x] DB-backed label resolution from classifier candidates into `food_reference`
- [x] USDA FoodData Central import client for food-reference updates
- [x] rule-based calorie estimation
- [x] meal history, meal detail, and daily summary
- [x] basic API, consumer, storage, and food-data tests

Not blocking the local MVP, but still open:
- [ ] API Dockerfile
- [ ] broad curated `food_reference` coverage
- [ ] deployment infra baseline beyond local Compose
- [ ] production-style retry/dead-letter handling for consumers
- [ ] RabbitMQ connectivity in health/readiness checks
- [ ] stricter admin/internal authorization for food-reference imports

Current status summary:
- local backend MVP is functionally complete for the current architecture
- main API producer side is functionally complete
- consumer microservice entrypoints are implemented in this repository
- remaining work is mostly data coverage, deployment, health/observability, and security hardening

Recommended rule for future threads:
- treat milestones `1` to `7` as functionally prototyped
- when continuing MVP work, prefer expanding the existing provider/import and classifier flows over adding parallel duplicate code

## Milestone 1. Foundation

Goal: create a stable backend skeleton with clear configuration and persistence boundaries.

Tasks:
- initialize the FastAPI project structure
- set up configuration management through environment variables
- connect PostgreSQL
- configure migrations
- add basic logging
- add health check endpoints

Acceptance criteria:
- the app starts locally
- the app connects to PostgreSQL
- migrations can create the initial schema
- health endpoint reports a healthy application state

Current status:
- [x] complete for local development
- [x] local app, config, logging, health endpoint, `PostgreSQL`, and migrations exist
- [ ] production `RDS PostgreSQL` configuration is still pending

## Milestone 2. Authentication

Goal: support isolated user data and authenticated API access.

Tasks:
- implement user registration
- implement user login
- add password hashing
- add token-based authentication
- protect meal and summary endpoints

Acceptance criteria:
- a user can register and log in
- protected endpoints reject unauthenticated access
- user-specific data is isolated by user identity

Current status:
- [x] complete with local `PostgreSQL` persistence

## Milestone 3. Meal Upload Flow

Goal: accept food photos and create pending meal entries.

Tasks:
- add endpoint for food photo upload
- store file metadata and meal record in PostgreSQL
- upload original image to `S3`
- save meal status as `pending`
- return a meal identifier to the client

Acceptance criteria:
- a user can upload a food image
- the image is persisted in storage
- a `meal_entry` is created in the database
- the response contains enough data to poll or fetch the meal later

Current status:
- [x] complete with local storage or S3, depending on `STORAGE_BACKEND`
- [x] S3-backed upload works when bucket, region, and credentials are configured

## Milestone 4. Asynchronous Processing

Goal: decouple upload from meal analysis.

Tasks:
- send meal-analysis tasks to `RabbitMQ`
- keep the API as a producer only
- define the contract for separate consumer microservices
- load the meal entry and image during processing
- update meal status to `processing`, then `done` or `failed`
- log task outcomes

Acceptance criteria:
- each upload enqueues a processing task
- the API publishes a durable RabbitMQ message
- the separate consumer can consume and process tasks
- task failures do not crash the whole service
- meal status reflects the processing lifecycle

Current status:
- [x] complete for API-side publishing
- [x] RabbitMQ publisher exists in this API service
- [x] external RabbitMQ consumer microservice exists under `consumers/meal_analysis`
- [x] meal status updates are persisted in `PostgreSQL` by processing logic

## Milestone 5. Dish Recognition

Goal: produce the first meaningful recognition result.

Tasks:
- define normalized dish labels
- implement a classifier integration interface
- store recognized label and confidence
- persist model version or prediction metadata

Acceptance criteria:
- the worker writes a recognized dish label for supported cases
- the result includes confidence information
- prediction metadata is stored for future debugging and model iteration

Current status:
- [x] complete with persisted prediction metadata
- [x] classifier backend is switchable between filename-based stub and AWS Rekognition
- [x] Rekognition labels are returned as candidates and resolved through `food_reference`

Notes:
- initial implementation may use a placeholder recognizer or lightweight pre-trained integration
- model quality is secondary to pipeline completeness in MVP

## Milestone 6. Calorie Estimation

Goal: convert dish recognition into an approximate calorie value.

Tasks:
- create and seed `food_reference`
- map normalized labels to reference entries
- estimate calories using default serving assumptions
- save estimated calories on the meal entry

Acceptance criteria:
- processed meals contain an estimated calorie value
- unsupported dishes fall back to a clear default behavior
- the estimation logic is deterministic and inspectable

Current status:
- [x] complete with seeded `food_reference` table and DB-backed candidate matching
- [x] USDA FoodData Central import can update existing labels or insert missing labels
- [ ] still needs broader `food_reference` coverage for realistic foods

Notes:
- portion estimation from photo alone is out of scope for the first MVP
- the first version should be honest about approximation quality

## Milestone 7. History and Daily Summary

Goal: expose useful nutrition tracking outputs to the client.

Tasks:
- implement meal history endpoint
- implement meal detail endpoint
- implement daily calorie summary endpoint
- support filtering by date

Acceptance criteria:
- a user can view their saved meal history
- a user can retrieve a single processed meal
- a user can request a daily summary with total estimated calories

Current status:
- [x] complete with queries backed by `PostgreSQL`

## Milestone 8. Deployment Baseline

Goal: package the project in a way that is deployable to AWS.

Tasks:
- add Dockerfile for the API
- define infrastructure layout for `ECS`, `RDS`, `S3`, and `RabbitMQ`
- prepare environment variable contract for cloud deployment
- define logging flow to `CloudWatch`

Acceptance criteria:
- the app can be containerized
- infra layout is defined clearly enough for implementation
- deployment responsibilities of API and consumer microservices are separated

Current status:
- [ ] API Dockerfile is not implemented
- [ ] infrastructure layout is not implemented
- [ ] CloudWatch logging flow is not implemented
- [ ] production deployment remains post-MVP work

## Non-goals for the first MVP

- medically accurate calorie counting
- portion-size estimation from image geometry
- recommendation engine
- meal planning
- admin panel
- mobile app
- advanced analytics beyond daily summary
- multi-model ML experimentation platform

## Nice-to-have after MVP

- manual correction of recognized dish
- manual correction of calories or serving size
- weekly summary
- Redis caching for summary endpoints
- rate limiting
- retries and dead-letter queue handling
- basic observability dashboards

## Suggested implementation order

1. foundation with local `PostgreSQL` and migrations
2. expand `food_reference` with common Rekognition labels and USDA-backed calorie estimates
3. add retry/dead-letter handling for consumers
4. add API containerization and deployment baseline
5. configure production-style AWS roles, lifecycle rules, and deployment infrastructure
6. add stronger consistency and observability patterns when needed
