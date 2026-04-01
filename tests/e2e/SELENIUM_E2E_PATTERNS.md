# Selenium E2E Test Patterns — HOPE Project

Reference guide for writing SeleniumBase E2E tests in the HOPE project.

**Key files:**

- `tests/e2e/helpers/selenium_base.py` — `HopeTestBrowser` (extends `seleniumbase.BaseCase`)
- `tests/e2e/new_selenium/conftest.py` — shared `browser`, `login`,
  fixtures
- `tests/e2e/conftest.py` — autouse DB fixtures (`create_super_user`, `create_unicef_partner`, etc.)

---

## Test Style Rules (MANDATORY)

**These rules are non-negotiable. Violations will cause test failures or flaky runs.**

1. **No `autouse=True`** on test data fixtures. Only infrastructure fixtures
   (e.g. `test_failed_check`, `clear_default_cache`) may be autouse.
   Test data fixtures must be explicitly requested by the test function.
2. **No `browser.sleep()`** — use `wait_for_element_clickable`, `wait_for_element_visible`,
   or `wait_for_element_absent` instead. Only as a last resort for CSS animations.
3. Tests MUST be plain functions (`def test_*()`), never classes.
4. One test = one scenario. Use `pytest.mark.parametrize` instead of loops.
5. No `if / for / while` inside test bodies or test helper functions.
   Loops in helpers are acceptable only for repetitive DOM actions (e.g. filling N round-name inputs).
6. Test data created exclusively in fixtures using factories from
   `extras.test_utils.factories` (not `old_factories`).
7. Use `db` fixture, NOT `transaction=True` / `transactional_db`.
8. Prefer CSS selectors with `data-cy` attributes over XPath.
9. Use `login` fixture directly — do not alias (`browser = login`).
10. Mock only external dependencies (network, S3, Celery). Never mock code under test.

---

## Architecture

```
HopeTestBrowser (extends seleniumbase.BaseCase)
    └── browser fixture  (tests/e2e/new_selenium/conftest.py)
        └── login fixture
            └── test functions using login.click(), login.type(), login.assert_text()
```

`HopeTestBrowser` provides HOPE-specific helpers on top of SeleniumBase:

- `login(username, password)` — logs in via Django admin, clears browser storage
- `select_listbox_element(name)` — selects from MUI `ul[role="listbox"]` dropdowns
- `select_option_by_name(name)` — selects from `data-cy="select-option-*"` dropdowns
- `scroll_main_content(scroll_by)` — scrolls the MUI main content area

Existing raw Selenium tests (`Common → BaseComponents → PageObject`) are unaffected.

---

## Fixture Setup

The `browser` and `login` fixtures are defined in `tests/e2e/new_selenium/conftest.py`.
Do NOT redefine them. Create local `conftest.py` only for domain-specific data fixtures.

### Autouse fixtures (from parent conftest.py)

| Fixture                            | Creates                                               |
| ---------------------------------- | ----------------------------------------------------- |
| `create_super_user`                | User (`superuser`/`testtest2`), partners, roles, DCTs |
| `create_unicef_partner`            | UNICEF + UNICEF HQ partners                           |
| `create_role_with_all_permissions` | Role with all permissions                             |
| `clear_default_cache`              | Clears Django cache                                   |

### On-demand fixtures

| Fixture                   | Creates                              |
| ------------------------- | ------------------------------------ |
| `business_area`           | Afghanistan BA with flags, settings  |
| `live_server_with_static` | Django live server with static files |

---

## SeleniumBase API Quick Reference

