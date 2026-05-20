# AGENTS.md

## Project Overview

HOPE (Humanitarian Cash Operations and Programme Ecosystem) is UNICEF's platform for managing humanitarian cash transfers across 20+ countries. It handles beneficiary registration, program management, payment processing, grievance handling, and compliance.

**Stack**: Python 3.14, Django 5.2+, DRF, Celery, PostgreSQL, Redis, Elasticsearch 8.14, React frontend (Bun/Vite).

## Development Setup

Services run via Docker Compose; backend runs locally with `uv`:

```bash
# Start services (PostgreSQL 14.3, Redis, Elasticsearch 8.14)
docker compose -f development_tools/compose.yml up -d

# Create venv and install dependencies
uv sync

# On macOS, may need to export GEOS_LIBRARY_PATH and GDAL_LIBRARY_PATH in your shell
```

### Running Locally

On macOS, prefix Python commands with `DYLD_FALLBACK_LIBRARY_PATH=$(brew --prefix)/lib` so the GEOS/GDAL native libs resolve.

```bash
# Run migrations
uv run python manage.py migrate

# Check for missing migrations
uv run python manage.py makemigrations --check

# Seed demo data (preserves existing db)
uv run python manage.py initdemo --skip-drop

# Django backend on :8080
uv run python manage.py runserver 0.0.0.0:8080 --classic

# Frontend (Vite) on :3000
cd src/frontend && bun run dev
```

**Local URLs:**
- Backend: http://localhost:8080
- Frontend (Vite): http://localhost:3000 — use this for FE dev; port 8080 serves stale builds
- Django Admin: http://localhost:8080/api/unicorn/ — login with `root` / `root1234` (the main `/login/` uses Azure AD OAuth)

### Running Tests Locally

```bash
# Unit tests (parallel, 8 workers, via tox)
uv run tox -e tests -- pytest tests/unit -q -rfE --no-header --tb=short \
    --no-migrations --randomly-seed=42 --dist=loadgroup --create-db -n 8

# E2E Selenium tests
uv run tox -e tests -- pytest tests/e2e -q -rfE --no-header --tb=short \
    --no-migrations --randomly-seed=42 --dist=loadgroup --create-db -n auto
```

## Lint and Type Checking

```bash
# Lint (ruff via pre-commit)
uv run tox -e lint

# Type checking
uv run tox -e mypy
```

## Architecture

### Centralized Models Pattern

Models are defined in individual files under `src/hope/models/` (not in app-specific `models.py` files), with the exception of `grievance` which has models in `src/hope/apps/grievance/models.py`. Each model file sets `app_label` in its Meta class to route it to the correct Django app. The `src/hope/models/__init__.py` re-exports everything via wildcard imports.

All model imports should use: `from hope.models import ModelName`

### Django Apps (`src/hope/apps/`)

Key domain apps: `payment`, `household`, `program`, `targeting`, `grievance`, `accountability`, `registration_data`, `registration_datahub`, `geo`, `sanction_list`, `steficon` (business rules engine).

Each app contains: services, tasks (Celery), admin customization, and REST API views. Admin is heavily customized in `src/hope/admin/`.

### Settings

Settings are in `src/hope/config/settings.py` with fragment modules in `src/hope/config/fragments/` (celery, elasticsearch, DRF, sentry, storages, etc.). Environment variables are managed via `src/hope/config/env.py`.

### API Structure

REST API mounted at `/api/rest/` via `src/hope/api/urls.py`. Uses DRF ViewSets with drf-spectacular for OpenAPI docs. All non-API routes fall through to the React SPA.

### Key External Integrations

- **Azure AD**: OAuth2 authentication
- **Kobo**: Data collection forms
- **Aurora**: Registration integration (`src/hope/contrib/aurora/`)
- **RapidPro**: Messaging
- **Elasticsearch**: Full-text search and deduplication

## Testing

See @docs/guide-dev/testing.md for how to run tests, coverage requirements, conventions (Arrange-Act-Assert, factories-in-fixtures, no-superuser, e2e selector rules), and test infrastructure.

## Skills

Multi-step procedures (review flows, scaffolding routines, etc.) live under
`.agents/` — see `.agents/README.md` for the convention.
