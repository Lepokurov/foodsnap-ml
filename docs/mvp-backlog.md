# MVP Backlog

This backlog reflects the selected MVP architecture:
- `FastAPI`
- `PostgreSQL`
- `AWS S3`
- `AWS RDS PostgreSQL`
- `AWS ECS Fargate`
- `AWS SQS`
- `AWS CloudWatch`

The focus is an end-to-end backend MVP, not maximum prediction accuracy.

## Current implementation snapshot

Already done in local stub form:
- FastAPI project skeleton
- environment-based config
- basic logging
- health endpoint
- registration and login
- bearer-token protected meal and summary endpoints
- meal upload with local file persistence
- in-memory async queue and background worker
- stub dish recognition
- rule-based calorie estimation
- meal history, meal detail, and daily summary
- basic API smoke tests

Still not done:
- real `PostgreSQL`
- migrations
- real `S3`
- real `SQS`
- Docker and infra baseline

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
- partially complete
- local app, config, logging, and health endpoint exist
- real database and migrations are still pending

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
- complete in stub form

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
- complete in stub form
- local storage and in-memory meal records are used instead of `S3` and `PostgreSQL`

## Milestone 4. Asynchronous Processing

Goal: decouple upload from meal analysis.

Tasks:
- send meal-analysis tasks to `SQS`
- create a worker process that consumes tasks
- load the meal entry and image during processing
- update meal status to `processing`, then `done` or `failed`
- log task outcomes

Acceptance criteria:
- each upload enqueues a processing task
- the worker can consume and process tasks
- task failures do not crash the whole service
- meal status reflects the processing lifecycle

Current status:
- complete in stub form
- in-memory queue replaces `SQS`

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
- complete in stub form
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
- complete in stub form

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
- complete in stub form

## Milestone 8. Deployment Baseline

Goal: package the project in a way that is deployable to AWS.

Tasks:
- add Dockerfiles for API and worker
- define infrastructure layout for `ECS`, `RDS`, `S3`, and `SQS`
- prepare environment variable contract for cloud deployment
- define logging flow to `CloudWatch`

Acceptance criteria:
- the app can be containerized
- infra layout is defined clearly enough for implementation
- deployment responsibilities of API and worker are separated

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

1. foundation
2. replace in-memory user and meal persistence with database repositories
3. add migrations and schema
4. swap local storage stub for real `S3` integration
5. swap in-memory queue for real `SQS`
6. keep worker flow and API contract stable during integration swap
7. add containerization and AWS deployment baseline
