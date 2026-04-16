#!/usr/bin/env bash
set -euo pipefail

uvicorn --env-file .env app.main:app --reload
