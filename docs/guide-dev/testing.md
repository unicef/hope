---
title: Testing
---

# Testing

HOPE uses pytest for testing with tox as the test runner.

## Test Structure

```
tests/
├── unit/           # Unit tests
│   ├── apps/       # Tests organized by Django app
│   └── ...
└── e2e/            # End-to-end tests (Selenium)
```

## Running Unit Tests

### Using tox (Recommended)

```bash
tox -e pytest
```

This runs all unit tests with the correct environment configuration.

### Running Specific Tests

Use the tox-created pytest binary directly:

```bash
# Run a specific test file
.tox/pytest/bin/pytest tests/unit/apps/household/test_models.py -v

# Run a specific test class
.tox/pytest/bin/pytest tests/unit/apps/household/test_models.py::TestHousehold -v

# Run a specific test method
.tox/pytest/bin/pytest tests/unit/apps/household/test_models.py::TestHousehold::test_create -v

# Run tests matching a pattern
.tox/pytest/bin/pytest tests/unit -k "test_create" -v
```

### Using direnv with pytest

With direnv active, you can also run:

```bash
direnv exec . .tox/pytest/bin/pytest tests/unit/path/to/test.py -v
```

### Common pytest Options

| Option | Description |
|--------|-------------|
| `-v` | Verbose output |
| `-vv` | More verbose output |
| `-x` | Stop on first failure |
| `-k "pattern"` | Run tests matching pattern |
| `--pdb` | Drop into debugger on failure |
| `-n auto` | Run tests in parallel |
| `--reruns 3` | Retry failed tests 3 times |

### Example: Running with Coverage

```bash
.tox/pytest/bin/pytest tests/unit --cov=src/hope --cov-report=html
```

## Running Tests with Docker

```bash
cd development_tools
docker compose run --rm backend pytest -n auto --reruns 3 -rP -p no:warnings --capture=sys ./tests/unit
```

## End-to-End Tests (Selenium)

Selenium tests run on the host machine due to ARM64 architecture limitations in Docker.

### Prerequisites

1. Services running (PostgreSQL, Redis, Elasticsearch)
2. Chrome/Chromium browser installed

### Setup

```bash
# macOS - install system requirements
brew install wkhtmltopdf pango postgis gdal

# Create and activate virtual environment
uv venv .venv --python 3.13
source .venv/bin/activate
uv sync
```

### Running E2E Tests

```bash
# Start services
cd development_tools
docker compose up db redis elasticsearch -d

# Run tests
python -m pytest -svvv tests/e2e --html-report=./report/report.html
```

## Coverage Requirements

Pull requests must maintain **95% code coverage** on new code to be merged.

Check coverage locally:

```bash
.tox/pytest/bin/pytest tests/unit --cov=src/hope --cov-report=term-missing --cov-fail-under=95
```

## Test Configuration

Test configuration is defined in `tox.ini`:

```ini
[testenv:pytest]
runner = uv-venv-lock-runner
description = Run unit tests
set_env =
    CELERY_TASK_ALWAYS_EAGER = true
    DATABASE_URL = postgres://postgres:postgres@localhost:5432/postgres
    ...
commands =
    pytest --no-migrations -q --create-db {posargs: ./tests/unit}
```

Key settings:
- `--no-migrations` - Uses test database without running migrations
- `--create-db` - Creates fresh test database
- `--reruns 3` - Retries flaky tests
- `--randomly-seed=42` - Deterministic test order

## Debugging Tests

### Using pdb

```bash
.tox/pytest/bin/pytest tests/unit/path/to/test.py -v --pdb
```

### Using ipdb

Set breakpoint in code:
```python
import ipdb; ipdb.set_trace()
```

Then run:
```bash
.tox/pytest/bin/pytest tests/unit/path/to/test.py -v -s
```

### Environment Variable for Debugging

```bash
export PYTHONBREAKPOINT=ipdb.set_trace
```