Full docs: [seleniumbase.io/help_docs/method_summary](https://seleniumbase.io/help_docs/method_summary/)

### Core methods

```python
# Navigation
browser.open(url)                        # HopeTestBrowser prepends live_server_url
browser.get_current_url()

# Interaction
browser.click(selector)
browser.type(selector, text)             # Clear + type (replaces existing)
browser.send_keys(selector, text)        # Append text (doesn't clear)
browser.js_click(selector)               # Click via JavaScript (for obscured elements)
browser.scroll_to(selector)

# Waiting (USE THESE instead of sleep)
browser.wait_for_element_visible(selector, timeout=None)
browser.wait_for_element_absent(selector, timeout=None)
browser.wait_for_element_clickable(selector, timeout=None)
browser.wait_for_text(text, selector="html", timeout=None)
browser.wait_for_ready_state_complete()

# Assertions
browser.assert_element(selector)         # Visible in viewport
browser.assert_text(text, selector)      # Text present in element
browser.assert_exact_text(text, selector)
browser.assert_element_absent(selector)
browser.assert_url_contains(substring)

# Reading
browser.get_text(selector)
browser.get_attribute(selector, attr)
browser.find_element(selector)           # Returns WebElement
browser.find_elements(selector)          # Returns list of WebElements
```

### Wait instead of sleep

```python
# BAD
browser.click(INPUT_NAME)          # dismiss picker
browser.sleep(0.3)                 # flaky
browser.click(INPUT_END_DATE)

# GOOD
browser.click(INPUT_NAME)          # dismiss picker
browser.wait_for_element_clickable(INPUT_END_DATE)
browser.click(INPUT_END_DATE)
```

### Fetch element once for click + type

```python
# BAD — two DOM lookups
browser.click(INPUT_START_DATE)
browser.send_keys(INPUT_START_DATE, "2024-01-01")

# GOOD — one lookup
el = browser.find_element(INPUT_START_DATE)
el.click()
el.send_keys("2024-01-01")
```

---

## Selector Conventions

All interactive elements use `data-cy` attributes. Common patterns:

```python
# Buttons
'a[data-cy="button-new-program"]'
'button[data-cy="button-next"]'
'button[data-cy="button-save"]'

# Inputs
'input[data-cy="input-name"]'
'textarea[data-cy="input-description"]'
'input[name="startDate"]'           # date inputs use name attr

# Dropdowns (click to open, then use helper)
'div[data-cy="select-sector"]'      # → browser.select_option_by_name("Child Protection")
'div[data-cy="input-beneficiary-group"]'  # → browser.select_listbox_element("Main Menu")

# Labels / display values
'div[data-cy="label-Sector"]'
'h5[data-cy="page-header-title"]'
'div[data-cy="status-container"]'

# Navigation
'a[data-cy="nav-Programmes"]'
'a[data-cy="nav-Programme Details"]'
```

Discover selectors in the frontend source or browser DevTools — search for `data-cy`.

---

## Writing a New Test

### 1. File structure

```
tests/e2e/new_selenium/<module>/test_<feature>.py
tests/e2e/new_selenium/<module>/conftest.py   # only if domain fixtures needed
```

### 2. Template

```python
import pytest
from extras.test_utils.selenium import HopeTestBrowser

pytestmark = pytest.mark.django_db()

# Selectors as module-level constants
HEADER = 'h5[data-cy="page-header-title"]'
BTN_ACTION = 'button[data-cy="button-action"]'


def test_feature_scenario(login: HopeTestBrowser) -> None:
    # Navigate
    login.click('a[data-cy="nav-Programmes"]')
    login.wait_for_text("Expected Title", HEADER)

    # Interact
    login.click(BTN_ACTION)
    login.type('input[data-cy="input-field"]', "value")

    # Assert
    login.assert_text("Expected Text", 'div[data-cy="label-Field"]')
```

### 3. Domain fixture example (local conftest.py)

```python
import pytest
from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.account.models import RoleAssignment

@pytest.fixture
def unhcr_partner():
    partner = PartnerFactory(name="UNHCR")
    ba = BusinessArea.objects.get(slug="afghanistan")
    partner.allowed_business_areas.add(ba)
    # ... setup as needed
    return partner
```

---

## Running Tests

```bash
# Run SeleniumBase tests
tox -e tests -- tests/e2e/new_selenium/

# Single test file
tox -e tests -- tests/e2e/new_selenium/program_details/test_create_program.py

# Single test
tox -e tests -- tests/e2e/new_selenium/program_details/test_create_program.py::test_name

# Visible browser
tox -e tests -- tests/e2e/new_selenium/ --headed

# Slow mode (demo)
tox -e tests -- tests/e2e/new_selenium/ --headed --demo

# Lint after changes
tox -e lint
```

tox runs: `pytest -q --create-db --no-migrations --dist=loadgroup {posargs:tests}`
