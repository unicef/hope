# write-e2e: HOPE E2E context

HOPE-specific knowledge for writing SeleniumBase E2E tests under `tests/e2e/new_selenium/`. Generic test rules (AAA, no `autouse`, no `sleep`, factory-only data, etc.) and run commands live in `docs/guide-dev/testing.md` — read both before writing.

## Key files

- `tests/e2e/helpers/selenium_base.py` — `HopeTestBrowser` (extends `seleniumbase.BaseCase`)
- `tests/e2e/new_selenium/conftest.py` — shared `browser` and `login` fixtures
- `tests/e2e/conftest.py` — autouse DB fixtures (see table below)

## HopeTestBrowser API

```
HopeTestBrowser (extends seleniumbase.BaseCase)
    └── browser fixture  (tests/e2e/new_selenium/conftest.py)
        └── login fixture
            └── test functions: login.click(), login.type(), login.assert_text(), ...
```

`HopeTestBrowser` adds HOPE-specific helpers on top of SeleniumBase:

- `login(username, password)` — logs in via Django admin, clears browser storage
- `select_listbox_element(name)` — selects from MUI `ul[role="listbox"]` dropdowns
- `select_option_by_name(name)` — selects from `data-cy="select-option-*"` dropdowns
- `scroll_main_content(scroll_by)` — scrolls the MUI main-content area

Use the `login` fixture directly — do not alias (`browser = login` is rejected by style).

The older raw-Selenium suite (`Common → BaseComponents → PageObject`) lives elsewhere; this skill targets only the new SeleniumBase style.

## Fixtures

Before adding a new fixture, grep the existing conftests:

```bash
grep -rn "@pytest.fixture" tests/e2e/new_selenium/
```

If a suitable fixture exists, request it explicitly in the test signature. If not, add a new one in the test file you're creating — must use a factory from `extras.test_utils.factories`, and must NOT use `autouse=True` (banned for data fixtures by `testing.md`).

Some autouse fixtures already run for every e2e test (UNICEF partner, role with all permissions, cache clear). You do not need to request these — they're set up at the conftest level.

## Selectors

Preference order is set in `docs/guide-dev/testing.md` (E2E selectors):
`name` > `data-cy` > `id` > CSS class > xpath (never).

The HOPE frontend tags most interactive elements with `data-cy`, so the practical fallback is almost always `data-cy`. Use `name` whenever the element actually has a `name` attribute — most commonly on form/date inputs.

### Selector shapes

```python
'input[name="startDate"]'                 # has name attr — prefer this
'input[data-cy="input-name"]'             # no name attr — fall back to data-cy
'button[data-cy="button-save"]'           # buttons
'div[data-cy="select-sector"]'            # MUI dropdown → login.select_option_by_name(...)
```

Discover selectors via the frontend source or browser DevTools — grep for `data-cy`.

## SeleniumBase patterns

### Fetch element once

```python
# BAD — two DOM lookups
browser.click(INPUT_START_DATE)
browser.send_keys(INPUT_START_DATE, "2024-01-01")

# GOOD — one lookup
el = browser.find_element(INPUT_START_DATE)
el.click()
el.send_keys("2024-01-01")
```

### Chain click onto wait

`wait_for_element_visible` returns the `WebElement`. Chain `.click()` instead of re-looking up:

```python
# BAD — wait finds it, then click finds it again
browser.wait_for_element_visible('button[data-cy="button-save"]')
browser.click('button[data-cy="button-save"]')

# GOOD — one lookup
browser.wait_for_element_visible('button[data-cy="button-save"]').click()
```

### Waits, not sleep

Use `wait_for_element_clickable`, `wait_for_element_visible`, `wait_for_element_absent`. `sleep` is banned by `testing.md`; only acceptable for genuine CSS-animation timing as a last resort — and even then prefer a conditional wait.

## Debugging

```bash
# Single e2e file with visible browser
tox -e tests -- tests/e2e/new_selenium/<area>/test_<feature>.py --headed
```
