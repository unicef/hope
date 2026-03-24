---
title: Contributing
---

# Contributing

Thank you for your interest in contributing to HOPE! This guide outlines the process and requirements for contributions.

## Getting Started

1. [Set up your development environment](setup.md)
2. Fork the repository on GitHub
3. Create a feature branch from `develop`
4. Make your changes
5. Submit a pull request

## Pull Request Requirements

All pull requests must meet these criteria before merging:

### Code Coverage

- **95% coverage** on new/modified code is required
- Run coverage locally to verify:
  ```bash
  .tox/pytest/bin/pytest tests/unit --cov=src/hope --cov-report=term-missing --cov-fail-under=95
  ```

### Code Quality

- All lint checks must pass:
  ```bash
  tox -e lint
  ```
- Pre-commit hooks should be installed:
  ```bash
  pre-commit install
  ```

### Reviews

- **Two approving reviews** are required before merging
- Address all reviewer comments

### Tests

- All existing tests must pass
- New functionality must include tests
- Run tests locally:
  ```bash
  tox -e pytest
  ```

## Branch Naming

Use descriptive branch names following this pattern:

```
<type>/<ticket-id>-<short-description>
```

Examples:
- `feat/AB#12345-add-user-export`
- `fix/AB#12346-payment-calculation`
- `refactor/AB#12347-cleanup-models`

Types:
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `docs` - Documentation only
- `test` - Adding tests
- `chore` - Maintenance tasks

## Commit Messages

Write clear, descriptive commit messages:

```
<type>: <short description>

<optional longer description>

<optional ticket reference>
```

Example:
```
feat: Add CSV export for household data

Implements export functionality for household listings with
configurable columns and date range filtering.

Ref: AB#12345
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feat/AB#12345-my-feature
```

### 2. Make Changes

- Write code following project conventions
- Add tests for new functionality
- Update documentation if needed

### 3. Run Checks Locally

```bash
# Lint
tox -e lint

# Tests
tox -e pytest

# Or run specific tests
.tox/pytest/bin/pytest tests/unit/path/to/test.py -v
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: Add my feature"
git push origin feat/AB#12345-my-feature
```

### 5. Create Pull Request

- Open PR against `develop` branch
- Fill in the PR template
- Link related issues/tickets
- Request reviews

## Code Style

### Python

- Follow PEP 8 (enforced by ruff)
- Use type hints where practical
- Maximum line length: 120 characters
- Use docstrings for public functions

### JavaScript/TypeScript

- Follow ESLint configuration
- Use TypeScript for new code
- Prefer functional components in React
- Use React Query for data fetching

## Testing Guidelines

### Unit Tests

- Test one thing per test
- Use descriptive test names
- Use fixtures and factories for test data
- Mock external dependencies

Example:
```python
def test_household_total_members_returns_correct_count(household_factory):
    household = household_factory(members_count=5)
    assert household.total_members == 5
```

### Integration Tests

- Test component interactions
- Use realistic test scenarios
- Clean up test data

## Questions?

- Open an issue on GitHub for bugs or feature requests
- Check existing issues before creating new ones
- Join discussions in pull requests

## License

By contributing, you agree that your contributions will be licensed under the project's license.
