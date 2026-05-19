---
name: write-uts
description: Generate a new pytest unit test for HOPE under tests/unit/. USE WHEN user asks to write, scaffold, add, or create a new unit test.
---

# write-uts

Generate a new HOPE unit test under `tests/unit/` that follows project rules and uses the shared factories/fixtures from `tests/extras/test_utils/`.

## Inputs from user

- **Module / endpoint / model / method under test** — what code is exercised
- **Scenario** — one behavior per test function (not a matrix)
- **Expected assertions** — what must be true at the end (status code, DB state, return value, raised exception, query count, ...)

If any of these is missing, ask for them before doing anything else.

## MANDATORY: read these before writing anything

1. `docs/guide-dev/testing.md` — project-wide test rules (especially **Conventions**, **Test data and fixtures**, **Mocking**, **Permissions**)
2. `.agents/write-uts/context.md` — HOPE-specific patterns: layout, fixtures, factories, permission helpers, ES/activity-log handling, mocking
3. At least one concrete example matching the kind of test you're writing:
   - API endpoint: `tests/unit/apps/grievance/test_create_feedback_ticket.py`
   - Model / domain logic: `tests/unit/apps/payment/test_model_account.py`
   - API contract (drf-api-checker): `tests/unit/api_contract/test_grievance_tickets.py`

Step 3 is non-optional. Existing tests show how the rules interact in practice.

## Procedure

1. **Location.** Mirror `src/hope/apps/<app>/...` under `tests/unit/apps/<app>/test_<feature>.py`. Non-app tests have dedicated homes: `tests/unit/api_contract/` (drf-api-checker contracts), `tests/unit/api/`, `tests/unit/models/`, `tests/unit/admin/`, `tests/unit/middlewares/`, `tests/unit/contrib/`.

2. **Scaffold the file:**
   ```python
   from typing import Any

   import pytest

   from extras.test_utils.factories import BusinessAreaFactory, UserFactory
   from hope.models import BusinessArea, User

   pytestmark = pytest.mark.django_db


   @pytest.fixture
   def business_area() -> BusinessArea:
       return BusinessAreaFactory(slug="afghanistan")


   @pytest.fixture
   def user() -> User:
       return UserFactory()


   def test_<scenario>(business_area: BusinessArea, user: User) -> None:
       # Arrange — request fixtures explicitly; build minimal data via factories
       # Act     — call the function / hit the endpoint / save the model
       # Assert  — one or more assertions on the observable outcome
   ```
   For API tests, request the `api_client` and `create_user_role_with_permissions` fixtures from the shared conftest — do not roll your own auth. See `context.md` for the canonical shape.

3. **Fill in the body following `testing.md` (rules) and `context.md` (fixtures, factories, permission helpers, ES/activity-log handling, mocking).** The mandatory reads above are not a suggestion.

## Verify before reporting done

```bash
# the file you just wrote (Makefile target)
make uts ARGS=tests/unit/apps/<app>/test_<feature>.py

# or the raw form CI uses
uv run tox -e tests -- pytest tests/unit/apps/<app>/test_<feature>.py

# 100% patch coverage on changed lines vs. develop — CI enforces this
uv run tox -e patch-coverage

# style + types
uv run tox -e lint
```

Run a `-k <name>` filter while iterating; run the whole file before declaring done.

## Refuse / push back if asked for

- `autouse=True` on data fixtures (banned by `testing.md`)
- Test classes — use functions
- `if` / `for` / `while` in test bodies — use `pytest.mark.parametrize` for variations
- Mocking code under test — only mock external deps (network, S3, Celery, ES)
- `transaction=True` / `transactional_db` — use the `db` fixture
- Superuser for permission tests — start from a no-permission user and grant via `create_user_role_with_permissions`
- `loaddata` or any global test data setup — use factories in fixtures
- Aggressive DRY in test bodies — redundancy that improves readability is fine
- Non-deterministic data without a seeded generator
