---
title: Testing
---

# Testing

## Test structure

```
tests/
├── unit/           # Unit tests (isolated, need services)
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

### Test sharding in CI

The unit and Selenium CI jobs are each split across several runners (`matrix.group` in
`.github/workflows/unit-tests.yml` and `.github/workflows/tests.yml`) with
[pytest-split](https://github.com/jerry-git/pytest-split), which balances the shards using per-test durations stored in `tests/unit/test_durations.json`
and `tests/e2e/test_durations.json`.

The files don't need updating on every PR — tests missing from them still run and are
assigned the average duration. Regenerate a file when its suite changes noticeably
(many tests added, removed or moved) or when the shards' run times in CI drift apart.

E2E:

```bash
tox -e tests -- pytest tests/e2e -m selenium --headless -n auto --dist=loadgroup --no-migrations --create-db \
    --store-durations --clean-durations --durations-path tests/e2e/test_durations.json
```

Unit:

```bash
tox -e tests -- pytest tests/unit -m unit -n auto --dist=loadgroup --no-migrations --create-db \
    --store-durations --clean-durations --durations-path tests/unit/test_durations.json
jq -S 'with_entries(select(.value >= 0.5) | .value |= (. * 1000 | round / 1000))' \
    tests/unit/test_durations.json > durations.tmp && mv durations.tmp tests/unit/test_durations.json
```

`--clean-durations` drops entries for tests that no longer exist; without it new
timings are merged into the existing file.

The unit file keeps only tests taking at least 0.5 s: with thousands of tests the full
file would be too large, and the fast ones balance out by count. As a side effect, the
"estimated duration" pytest-split prints for unit shards is far too high. Keep the
`@elasticsearch` suffixes in the test IDs; xdist adds them and pytest-split matches on them.

## Coverage

Pull requests must maintain **100% patch coverage** on lines changed vs.
`develop`. Check locally before pushing:

```bash
tox -e patch-coverage
```

The repo-wide floor in `.coveragerc` (`fail_under = 15`) is a safety net only;
the 100% patch-coverage gate is what CI enforces on new code (via Codecov,
configured in `codecov.yml`).

## Conventions

These criteria come from architecture and apply across the test suite (unit and
e2e).

### Test design

- Tests should be named in Arrange-Act-Assert fashion.
- Test should be written as functions, not classes.
- One test - one scenario. Use `pytest.mark.parametrize` for variations, not loops.
- Tests should not contain `if`/`for`/`while` statements.
- Tests should be deterministic. If using random, make sure that generator is seeded.
- Don't try to keep tests DRY. It's OK to have redundancy in test bodies as long as it's easy to read it.

### Test data and fixtures

- Test data should be created ONLY in fixtures by using factories (no `loaddata` or global setup).
- Don't use `autouse=True` for fixtures.
- Data used for test setup should be as minimal as possible.
- Factories should be used in fixtures, not in tests.
- Utils can be created only in `extras/test_utils`.
- We have global conftests defined for both `e2e`/`ut` but try to place dedicated fixtures in test files.

### Mocking

- Mock only external deps (network, S3, Celery). Never mock code under test.

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

- `tests/unit/apps/` mirrors `src/hope/apps/` — one test directory per app.
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
