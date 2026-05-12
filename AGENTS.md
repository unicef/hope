# AGENTS.md

## Project Overview

HOPE (Humanitarian Cash Operations and Programme Ecosystem) is UNICEF's platform for managing humanitarian cash transfers across 20+ countries. It handles beneficiary registration, program management, payment processing, grievance handling, and compliance.

**Stack**: Python 3.13, Django 5.2+, DRF, Celery, PostgreSQL, Redis, Elasticsearch 8.14, React frontend (Bun/Vite).

## Development Setup

Services run via Docker Compose, backend runs locally with direnv + venv:

```bash
# Start services (PostgreSQL 14.3, Redis, Elasticsearch 8.14)
docker compose -f development_tools/compose.yml up -d

# Backend setup - direnv loads .envrc which creates/activates venv
cp .envrc.example .envrc
direnv allow

# Install dependencies
uv sync

# On macOS, may need to uncomment GEOS_LIBRARY_PATH and GDAL_LIBRARY_PATH in .envrc
```

## Lint and Type Checking

```bash
# Lint (ruff via pre-commit)
direnv exec . tox -e lint

# Type checking
direnv exec . tox -e mypy
```

## Code Style

- **Ruff** with 120-char line length, config in `ruff.toml`
- Double quotes, space indentation
- isort with first-party packages: `hope`, `extras`, `e2e`
- Pre-commit hooks enforce formatting - run `tox -e lint` before committing

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
`agents/` — see `agents/README.md` for the convention.
