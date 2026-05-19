# write-uts: HOPE unit test context

HOPE-specific knowledge for writing pytest unit tests under `tests/unit/`. Project-wide test rules live in `docs/guide-dev/testing.md` — read both before writing.

## Layout

`tests/unit/` mirrors the Django source tree:

```
tests/unit/
├── conftest.py          # autouse: UNICEF partner, role w/ all perms, cache clear, activity-log silencer
├── apps/<app>/          # mirrors src/hope/apps/<app>/
├── api/                 # cross-cutting API tests (auth, throttling, helpers)
├── api_contract/        # drf-api-checker snapshot tests (its own conftest + helpers)
├── models/              # cross-app model tests
├── admin/               # Django admin tests
├── contrib/             # 3rd-party integration tests (e.g. Vision)
└── middlewares/
```

Put a new test next to the code it exercises (`tests/unit/apps/<app>/test_<feature>.py`). One scenario per `test_*` function.

## Factories

Importable from `extras.test_utils.factories` (factory-boy).

```python
from extras.test_utils.factories import BusinessAreaFactory, UserFactory, ProgramFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
```

Run `ls tests/extras/test_utils/factories/` and grep `__init__.py` for the full export list. **Do not create new factories inside test files** — extend `tests/extras/test_utils/factories/` if something is missing.

Factories belong in fixtures, not in test bodies (rule from `testing.md`).

## Shared fixtures

Defined in `tests/extras/test_utils/fixtures/` and auto-imported via `tests/unit/conftest.py`. The ones you'll reach for most often:

| Fixture | What it does |
| --- | --- |
| `api_client` | Callable: `api_client(user) -> ReauthenticateAPIClient`. Use it for any API endpoint test. Re-authenticates on every request so permission changes mid-test take effect. |
| `create_user_role_with_permissions` | Callable: `(user, [Permissions.X, ...], business_area, program=None, areas=None, whole_business_area_access=False)`. Grants perms by creating a `Role` + `RoleAssignment`. |
| `create_partner_role_with_permissions` | Same, but for `Partner` instead of `User`. |
| `set_admin_area_limits_in_program` | Limits a partner's admin-area access inside a program. |
| `afghanistan` | Pre-built Afghanistan `BusinessArea` (slug `afghanistan`). |
| `partner_unicef`, `partner_unicef_hq` | UNICEF partner objects. |
| `currency_pln`, `currency_usd`, `currency_usdc`, `all_currencies` | Defined in `tests/unit/conftest.py`. |
| `mock_elasticsearch` | Mocks ES utility functions and per-program index management. Use whenever the code under test touches ES but you're not verifying search results. |
| `django_elasticsearch_setup` | Sets up real ES connection (requires running ES). Pair with `create_program_es_index` for per-program indexes. |
| `create_program_es_index` | Callable: `_create(program)`. Creates and tears down per-program ES indexes for one test. |
| `django_assert_num_queries` | pytest-django built-in. Use to pin query counts and catch N+1 regressions. |
| `mocker` | pytest-mock. Use `mocker.patch(...)` for external deps only. |
| `monkeypatch` | pytest built-in. Use for env vars, attribute swaps, etc. |
| `db` | pytest-django built-in. Already activated by `pytestmark = pytest.mark.django_db`; request it explicitly when a fixture needs DB access but the test function doesn't. |

Local fixtures (used in one file) go at the top of that file, not in `conftest.py`. The rule from `testing.md`: "We have global conftests defined for both `e2e`/`ut` but try to place dedicated fixtures in test files."

## Module-level marks

```python
pytestmark = pytest.mark.django_db                              # most tests
pytestmark = [pytest.mark.django_db, pytest.mark.enable_activity_log]   # opt back into activity logging
pytestmark = [pytest.mark.usefixtures("mock_elasticsearch"), pytest.mark.django_db]   # all tests in file need ES mocked
```

Activity logging is silenced by default (`disable_activity_log` autouse in `tests/unit/conftest.py`); opt in with `pytest.mark.enable_activity_log` on the test, class, or module.

ES auto-sync is off (`ELASTICSEARCH_DSL_AUTOSYNC = False`). If code under test calls ES utilities, either mock them with `mock_elasticsearch` or stand up a real index with `django_elasticsearch_setup` + `create_program_es_index`.

## Test shapes

### API endpoint

```python
from django.urls import reverse
from rest_framework import status

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory, UserFactory
from hope.apps.account.permissions import Permissions

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(): return BusinessAreaFactory(slug="afghanistan")

@pytest.fixture
def user(): return UserFactory()

@pytest.fixture
def authenticated_client(api_client, user): return api_client(user)

@pytest.fixture
def list_url(business_area):
    return reverse("api:grievance-tickets:grievance-tickets-global-list",
                   kwargs={"business_area_slug": business_area.slug})


def test_create_returns_403_without_permission(authenticated_client, list_url):
    response = authenticated_client.post(list_url, {...}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_returns_201_with_permission(
    authenticated_client, create_user_role_with_permissions, user, business_area, list_url,
    django_assert_num_queries,
):
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area)

    with django_assert_num_queries(100):  # placeholder — replace with actual count after first run
        response = authenticated_client.post(list_url, {...}, format="json")

    assert response.status_code == status.HTTP_201_CREATED
```

