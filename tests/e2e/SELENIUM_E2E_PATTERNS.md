# Selenium E2E Test Patterns — HOPE Project

This document is a reference guide for creating new SeleniumBase E2E tests in the HOPE project. It describes the Aurora-style setup pattern, the `HopeTestBrowser` wrapper, available selectors, and a step-by-step template for writing new tests.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Aurora Pattern (Reference)](#aurora-pattern-reference)
- [HopeTestBrowser](#hopetestbrowser)
- [Fixture Setup (browser_sb)](#fixture-setup-browser_sb)
- [Login Fixture](#login-fixture)
- [Database Fixtures (Reused from conftest.py)](#database-fixtures-reused-from-conftestpy)
- [SeleniumBase Key API Methods](#seleniumbase-key-api-methods)
- [Programme Wizard Selectors](#programme-wizard-selectors)
- [Programme Details Selectors](#programme-details-selectors)
- [Navigation Selectors](#navigation-selectors)
- [Writing a New Test — Step by Step](#writing-a-new-test--step-by-step)
- [Running Tests](#running-tests)
- [Existing Raw Selenium Tests](#existing-raw-selenium-tests)

---

## Architecture Overview

```
seleniumbase.BaseCase
    └── HopeTestBrowser          (tests/e2e/helpers/selenium_base.py)
            └── browser_sb fixture   (per-test file or local conftest)
                    └── login_sb fixture
                            └── Test methods using sb.type(), sb.click(), sb.assert_text()
```

New SeleniumBase tests use `HopeTestBrowser` (extends `BaseCase`) with selectors referenced directly via `data-cy` attributes — no page object layer. This follows the Aurora pattern where SeleniumBase's concise API makes a page object layer unnecessary.

Existing raw Selenium tests continue to use the `Common → BaseComponents → PageObject` hierarchy and are not affected by the SeleniumBase setup.

---

## Aurora Pattern (Reference)

Source: [hope-aurora/tests/extras/testutils/selenium.py](https://github.com/unicef/hope-aurora/blob/develop/tests/extras/testutils/selenium.py)

```python
from seleniumbase import BaseCase

class AuroraSeleniumTC(BaseCase):
    live_server_url: str = ""

    def setUp(self, masterqa_mode=False):
        super().setUp()
        from testutils.factories import SuperUserFactory
        super().setUpClass()
        self.admin_user = SuperUserFactory()
        self.admin_user._password = "password"

    def tearDown(self):
        self.save_teardown_screenshot()
        super().tearDown()
        self.admin_user.delete()

    def base_method(self):
        pass

    def open(self, url: str):
        self.maximize_window()
        return super().open(f"{self.live_server_url}{url}")

    def login(self, url=None):
        self.open("/admin/")
        if self.get_current_url() == f"{self.live_server_url}/admin/login/?next=/admin/":
            self.type("input[name=username]", f"{self.admin_user.username}")
            self.type("input[name=password]", f"{self.admin_user._password}")
            self.submit('input[value="Log in"]')
            self.wait_for_ready_state_complete()

    def select2_select(self, element_id: str, value: str):
        self.slow_click(f"span[aria-labelledby=select2-{element_id}-container]")
        self.wait_for_element_visible("input.select2-search__field")
        self.click(f"li.select2-results__option:contains('{value}')")
        self.wait_for_element_absent("input.select2-search__field")

AuroraTestBrowser = AuroraSeleniumTC
```

Aurora's `conftest.py` wiring:

```python
from seleniumbase import config as sb_config
from seleniumbase.core import session_helper

@pytest.fixture
def browser(live_server, request):
    sb = AuroraSeleniumTC("base_method")
    sb.live_server_url = str(live_server)
    sb.setUp()
    sb._needs_tearDown = True
    sb._using_sb_fixture = True
    sb._using_sb_fixture_no_class = True
    sb_config._sb_node[request.node.nodeid] = sb
    yield sb
    if sb._needs_tearDown:
        sb.tearDown()
        sb._needs_tearDown = False
```

Aurora test usage:

```python
def test_register(mock_state, browser: AuroraTestBrowser, registration):
    url = registration.get_absolute_url()
    browser.open(url)
    browser.type("input[name=first_name]", "first_name")
    browser.type("input[name=last_name]", "last_name")
    browser.click("input[name=_save_form]")
    assert Record.objects.filter(id=browser.get_text("#registration-id").split("/")[1])
```

---

## HopeTestBrowser

Location: `tests/e2e/helpers/selenium_base.py`

```python
from seleniumbase import BaseCase

class HopeTestBrowser(BaseCase):
    live_server_url: str = ""

    def setUp(self, masterqa_mode=False):
        super().setUp()

    def tearDown(self):
        self.save_teardown_screenshot()
        super().tearDown()

    def base_method(self):
        pass

    def open(self, url: str):
        self.maximize_window()
        return super().open(f"{self.live_server_url}{url}")

    def login(self, username="superuser", password="testtest2"):
        self.open("/api/unicorn/")
        self.execute_script("""
            window.indexedDB.databases().then(dbs => dbs.forEach(db => {
                indexedDB.deleteDatabase(db.name);
            }));
            window.localStorage.clear();
            window.sessionStorage.clear();
        """)
        self.wait_for_element_visible("#id_username")
        self.type("#id_username", username)
        self.type("#id_password", password)
        self.click('//*[@id="login-form"]/div[3]/input', by="xpath")
        self.sleep(0.3)
        self.open("/")
        self.wait_for_ready_state_complete()

    def select_listbox_element(self, name, timeout=10):
        self.wait_for_element_visible('ul[role="listbox"]', timeout=timeout)
        self.sleep(1)
        self.click(f'ul[role="listbox"] li:contains("{name}")')
        self.wait_for_element_absent('ul[role="listbox"]')

    def select_option_by_name(self, option_name):
        selector = f'li[data-cy="select-option-{option_name}"]'
        self.wait_for_element_visible(selector)
        self.click(selector)
        self.wait_for_element_absent(selector)

    def scroll_main_content(self, scroll_by=600):
        self.execute_script(f"""
            var c = document.querySelector("div[data-cy='main-content']");
            if (c) c.scrollBy(0, {scroll_by});
        """)
        self.sleep(1)
```

### Key differences from Aurora's `AuroraSeleniumTC`

| Aspect           | Aurora                          | HOPE                                                           |
| ---------------- | ------------------------------- | -------------------------------------------------------------- |
| Login flow       | Django admin (`/admin/`)        | HOPE API (`/api/unicorn/`)                                     |
| User creation    | `SuperUserFactory()` in setUp() | Reuses `create_super_user` fixture from conftest.py            |
| Dropdown helpers | `select2_select()` for Select2  | `select_listbox_element()` + `select_option_by_name()` for MUI |
| Scroll           | Not needed                      | `scroll_main_content()` for MUI layout                         |

---

## Fixture Setup (browser_sb)

The `browser_sb` fixture follows the **exact Aurora conftest.py wiring** pattern. It must be defined in each test file or a local conftest:

```python
from typing import Generator
import pytest
from seleniumbase import config as sb_config
from seleniumbase.core import session_helper
from e2e.helpers.selenium_base import HopeTestBrowser

@pytest.fixture
def browser_sb(live_server_with_static, request) -> Generator[HopeTestBrowser, None, None]:
    if request.cls:
        if sb_config.reuse_class_session:
            the_class = str(request.cls).split(".")[-1].split("'")[0]
            if the_class != sb_config._sb_class:
                session_helper.end_reused_class_session_as_needed()
                sb_config._sb_class = the_class
        request.cls.sb = HopeTestBrowser("base_method")
        request.cls.sb.live_server_url = str(live_server_with_static)
        request.cls.sb.setUp()
        request.cls.sb._needs_tearDown = True
        request.cls.sb._using_sb_fixture = True
        request.cls.sb._using_sb_fixture_class = True
        sb_config._sb_node[request.node.nodeid] = request.cls.sb
        yield request.cls.sb
        if request.cls.sb._needs_tearDown:
            request.cls.sb.tearDown()
            request.cls.sb._needs_tearDown = False
    else:
        sb = HopeTestBrowser("base_method")
        sb.live_server_url = str(live_server_with_static)
        sb.setUp()
        sb._needs_tearDown = True
        sb._using_sb_fixture = True
        sb._using_sb_fixture_no_class = True
        sb_config._sb_node[request.node.nodeid] = sb
        yield sb
        if sb._needs_tearDown:
            sb.tearDown()
            sb._needs_tearDown = False
```

### Why a separate fixture?

SeleniumBase's `BaseCase` manages its own browser lifecycle internally. It can't accept an externally-created `Chrome` driver. The existing `browser` fixture returns a raw `selenium.webdriver.Chrome` instance — fundamentally incompatible.

**Shared fixtures** (DB/server level — work with both):

- `create_super_user` (autouse) — creates users, roles, DCTs, document types
- `create_unicef_partner` (autouse) — creates UNICEF partner
- `create_role_with_all_permissions` (autouse) — creates role
- `clear_default_cache` (autouse) — clears Django cache
- `live_server_with_static` — Django live server with static files
- `business_area` — Afghanistan setup

**Incompatible fixtures** (raw Selenium only):

- `driver` — raw `Chrome` instance
- `browser` — wraps `driver` (autouse in conftest.py)
- `login` — uses raw Selenium API
- All `page_*` fixtures — require raw `Chrome` instance

---

## Login Fixture

```python
@pytest.fixture
def login_sb(browser_sb: HopeTestBrowser) -> HopeTestBrowser:
    browser_sb.login()
    return browser_sb
```

Credentials: `superuser` / `testtest2` (created by the autouse `create_super_user` fixture).

---

## Database Fixtures (Reused from conftest.py)

All these are set up automatically (autouse) or via dependency chain:

| Fixture                            | What it creates                                                                                                                                                                                          |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `business_area`                    | Afghanistan BA with flags, settings                                                                                                                                                                      |
| `create_super_user`                | BeneficiaryGroups ("Main Menu", "People"), Partners (TEST, UNICEF, UNHCR), Roles, User (`superuser`/`testtest2`), 5 DataCollectingTypes (Full, Size only, WASH, Partial, size/age/gender), DocumentTypes |
| `create_unicef_partner`            | UNICEF + UNICEF HQ partners                                                                                                                                                                              |
| `create_role_with_all_permissions` | Role with all permissions                                                                                                                                                                                |
| `clear_default_cache`              | Clears Django cache                                                                                                                                                                                      |
| `live_server_with_static`          | Django live server with static files handling                                                                                                                                                            |

### Partner fixture for programme creation

Programme creation requires UNHCR partner to have a role in the business area. Add this as autouse in your test file:

```python
@pytest.fixture(autouse=True)
def create_unhcr_partner() -> None:
    partner_unhcr = PartnerFactory(name="UNHCR")
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    partner_unhcr.role_assignments.all().delete()
    partner_unhcr.allowed_business_areas.add(afghanistan)
    RoleAssignmentFactory(
        partner=partner_unhcr,
        business_area=afghanistan,
        role=RoleFactory(name="Role for UNHCR"),
        program=None,
    )
```

---

## SeleniumBase Key API Methods

Full reference: [seleniumbase.io method summary](https://seleniumbase.io/help_docs/method_summary/)

### Navigation

```python
sb.open(url)                    # Navigate to URL (HopeTestBrowser prepends live_server_url)
sb.go_back()                    # Browser back
sb.go_forward()                 # Browser forward
sb.refresh()                    # Reload page
sb.get_current_url()            # Current URL
```

### Interaction

```python
sb.click(selector)              # Click element
sb.slow_click(selector)         # Click with built-in wait
sb.type(selector, text)         # Clear + type text (replaces existing)
sb.send_keys(selector, text)    # Append text (doesn't clear)
sb.clear(selector)              # Clear input field
sb.submit(selector)             # Submit form
sb.click_if_visible(selector)   # Click only if visible (no error if absent)
sb.check_if_unchecked(selector) # Check a checkbox if unchecked
sb.hover(selector)              # Hover over element
sb.js_click(selector)           # Click via JavaScript
sb.scroll_to(selector)          # Scroll element into view
```

### Waiting

```python
sb.wait_for_element_visible(selector, timeout=None)  # Wait until visible
sb.wait_for_element_absent(selector, timeout=None)    # Wait until gone
sb.wait_for_element_clickable(selector, timeout=None) # Wait until clickable
sb.wait_for_text(text, selector="html", timeout=None) # Wait for text in element
sb.wait_for_exact_text(text, selector, timeout=None)  # Wait for exact text
sb.wait_for_ready_state_complete()                     # Wait for page load
sb.sleep(seconds)                                      # Explicit sleep (AVOID — see rule below)
```

> **Rule: prefer `wait_for_element_*` over `sb.sleep()`.**
> Instead of hardcoding `sb.sleep(0.3)` (or any duration) to wait for an
> overlay/picker to disappear, use an explicit wait on the **next element you
> intend to interact with**:
>
> ```python
> # BAD — fixed delay, slow on fast machines, flaky on slow ones
> sb.click(INPUT_START_DATE)
> sb.send_keys(INPUT_START_DATE, start_date)
> sb.click(INPUT_NAME)          # dismiss picker
> sb.sleep(0.3)                 # ← don't do this
> sb.click(INPUT_END_DATE)
>
> # GOOD — proceeds as soon as the element is ready
> sb.click(INPUT_START_DATE)
> sb.send_keys(INPUT_START_DATE, start_date)
> sb.click(INPUT_NAME)          # dismiss picker
> sb.wait_for_element_clickable(INPUT_END_DATE)  # ← do this
> sb.click(INPUT_END_DATE)
> ```
>
> Use `sb.sleep()` only as a **last resort** when no DOM condition can be
> waited on (e.g. CSS animations with no attribute change).

### Assertions

```python
sb.assert_element(selector)                    # Assert element exists and visible
sb.assert_element_present(selector)            # Assert element in DOM (may be hidden)
sb.assert_element_absent(selector)             # Assert element not in DOM
sb.assert_element_not_visible(selector)        # Assert element hidden
sb.assert_text(text, selector="html")          # Assert text is present in element
sb.assert_exact_text(text, selector="html")    # Assert exact text match
sb.assert_text_not_visible(text, selector)     # Assert text NOT in element
sb.assert_title(title)                         # Assert page title
sb.assert_url_contains(substring)              # Assert URL contains string
sb.assert_true(expr)                           # Assert expression is true
sb.assert_equal(first, second)                 # Assert equality
```

### Reading

```python
sb.get_text(selector)            # Get element text
sb.get_attribute(selector, attr) # Get attribute value
sb.is_element_visible(selector)  # Check visibility (boolean)
sb.is_text_visible(text, sel)    # Check text presence (boolean)
sb.find_element(selector)        # Get WebElement
sb.find_elements(selector)       # Get list of WebElements
```

### Utility

```python
sb.execute_script(script)                # Execute JavaScript
sb.save_screenshot(name)                 # Save screenshot
sb.save_teardown_screenshot()            # Screenshot on teardown
sb.maximize_window()                     # Maximize browser window
sb.highlight(selector)                   # Highlight element (debugging)
sb.highlight_click(selector)             # Highlight + click
```

---

## Programme Wizard Selectors

### Step 1 — Details (data-cy attributes)

| Selector                                                     | Description                     |
| ------------------------------------------------------------ | ------------------------------- |
| `a[data-cy="button-new-program"]`                            | "NEW PROGRAMME" button          |
| `input[data-cy="input-name"]`                                | Programme name input            |
| `input[name="startDate"]`                                    | Start date input (YYYY-MM-DD)   |
| `input[name="endDate"]`                                      | End date input (YYYY-MM-DD)     |
| `div[data-cy="select-sector"]`                               | Sector dropdown (click to open) |
| `div[data-cy="input-data-collecting-type"]`                  | DCT dropdown (click to open)    |
| `div[data-cy="input-beneficiary-group"]`                     | Beneficiary group dropdown      |
| `span[data-cy="input-cashPlus"]`                             | CASH+ checkbox                  |
| `textarea[data-cy="input-description"]`                      | Description textarea            |
| `input[data-cy="input-budget"]`                              | Budget input                    |
| `input[data-cy="input-administrativeAreasOfImplementation"]` | Admin areas input               |
| `input[data-cy="input-populationGoal"]`                      | Population goal input           |
| `input[data-cy="input-programme-code"]`                      | Programme code input            |
| `//*[@data-cy="input-frequency-of-payment"]/div[1]/div/span` | One-off frequency radio (XPath) |
| `//*[@data-cy="input-frequency-of-payment"]/div[2]/div/span` | Regular frequency radio (XPath) |

### Dropdown option selection

After clicking a dropdown, use one of:

- `sb.select_option_by_name("Child Protection")` — for `data-cy="select-option-*"` dropdowns
- `sb.select_listbox_element("Main Menu")` — for `ul[role="listbox"]` MUI dropdowns

### Step 2 — Time Series Fields

| Selector                                                                 | Description                   |
| ------------------------------------------------------------------------ | ----------------------------- |
| `button[data-cy="button-add-time-series-field"]`                         | Add TSF button                |
| `input[data-cy="input-pduFields.{idx}.label"]`                           | TSF label input               |
| `div[data-cy="select-pduFields.{idx}.pduData.subtype"]`                  | TSF subtype dropdown          |
| `div[data-cy="select-pduFields.{idx}.pduData.numberOfRounds"]`           | TSF number of rounds dropdown |
| `input[data-cy="input-pduFields.{idx}.pduData.roundsNames.{round_idx}"]` | Round name input              |

Available subtypes: `Text`, `Number`, `Date`, `Boolean`

### Step 3 — Partners

| Selector                               | Description                |
| -------------------------------------- | -------------------------- |
| `div[data-cy="select-partnerAccess"]`  | Partner access dropdown    |
| `button[data-cy="button-add-partner"]` | Add partner button         |
| `div[data-cy="select-partners[0].id"]` | Partner selection dropdown |

### Wizard navigation

| Selector                        | Description                           |
| ------------------------------- | ------------------------------------- |
| `button[data-cy="button-next"]` | Next step button                      |
| `button[data-cy="button-back"]` | Previous step button                  |
| `a[data-cy="button-cancel"]`    | Cancel button (returns to management) |
| `button[data-cy="button-save"]` | Save programme button                 |

---

## Programme Details Selectors

| Selector                                                      | Description                                  |
| ------------------------------------------------------------- | -------------------------------------------- |
| `h5[data-cy="page-header-title"]`                             | Programme name header                        |
| `div[data-cy="status-container"]`                             | Programme status (DRAFT / ACTIVE / FINISHED) |
| `div[data-cy="label-START DATE"]`                             | Start date display                           |
| `div[data-cy="label-END DATE"]`                               | End date display                             |
| `div[data-cy="label-Sector"]`                                 | Sector display                               |
| `div[data-cy="label-Data Collecting Type"]`                   | DCT display                                  |
| `div[data-cy="label-Frequency of Payment"]`                   | Frequency display                            |
| `div[data-cy="label-Administrative Areas of implementation"]` | Admin areas display                          |
| `div[data-cy="label-CASH+"]`                                  | CASH+ display (Yes/No)                       |
| `div[data-cy="label-Programme size"]`                         | Programme size display                       |
| `div[data-cy="label-Description"]`                            | Description display                          |
| `div[data-cy="label-Programme Code"]`                         | Programme code display                       |
| `div[data-cy="label-Partner Access"]`                         | Partner access display                       |
| `h6[data-cy="label-partner-name"]`                            | Partner name display                         |

---

## Navigation Selectors

| Selector                                    | Target page          |
| ------------------------------------------- | -------------------- |
| `a[data-cy="nav-Programmes"]`               | Programme Management |
| `a[data-cy="nav-Programme Details"]`        | Programme Details    |
| `a[data-cy="nav-Country Dashboard"]`        | Country Dashboard    |
| `a[data-cy="nav-Registration Data Import"]` | RDI                  |
| `a[data-cy="nav-Targeting"]`                | Targeting            |
| `a[data-cy="nav-Payment Module"]`           | Payment Module       |
| `a[data-cy="nav-Programme Cycles"]`         | Programme Cycles     |
| `a[data-cy="nav-Grievance Tickets"]`        | Grievance Tickets    |
| `a[data-cy="nav-Feedback"]`                 | Feedback             |
| `a[data-cy="nav-Programme Users"]`          | Programme Users      |
| `a[data-cy="nav-Programme Log"]`            | Programme Log        |

---

## Writing a New Test — Step by Step

### 1. Create the file

```
tests/e2e/<module>/test_<feature>.py
```

### 2. Add imports and markers

```python
from typing import Generator
import pytest
from seleniumbase import config as sb_config
from seleniumbase.core import session_helper
from e2e.helpers.selenium_base import HopeTestBrowser

pytestmark = pytest.mark.django_db()
```

### 3. Define selectors as module-level constants

```python
NAV_TARGET = 'a[data-cy="nav-Target Page"]'
HEADER = 'h5[data-cy="page-header-title"]'
BTN_ACTION = 'button[data-cy="button-action"]'
```

### 4. Add the browser_sb and login_sb fixtures

Copy the `browser_sb` and `login_sb` fixtures from the pattern above. Add any autouse fixtures needed for test data.

### 5. Write test methods

```python
class TestMyFeature:
    def test_something(self, login_sb: HopeTestBrowser) -> None:
        sb = login_sb

        # Navigate
        sb.click(NAV_TARGET)
        sb.wait_for_text("Expected Title", HEADER)

        # Interact
        sb.click(BTN_ACTION)
        sb.type('input[data-cy="input-field"]', "value")

        # Assert
        sb.assert_text("Expected Text", 'div[data-cy="label-Field"]')
        sb.assert_element('div[data-cy="status-container"]')
```

### 6. Use helper functions for repeated flows

```python
def _fill_form(sb: HopeTestBrowser, **fields) -> None:
    for selector, value in fields.items():
        sb.type(selector, value)
```

---

## Running Tests

All E2E tests (both raw Selenium and SeleniumBase) are run via `tox`:

```bash
# Run ALL e2e tests with 3 parallel workers (standard CI command)
tox -e selenium -- tests/e2e -n 3

# Run only the SeleniumBase create-program tests
tox -e selenium -- tests/e2e/program_details/test_create_program.py

# Run a single test
tox -e selenium -- tests/e2e/program_details/test_create_program.py::TestCreateProgram::test_create_programme_mandatory_fields_only

# Run with visible browser for debugging (override --headless from tox.ini)
tox -e selenium -- tests/e2e/program_details/test_create_program.py --headed

# Run with slow mode for debugging (SeleniumBase demo mode)
tox -e selenium -- tests/e2e/program_details/test_create_program.py --headed --demo

# Collect tests without running (verify discovery)
tox -e selenium -- tests/e2e --collect-only

# Run existing raw Selenium tests only
tox -e selenium -- tests/e2e/programme_management/test_programme_management.py -n 3
```

### How tox runs tests

The `tox -e selenium` environment ([tox.ini](../../tox.ini)) runs:

```
pytest -q -rfE --no-header --tb=short --randomly-seed=42 \
  --create-db --reruns-delay 1 --no-migrations \
  --headless {posargs:./tests/e2e}
```

Key flags:

- `--headless` — runs browsers without a visible window (required for CI; SeleniumBase respects this flag, raw Selenium tests hardcode headless in the `driver` fixture)
- `-n N` — number of parallel workers (passed via `{posargs}`, e.g. `tox -e selenium -- tests/e2e -n 3`)
- `--create-db` — creates a fresh test database
- `--no-migrations` — skips migrations for speed
- `--headed` — override to show the browser (useful for local debugging, passed via `{posargs}`)

---

## Existing Raw Selenium Tests

The existing tests use a 3-layer Page Object Model:

```
Common (helpers/helper.py)           — WebDriver wait utilities, scroll, screenshots
    └── BaseComponents (base_components.py) — Navigation, global filter, MUI helpers
            └── ProgrammeManagement    — Wizard selectors and actions
            └── ProgrammeDetails       — Details page selectors
            └── (40+ other page objects)
```

These tests use a raw `Chrome` driver and are managed by the `browser` fixture in `conftest.py`. They will continue to work unchanged. Migration to SeleniumBase is optional and can be done incrementally.

### Key raw Selenium patterns (for reference)

```python
# Wait for element
element = self.wait_for('div[data-cy="status-container"]')

# Wait for text in element
self.wait_for_text("DRAFT", 'div[data-cy="status-container"]')

# Select from MUI listbox
self.select_listbox_element("Main Menu")

# Select from data-cy dropdown
self.select_option_by_name("Child Protection")

# Scroll main content
self.scroll(scroll_by=600)

# Assert
assert "DRAFT" in element.text
```

### SeleniumBase equivalents

```python
# Wait for element
sb.wait_for_element_visible('div[data-cy="status-container"]')

# Wait for text in element
sb.wait_for_text("DRAFT", 'div[data-cy="status-container"]')

# MUI listbox (via HopeTestBrowser helper)
sb.select_listbox_element("Main Menu")

# data-cy dropdown (via HopeTestBrowser helper)
sb.select_option_by_name("Child Protection")

# Scroll
sb.scroll_main_content(600)

# Assert
sb.assert_text("DRAFT", 'div[data-cy="status-container"]')
```
