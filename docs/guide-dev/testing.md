---
title: Testing
---

# Testing

## Test structure

```
tests/
├── unit/           # Unit tests (isolated, fast)
└── e2e/            # End-to-end tests (Selenium, needs running services)
```

## Running tests

All tests run through the `tests` tox env — unit and e2e are the same env with
different paths.

```bash
# All unit tests
tox -e tests -- tests/unit

# All e2e (Selenium) tests
tox -e tests -- tests/e2e

# A specific file, class, or method (pytest node-id syntax)
tox -e tests -- tests/unit/apps/household/test_models.py::TestHousehold::test_create

# Filter by name pattern
tox -e tests -- tests/unit -k "test_create"
```

E2E tests require Postgres, Redis, and Elasticsearch to be running locally — see
`development_tools/compose.yml`.

## Coverage

Pull requests must maintain **97% patch coverage** on lines changed vs.
`develop`. Check locally before pushing:

```bash
tox -e patch-coverage
```

The repo-wide floor in `.coveragerc` (`fail_under = 15`) is a safety net only;
the 97% gate is what CI enforces on new code (via Codecov, configured in
`codecov.yml`).

## Conventions

These criteria come from architecture and apply across the test suite (unit and
e2e).

### Test design

- Tests should be named in Arrange-Act-Assert fashion.
- Test should be written as functions, not classes.
- One test - one scenario.
- Tests should not contain `if`/`for`/`while` statements.
- Tests should be stable and deterministic.
- Don't try to keep tests DRY. It's OK to have redundancy in test bodies as long as it's easy to read it.

### Test data and fixtures

- Test data should be created ONLY in fixtures by using factories (no `loaddata` or global setup).
- Don't use `autouse=True` for fixtures.
- Data used for test setup should be as minimal as possible.
- Factories should be used in fixtures, not in tests.
- Utils can be created only in `extras/test_utils`.
- We have global conftests defined for both `e2e`/`ut` but try to place dedicated fixtures in test files.

### Mocking

- Mock only external deps (network, S3).

### Permissions

- Do not use superuser for tests. Use no-permission user, test always for no-perm/perm behaviour, use context manager to add required perm.

### E2E selectors

- Don't use xpath.
- Don't use `sleep` in tests.
- Remove constants, move selectors directly to the tests.
- Don't search twice for the object. Save it somewhere instead.
- Prefer to use input `name` (less expensive identifier) instead of `data-cy`.
- Don't use CSS classes for identifying an object. Use them only if there is no `id`/`name`.

## Test infrastructure

- Tests in `tests/unit/` mirror the app structure under `tests/unit/apps/`.
- API contract tests in `tests/unit/api_contract/`.
- Factories in `tests/extras/test_utils/factories/` (factory-boy) and legacy ones in `tests/extras/test_utils/old_factories/`.
- Fixtures in `tests/extras/test_utils/fixtures/`.
- Auto-created fixtures per test: UNICEF Partner, Role with all permissions, cleared cache.
- Activity logging is disabled by default in tests; use `@pytest.mark.enable_activity_log` to enable.
- ES is disabled by default (`ELASTICSEARCH_DSL_AUTOSYNC = False`); use `django_elasticsearch_setup` fixture or `mock_elasticsearch` fixture.
- `DJANGO_SETTINGS_MODULE=hope.config.settings`.
- `CELERY_TASK_ALWAYS_EAGER=true` in tests.
- Tests use `--no-migrations` with a custom `sync_apps` patch in `tests/unit/conftest.py` to handle the centralized models pattern (models live under `src/hope/models/`).
- Use the `db` fixture, not `transaction=True` / `transactional_db`.
- Use `django_assert_num_queries` (or pytest-django's `assertNumQueries`) to assert query counts and catch N+1 regressions.
