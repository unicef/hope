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
the 97% gate is what CI enforces on new code.
