#!/usr/bin/env bash
set -euo pipefail

cat <<EOF
Meal-analysis consumer is now a separate microservice entrypoint.

Run locally:
  uv run python -m consumers.meal_analysis.main

Run with Docker Compose:
  docker compose up --build meal-analysis-consumer

Queue: ${RABBITMQ_MEAL_ANALYSIS_QUEUE:-foodsnap.meal_analysis}
EOF
