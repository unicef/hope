---
name: write-e2e
description: Generate a new SeleniumBase E2E test for HOPE that follows project rules and uses the HopeTestBrowser fixture API. USE WHEN user asks to write, scaffold, add, or create a new E2E test under tests/e2e/new_selenium/.
---

# write-e2e

Generate a new HOPE E2E test under `tests/e2e/new_selenium/` that follows project rules and uses the `HopeTestBrowser` API.

## Inputs from user

- **Feature / page under test** — which UI area is exercised
- **Scenario** — one user path through the UI (not a matrix)
- **Expected assertions** — what must be true at the end

If any of these is missing, ask for them before doing anything else.

## MANDATORY: read these before writing anything

1. `docs/guide-dev/testing.md` — project-wide test rules (especially **Conventions** and **E2E selectors**)
2. `.agents/write-e2e/context.md` — HopeTestBrowser API, fixtures, selectors, SeleniumBase patterns
3. `tests/e2e/new_selenium/grievance/test_grievance_tickets.py` — concrete example of a working new-style test

Step 3 is non-optional. Existing tests show how the rules interact in practice.

## Procedure

1. **Location.** Put the new test in `tests/e2e/new_selenium/<area>/test_<feature>.py`. `<area>` mirrors a directory under `src/hope/apps/`.

2. **Scaffold the file:**
   ```python
   import pytest
   from extras.test_utils.selenium import HopeTestBrowser

   pytestmark = pytest.mark.django_db()

   def test_<scenario>(login: HopeTestBrowser) -> None:
       # Arrange — request fixtures explicitly; build minimal data via factories
       # Act     — login.click(...), login.type(...), login.wait_for_element_visible(...).click()
       # Assert  — login.assert_text(...), login.assert_element(...)
   ```

3. **Fill in the body following `testing.md` (rules) and `context.md` (HopeTestBrowser API, fixtures, selectors, SeleniumBase patterns).** The mandatory reads above are not a suggestion.

## Verify before reporting done

```bash
tox -e tests -- tests/e2e/new_selenium/<area>/test_<feature>.py
tox -e lint
```

For a visible browser during iteration, append `--headed`.

## Refuse / push back if asked for

- `autouse=True` on data fixtures
- `browser.sleep()` for anything other than genuine CSS-animation timing
- Mocking code under test — only mock external deps (network, S3, Celery)
- `xpath` selectors
- Multiple scenarios in one test function (split, or use `parametrize`)
- `transaction=True` / `transactional_db` — use the `db` fixture
- Aliasing `browser = login` — use `login` directly
