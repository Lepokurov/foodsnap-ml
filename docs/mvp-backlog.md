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
2. auth
3. meal upload
4. queue + worker
5. recognition
6. calorie estimation
7. history + summary
8. containerization + AWS deployment
