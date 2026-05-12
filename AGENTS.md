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

## Build, Test, and Lint Commands

```bash
# Lint (ruff via pre-commit)
direnv exec . tox -e lint

# Run all unit tests (uses default flags from tox.ini)
direnv exec . tox -e tests

# Run specific test file (posargs replaces ALL default flags, so provide them)
direnv exec . tox -e tests -- pytest -q -rfE --no-header --tb=short --no-migrations --randomly-seed=42 --create-db tests/unit/apps/payment/test_models.py

# Run specific test by name
direnv exec . tox -e tests -- pytest -q -rfE --no-header --tb=short --no-migrations --randomly-seed=42 --create-db tests/unit/apps/payment/test_models.py -k test_payment_create

# Run tests for a specific app directory
direnv exec . tox -e tests -- pytest -q -rfE --no-header --tb=short --no-migrations --randomly-seed=42 --create-db tests/unit/apps/payment/

# E2E tests (selenium)
direnv exec . tox -e tests -- pytest -q -rfE --no-header --tb=short --no-migrations --randomly-seed=42 --create-db tests/e2e/

# Type checking
direnv exec . tox -e mypy
```

**Coverage**: Codecov requires **97% patch coverage** on PRs (configured in `codecov.yml`). Local coverage config is in `.coveragerc`.

## Code Style

- **Ruff** with 120-char line length, config in `ruff.toml`
- Double quotes, space indentation
- isort with first-party packages: `hope`, `extras`, `e2e`
- Pre-commit hooks enforce formatting - run `tox -e lint` before committing

## Architecture

### Centralized Models Pattern

Models are defined in individual files under `src/hope/models/` (not in app-specific `models.py` files), with the exception of `grievance` which has models in `src/hope/apps/grievance/models.py`. Each model file sets `app_label` in its Meta class to route it to the correct Django app. The `src/hope/models/__init__.py` re-exports everything via wildcard imports.

All model imports should use: `from hope.models import ModelName`

Tests use `--no-migrations` with a custom `sync_apps` patch in `tests/unit/conftest.py` to handle this pattern.

### Django Apps (`src/hope/apps/`)

Key domain apps: `payment`, `household`, `program`, `targeting`, `grievance`, `accountability`, `registration_data`, `registration_datahub`, `geo`, `sanction_list`, `steficon` (business rules engine).

Each app contains: services, tasks (Celery), admin customization, and REST API views. Admin is heavily customized in `src/hope/admin/`.

### Settings

Settings are in `src/hope/config/settings.py` with fragment modules in `src/hope/config/fragments/` (celery, elasticsearch, DRF, sentry, storages, etc.). Environment variables are managed via `src/hope/config/env.py`.

### API Structure

REST API mounted at `/api/rest/` via `src/hope/api/urls.py`. Uses DRF ViewSets with drf-spectacular for OpenAPI docs. All non-API routes fall through to the React SPA.

### Test Infrastructure

- Tests in `tests/unit/` mirror the app structure under `tests/unit/apps/`
- API contract tests in `tests/unit/api_contract/`
- Factories in `tests/extras/test_utils/factories/` (factory-boy) and legacy ones in `tests/extras/test_utils/old_factories/`
- Fixtures in `tests/extras/test_utils/fixtures/`
- Auto-created fixtures per test: UNICEF Partner, Role with all permissions, cleared cache
- Activity logging is disabled by default in tests; use `@pytest.mark.enable_activity_log` to enable
- ES is disabled by default (`ELASTICSEARCH_DSL_AUTOSYNC = False`); use `django_elasticsearch_setup` fixture or `mock_elasticsearch` fixture
- `DJANGO_SETTINGS_MODULE=hope.config.settings`
- `CELERY_TASK_ALWAYS_EAGER=true` in tests

### Test Conventions

- Tests are **only plain functions** (`def test_*`), never in classes. Split into separate files if needed for logical grouping.
- One test = one scenario. Follow **Arrange-Act-Assert** naming.
- No `if`/`for`/`while` in test bodies — use `pytest.mark.parametrize` instead.
- Test data is created **exclusively in fixtures** (no `loaddata`, no global setups). Factories must be used inside fixtures, never directly in tests.
- Fixtures must not use `autouse=True`.
- Fixtures must not be shared between test files — keep them local to each file.
- Use minimal data necessary for the scenario.
- Use `db` fixture, not `transaction=True` / `transactional_db`.
- Mock only external dependencies (network, S3, Celery/async, integrations). Never mock the code under test.
- If tests accidentally touch Elasticsearch (but don't test ES), mock ES using the project's existing `mock_elasticsearch` fixture.
- Do not create test utility modules.
- **Assert number of queries** — use `django_assert_num_queries` or `pytest-django`'s `assertNumQueries` to verify the expected query count. This catches N+1 regressions early.

### Key External Integrations

- **Azure AD**: OAuth2 authentication
- **Kobo**: Data collection forms
- **Aurora**: Registration integration (`src/hope/contrib/aurora/`)
- **RapidPro**: Messaging
- **Elasticsearch**: Full-text search and deduplication

## Further reading

@docs/guide-dev/testing.md

## Skills

Multi-step procedures (review flows, scaffolding routines, etc.) live under
`agents/` — see `agents/README.md` for the convention.
