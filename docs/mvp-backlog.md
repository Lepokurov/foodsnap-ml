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

Already done:
- FastAPI project skeleton
- environment-based config
- basic logging
- health endpoint with live database connectivity check
- registration and login
- bearer-token protected meal and summary endpoints
- meal upload with local file persistence
- local `PostgreSQL` persistence for users, meals, predictions, and food reference data
- `SQLAlchemy` models and repository layer
- `Alembic` migration baseline
- seeded `food_reference` data
- RabbitMQ publisher for meal-analysis tasks
- RabbitMQ publisher for food-reference import tasks
- RabbitMQ consumer microservices for meal analysis and food-reference imports
- Dockerfiles for both consumer images
- stub dish recognition
- rule-based calorie estimation
- meal history, meal detail, and daily summary
- basic API and consumer smoke tests

Still not done:
- real `S3`
- API Dockerfile
- real food-data provider clients for the import consumer
- deployment infra baseline beyond local Compose

Current status summary:
- main API producer side is functionally complete for the current MVP architecture
- consumer microservice entrypoints are implemented in this repository
- remaining work is mostly storage, deployment, real provider integration, health/observability, and security hardening

Recommended rule for future threads:
- treat milestones `1` to `7` as functionally prototyped
- when continuing MVP work, prefer replacing stubs with real integrations over adding parallel duplicate code

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
- complete for local development
- local app, config, logging, health endpoint, `PostgreSQL`, and migrations exist
- production `RDS PostgreSQL` configuration is still pending

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
- complete with local `PostgreSQL` persistence

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
- complete with local storage and local `PostgreSQL`
- local storage is still used instead of `S3`

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
- complete for API-side publishing
- RabbitMQ publisher exists in this API service
- external consumer microservice is still pending
- meal status updates are persisted in `PostgreSQL` by processing logic

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
- complete with persisted prediction metadata
- classifier is filename-based heuristic logic for now

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
- complete with seeded `food_reference` table

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
- complete with queries backed by `PostgreSQL`

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
- not started

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
2. swap local storage stub for real `S3` integration
3. replace the food-reference import stub with real provider clients
4. add API containerization and deployment baseline
5. add retry/dead-letter handling for consumers
6. add stronger consistency and observability patterns when needed
