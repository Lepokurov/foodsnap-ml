#!/usr/bin/env bash
set -euo pipefail

cat <<EOF
This API service no longer owns the meal-analysis worker.

The API publishes JSON messages to RabbitMQ and an external worker microservice
should consume the queue, process the meal, and update PostgreSQL.

Queue: ${RABBITMQ_MEAL_ANALYSIS_QUEUE:-foodsnap.meal_analysis}
Message shape:
{
  "event_type": "meal.analysis.requested",
  "version": 1,
  "meal_id": "meal_xxx",
  "occurred_at": "2026-04-15T12:00:00+00:00"
}
EOF
