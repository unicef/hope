---
title: Testing
---

# Testing

## Test Structure

```
tests/
├── unit/           # Unit tests
└── e2e/            # End-to-end tests (Selenium)
```

## Running Unit Tests

```bash
# Run all unit tests
tox -e pytest

# Run specific test file
tox -e pytest -- tests/unit/apps/household/test_models.py -v

# Run specific test class
tox -e pytest -- tests/unit/apps/household/test_models.py::TestHousehold -v

# Run specific test method
tox -e pytest -- tests/unit/apps/household/test_models.py::TestHousehold::test_create -v

# Run tests matching a pattern
tox -e pytest -- tests/unit -k "test_create" -v
```

## Running Tests with Docker

```bash
cd development_tools
docker compose run --rm backend pytest ./tests/unit
```

## End-to-End Tests (Selenium)

```bash
tox -e selenium
```

## Coverage Requirements

Pull requests must maintain **97% code coverage** on new code.