Always test both the no-permission path and the with-permission path. Never authenticate as a superuser. Happy-path tests wrap the Act call in `django_assert_num_queries` (see *Query-count guard* below).

### Model / domain logic

```python
from django.db import transaction
from django.db.utils import IntegrityError

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("desc", "active", "is_unique", "should_raise"),
    [
        ("inactive is allowed", False, True, False),
        ("duplicate is rejected", True, True, True),
    ],
)
def test_unique_active_wallet_constraint(individual, desc, active, is_unique, should_raise):
    AccountFactory(individual=individual, unique_key="wallet-1", active=True, is_unique=True)
    kwargs = {"individual": individual, "unique_key": "wallet-1", "active": active, "is_unique": is_unique}
    if should_raise:
        with transaction.atomic(), pytest.raises(IntegrityError):
            AccountFactory(**kwargs)
    else:
        AccountFactory(**kwargs)
```

`IntegrityError` must be raised inside `transaction.atomic()` — otherwise the broken transaction poisons later assertions.

### Query-count guard

**Every happy-path test must wrap the Act phase in `django_assert_num_queries`.** This pins query count and catches N+1 regressions on every change.

Use `100` as the initial budget — it's a placeholder. Run the test, read the actual count from the failure message, and replace `100` with the real value. Leaving `100` in committed code is wrong; the user updates it once the real number is known.

```python
def test_list_returns_tickets(authenticated_client, list_url, django_assert_num_queries):
    # Arrange ...

    with django_assert_num_queries(100):  # placeholder — replace with actual count after first run
        response = authenticated_client.get(list_url)

    assert response.status_code == 200
    # further assertions on response.data ...
```

Only wrap the single Act call (the request / function call under test), not the Arrange fixtures. Error-path tests (403, 404, 400) don't need the guard.

### API contract (drf-api-checker)

Lives in `tests/unit/api_contract/`. Uses `frozenfixture` (auto-cached JSON) and `HopeRecorder` from `_helpers.py`. The conftest in that directory freezes time, monkeypatches the serializer, and resets factory sequences. Do **not** mix these patterns into regular unit tests — they're contract-snapshot machinery.

```python
from drf_api_checker.pytest import frozenfixture
from unit.api_contract._helpers import HopeRecorder

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem

@frozenfixture()
def grievance_ticket(request, db, business_area, program, superuser):
    return GrievanceTicketFactory(business_area=business_area, ...)

def test_list_grievance_tickets(superuser, business_area, ..., grievance_ticket):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/.../grievance-tickets/")
```

## Mocking

- `mocker.patch("hope.apps.x.y.external_call")` — third-party HTTP, S3, Celery, ES utility functions.
- `monkeypatch.setattr(Account, "update_unique_field", mock.Mock())` — swap an attribute on the class for the duration of one test.
- **Never** mock the function the test is supposed to exercise. If you find yourself mocking the code under test, the test is testing the mock.

For ES: prefer the `mock_elasticsearch` fixture (already wired up to patch the right call sites — see `tests/unit/conftest.py`) over hand-rolling `mocker.patch` calls.

## Permissions

`hope.apps.account.permissions.Permissions` is an enum of every permission key. Pick the most specific one for the action under test (`GRIEVANCES_CREATE`, `PROGRAMME_FINISH`, `GRIEVANCES_VIEW_LIST_SENSITIVE`, etc.). One test asserts the unauthenticated/unauthorized path (403); another grants the perm and asserts the success path.

```python
create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)
```

Pass `program=None, whole_business_area_access=True` for business-area-wide roles.

## Determinism

- `freezegun.freeze_time` for time-sensitive assertions. (`api_contract/conftest.py` auto-freezes time at `2025-01-01T00:00:00Z` for contract tests.)
- Seed any `random` / `uuid` calls inside fixtures so re-runs and parallel workers (`-n auto`) produce stable output.

## Running

```bash
# whole file (Makefile target — starts compose services if needed)
make uts ARGS=tests/unit/apps/<app>/test_<feature>.py

# single test (raw form — matches CI)
uv run tox -e tests -- pytest tests/unit/apps/<app>/test_<feature>.py::test_<scenario>

# name filter
uv run tox -e tests -- pytest tests/unit/apps/<app> -k "create_and_not"

# 100% patch coverage gate (CI enforces this on every PR)
uv run tox -e patch-coverage

# style + types
uv run tox -e lint
```
