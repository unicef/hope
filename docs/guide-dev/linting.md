---
title: Linting
---

# Code Quality

HOPE uses automated tools to maintain code quality and consistent formatting.

## Tools

| Tool | Purpose |
|------|---------|
| **ruff** | Python linter and formatter (replaces flake8, isort, black) |
| **pre-commit** | Git hooks for automated checks |
| **mypy** | Static type checking |

## Running Lint Checks

### Using tox

```bash
tox -e lint
```

This runs all pre-commit hooks on all files, including:
- ruff linting
- ruff formatting
- Other configured checks

### Auto-fix Issues

```bash
tox -e clean
```

This automatically fixes:
- Linting issues (where possible)
- Code formatting

## Pre-commit Hooks

Pre-commit runs checks automatically before each commit.

### Installation

```bash
pre-commit install
```

### Manual Run

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run a specific hook
pre-commit run ruff --all-files
```

### Configuration

Pre-commit hooks are configured in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Ruff

Ruff is an extremely fast Python linter and formatter.

### Running ruff Directly

```bash
# Check for issues
ruff check src tests

# Fix issues automatically
ruff check --fix src tests

# Format code
ruff format src tests
```

### Configuration

Ruff is configured in `ruff.toml`:

```toml
line-length = 120
target-version = "py313"

[lint]
select = ["E", "F", "W", "I", "UP", "B", "C4", ...]
ignore = [...]
```

## Type Checking with mypy

### Running mypy

```bash
tox -e mypy
```

Or directly:

```bash
mypy src
```

### Configuration

mypy is configured in `mypy.ini`:

```ini
[mypy]
python_version = 3.13
plugins = mypy_django_plugin.main
```

## IDE Integration

### VS Code

Install extensions:
- **Ruff** (charliermarsh.ruff)
- **Pylance** (ms-python.vscode-pylance)

Settings (`.vscode/settings.json`):
```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  }
}
```

### PyCharm

1. Go to **Settings > Plugins**
2. Install **Ruff** plugin
3. Enable **Ruff** in **Settings > Tools > Ruff**

## Common Issues

### Import Order

Ruff automatically sorts imports. If you see import order errors:

```bash
ruff check --fix --select I src
```

### Line Length

Default line length is 120 characters. Long lines will be flagged:

```bash
ruff check --select E501 src
```

### Unused Imports

```bash
ruff check --select F401 --fix src
```

## CI/CD

Lint checks run automatically in CI. PRs must pass all lint checks to be merged.

The CI runs:
```bash
tox -e lint
```

Ensure you run this locally before pushing to avoid CI failures.
