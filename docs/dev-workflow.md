# Development Workflow

This document fixes the chosen local development standard for the project.

## Decision

The project uses `uv` as the primary Python workflow tool.

That means:
- `uv` is responsible for environment creation and synchronization
- `uv` is the default way to install dependencies
- `uv` is the default way to run project commands
- the project keeps dependency metadata in `pyproject.toml`
- the project should keep a lockfile in `uv.lock`

## Why `uv`

Reasons for choosing it:
- it is currently one of the most modern and widely adopted Python workflows for new projects
- it reduces the amount of separate tooling needed for virtualenv, install, sync, and command execution
- it fits well with a `FastAPI` backend project and future containerized deployment
- it works cleanly with `pyproject.toml`

## Environment standard

Local environment standard:
- Python `3.11+`
- local virtual environment in `.venv`
- dependencies declared in `pyproject.toml`
- locked dependency graph in `uv.lock`

Recommended rule:
- do not use ad-hoc global `pip install`
- do not rely on manually activated random virtualenvs outside the repo
- prefer `uv run ...` for local commands

## Local workflow

Current default commands:

```bash
uv sync --extra dev
uv run ./scripts/run-api.sh
uv run pytest
```

Later, after linting is added:

```bash
uv run ruff check .
uv run ruff format .
```

## Infra workflow

The intended split is:
- `uv` for Python application workflow
- local infrastructure through `Docker Compose` when `PostgreSQL` and other services are introduced
- Docker images for deployment to `ECS Fargate`

This means local development should eventually look like:
1. infrastructure starts via `Docker Compose`
2. application code runs through `uv run`
3. tests also run through `uv run`

## What not to use as the main standard

Not selected as the project default:
- `Poetry`
- `PDM`
- raw `pip` + manually managed `venv`

These tools are not forbidden, but they should not become the primary project workflow.

## Implication for future threads

When making setup, dependency, test, or local-run changes:
- prefer `uv` commands in docs and scripts
- keep `pyproject.toml` as the canonical dependency file
- assume `.venv` and `uv.lock` are the target local standard

## Next practical setup step

This step is already completed:
- `pyproject.toml` is aligned with `uv`
- `uv.lock` is generated and committed
- local setup works through `uv sync --extra dev`
- local commands run through `uv run`

Next tooling steps after that:
- add `ruff`
- later add local infra via `Docker Compose`
