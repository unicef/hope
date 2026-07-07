# Selenium E2E Coverage Audit

**Date:** 2026-07-07
**Baseline:** `develop` **reconciled as if [PR #6154 "Additional e2e tests"](https://github.com/unicef/hope/pull/6154) is merged** (branch `additional-e2e-tests`).
**Scope:** Both Selenium suites — legacy `tests/e2e/` (excluding `new_selenium/`) and new `tests/e2e/new_selenium/`.

## Method

The app's user-facing feature map was derived from the frontend route definitions under
`src/frontend/src/` (pages/components/routers). That map (the "denominator") was
cross-referenced against every `def test_*` in both Selenium suites (the "numerator").
Disabled markers (`xfail`, `skip`, `night`) were enumerated with `grep` against the
**post-PR-6154 state** of each file.

> **What PR #6154 changed** (relevant to this audit): added a **Country Search** suite,
> an **access-denied** suite, and an **error-page / 404** suite; re-enabled **Managerial
> Console** (both tests un-xfailed and rewritten); removed the **Grievance Dashboard**
> xfail; and trimmed a handful of other xfails (~6 marker lines net). It did **not** touch
> `tests/pytest.ini`, the `program_details` / RDI skips, the filters "ToDo" skips, the
> deadlock-202318 xfails, or the Country Dashboard xfail. (It also adds ~160 unit tests and
> removes dead code — out of scope for this selenium audit.)

> **Caveat — "a test exists" ≠ "it protects anything."** A large share of legacy tests are
> still `xfail`/`skip` and do not fail CI when the feature breaks. Read section 3
> (effectively-uncovered) alongside section 2 (never-covered). Post-PR counts: the legacy
> suite has **~201** test functions, of which **41 are `xfail`** (down from 47) and **5
> are `skip`** (down from 11); **19 `night`-marked** tests remain under an unregistered marker.
> The new suite (`new_selenium/`) has **~43** tests, **0 disabled**.

---

## 1. Coverage summary by module

| Module | Tests? | Active | Disabled | Notes |
|---|---|---|---|---|
| Programs (create/edit/details) | ✅ | many | 5 xfail | Duplicate-program flow still untested |
| Population — Households | ✅ | 2 smoke | — | Smoke only |
| Population — Individuals | ✅ | 2 smoke | — | Smoke only; online templates untested |
| Population — People | ⚠️ | some | 1 xfail | `TestPeople` class still xfail (REST refactor); details/happy-path re-enabled by PR |
| Periodic Data (templates/upload) | ✅ | 8 | — | Offline only |
| RDI | ⚠️ | 4 | 4 skip | Core import + kobo still skipped |
| Targeting | ⚠️ | large | 12 xfail | Big block still disabled (deadlock/REST refactor) |
| Payment Module (plans/cycles/groups/top-up) | ✅ | strong (new suite) | 1 xfail | 1 legacy happy-path deadlock remains |
| Payment Verification | ✅ | 10 | 1 xfail | Only `xlsx_successful` still xfail |
| Grievance Tickets | ⚠️ | ~15 | 10 xfail | System-generated/adjudication/process still disabled |
| Feedback | ⚠️ | ~6 | 6 xfail + 1 skip | Filters class skipped; several create-flows xfail |
| Grievance Dashboard | ✅ | 2 | — | **PR re-enabled** (xfail removed) |
| Accountability — Surveys | ✅ | 2 smoke | — | Smoke only |
| Accountability — Communication | ✅ | 2 smoke | — | Create/edit interactions thin |
| Managerial Console | ✅ | 2 | — | **PR re-enabled + rewrote** (renders-all-sections + happy-path) |
| Country Dashboard | ❌ (effectively) | 0 | 1 xfail class | **Still xfail** — not addressed by PR |
| Program Log / Activity Log | ⚠️ | 2 smoke | — | No content assertions |
| Program Users | ⚠️ | 1 smoke | — | View only; no add/edit/remove |
| Login / Auth | ✅ | 7 | — | Good |
| Drawer / Navigation | ✅ | 4 | — | Good |
| Filters | ✅ | 4 | 2 xfail | 2 ToDo stubs now implemented (grievance + payment-verification list filters) |
| Generic Import | ✅ | 20 | — | Strongest legacy coverage |
| **Country Search** | ✅ | 3 | — | **NEW in PR** (`country_search/test_country_search.py`) |
| **Access Denied** | ✅ | 1 | — | **NEW in PR** (`access_denied/test_access_denied.py`) |
| **Error page / 404** | ✅ | 2 | — | **NEW in PR** (`error_page/test_error_page.py`) |

Legend: ✅ covered · ⚠️ partial/thin · ❌ not covered (or only via disabled tests).

---

## 2. Never-covered features (no test exists)

Confirmed via `grep` returning **zero** hits in either suite (post-PR).

| Feature | Route | Why it matters |
|---|---|---|
| **Duplicate Program** | `/:ba/programs/:id/duplicate/:id` | Program duplication is a distinct create path with copy semantics. (`duplicate_tp` covers Target Population, not Program.) |
| **Individual/People Online templates** | `population/individuals/new-online-template`, `.../online-templates/:id`, `.../edit-authorised-users` | Online periodic-data templates + authorized-user editing. Only the *offline* template flow is covered. |
| **Grievances by RDI** | `grievance/rdi/:id` | Context-scoped grievance list launched from an RDI. Not exercised directly. |
| **Grievances by Payment Verification context** | `grievance/payment-verification/:cashPlanId` | Context-scoped grievance list from a verification plan. Not exercised directly. |
| **Payment Details (single payment)** | `payment-module/payments/:paymentId` | Individual payment record detail view — no dedicated E2E test (PR added a *unit* ordering test only). |
| **Program Users management** | `.../users-list` | Only a smoke *view* test; add / edit / remove user flows untested. |
| **Activity Log / Program Log content** | `.../activity-log` | Smoke-only; no assertions that actions are actually logged. |
| **Maintenance page** | `/maintenance` | Untested. (PR added coverage for `404`, `access-denied`, and `error`, but not `maintenance`.) |

---

## 3. Effectively-uncovered features (only test is disabled)

Modules that *have* tests, but every meaningful test is `xfail`/`skip`, so a regression
would not fail CI (post-PR):

- **Country Dashboard** — `TestSmokeCountryDashboard` class still `xfail("UNSTABLE")`. *(Not addressed by PR.)*
- **People** — `TestPeople` class still `xfail` (REST refactor).
- **Grievance (system-generated)** — system-generated page/details, `process_tickets`, `needs_adjudication` still `xfail`.
- **Feedback** — filters class `skip`; several create-flows still `xfail` (incl. 2 deadlock-202318).
- **Targeting** — copy, edit, rebuild, program-status, PDU bool/decimal criteria, adjudication/sanction exclusion, filters still `xfail` (mostly deadlock-202318 / REST refactor).
- **Filters** — 2 module tests still `xfail` (the 2 `skip("ToDo")` stubs are now implemented).

> Resolved by PR (no longer in this list): **Managerial Console** and **Grievance Dashboard**.

---

## 4. Disabled-test inventory (post-PR)

### 4a. Skipped (5 markers)

> The 4 `program_details` date-fix skips and the 2 filters `"ToDo"` stubs were resolved
> (frontend `AddNewProgramCycle` blank-dialog bug fixed; tests un-skipped/implemented).

| File:line | Test / class | Reason |
|---|---|---|
| `registration_data_import/test_registration_data_import.py:148` | `test_smoke_registration_data_import_select_file` | "RDI import only possible through Program Population" |
| `registration_data_import/test_registration_data_import.py:215` | `test_registration_data_import_happy_path` | "RDI import only possible through Program Population" |
| `registration_data_import/test_registration_data_import.py:267` | `test_import_empty_kobo_form` | "Kobo form is not available… external service" |
| `registration_data_import/test_registration_data_import.py:298` | `test_import_kobo_form` | "Kobo form is not available… external service" |
| `grievance/feedback/test_feedback.py:221` | `TestFeedbackFilters` (class) | "ToDo: Filters" |

### 4b. xfail (41 markers) — grouped by reason

**`UNSTABLE` (24)**
- `programme_management/test_programme_management.py:528` (back scenarios), `:620` `test_create_programme_chose_dates_via_calendar`, `:713` `test_edit_programme`, `:745` `test_programme_partners`, `:856` (calendar/manual)
- `filters/test_filters.py:290` `test_filters_selected_program`, `:435` (parametrized by `module`)
- `program_details/test_program_details.py:328` `test_program_details_check_default_cycle`, `:520` `test_program_details_delete_programme_cycle`
- `targeting/test_targeting.py:608` (create targeting), `:1666` `test_targeting_info_button`
- `payment_verification/test_payment_verification.py:552` `test_payment_verification_xlsx_successful`
- `country_dashboard/test_country_dashboard.py:72` `TestSmokeCountryDashboard` (class)
- `grievance/grievance_tickets/test_e2e_grievance_tickets.py:429` system-generated page, `:454` details page, `:492` details normal program, `:574/:586/:591/:596/:601` (5 parametrized cases of create-new-tickets), `:1133` `test_grievance_tickets_process_tickets`, `:1231` `test_grievance_tickets_needs_adjudication`
- `grievance/feedback/test_feedback.py:281` optional-fields, `:315` programme-filter, `:486` linked-ticket

**`UNSTABLE AFTER REST REFACTOR` (4)**
- `targeting/test_targeting.py:994` `test_create_targeting_with_pdu_bool_criteria`, `:1071` `test_create_targeting_with_pdu_decimal_criteria`
- `people/test_people.py:227` `TestPeople` (class)
- `grievance/feedback/test_feedback.py:390` `test_create_feedback_with_household_and_individual`

**Deadlock — issue 202318 (9)**
- `targeting/test_targeting.py:1360` create-use-ids-individual, `:1394` rebuild, `:1433` copy, `:1519` different-program-statuses, `:1629` sanction-screen-flag, `:1801` parametrized-rules-and-or
- `grievance/feedback/test_feedback.py:361` with-household, `:421` with-individual
- `payment_module/test_e2e_payment_plans.py:575` `test_payment_plan_happy_path` ("psycopg2… DeadlockDetected")

**Other one-offs (2)**
- `targeting/test_targeting.py:1459` `test_edit_targeting` — "Problem with select_listbox_element or getButtonIconEdit"
- `targeting/test_targeting.py:1556` `test_exclude_households_with_active_adjudication_ticket` — "UNSTABLE AFTER PAYMENT CHANNEL VALIDATION SECTION ADDED"

*(Note: the 5 `grievance_tickets` marks at 574–601 are parametrized cases of a single test function.)*

### 4c. `night`-marked (19) — configuration gap (unchanged by PR)

`@pytest.mark.night` is still **not** declared in `tests/pytest.ini` (registered markers are
only `elasticsearch`, `isolated`, `unit`, `selenium`). These tests run under an unregistered
marker, so whether they execute depends on an external `-m` selection. Located in:
`programme_management/`, `filters/`, `targeting/`, `registration_data_import/`,
`people/test_people_periodic_data_update.py`, and `grievance/grievance_tickets/`.

### 4d. Commented-out tests & in-body skips

**None found** in either suite — disabling is done exclusively via decorators (good hygiene).

---

## 5. What PR #6154 added (now counted as covered)

| Area | Tests |
|---|---|
| **Country Search** (`country_search/test_country_search.py`) | `test_country_search_finds_household_by_id`, `test_country_search_finds_individual_by_id`, `test_country_search_shows_no_results_for_unknown_id` |
| **Access Denied** (`access_denied/test_access_denied.py`) | `test_access_denied_for_user_without_business_area` |
| **Error page / 404** (`error_page/test_error_page.py`) | `test_page_not_found_for_missing_program`, `test_page_not_found_for_unknown_route` |
| **Managerial Console** (re-enabled) | `test_managerial_console_renders_all_sections`, `test_managerial_console_happy_path` |
| **Grievance Dashboard** (re-enabled) | `test_smoke_grievance_dashboard` (xfail removed) |

New page objects: `page_object/country_search/`, `page_object/error_page/`. Deleted stale
`page_object/404.py`.

---

## 6. Remaining backlog (prioritized) — NOT addressed by PR #6154

1. **Fix deadlock 202318** — single highest-leverage fix; still gates 8 targeting/feedback `xfail`s plus the payment-plan happy-path deadlock.
2. **Re-validate remaining REST-refactor `xfail`s** (~4: people `TestPeople`, targeting PDU bool/decimal, feedback with-hh-and-individual) — likely stale selectors.
3. **Register or retire the `night` marker** in `tests/pytest.ini` (19 tests, config gap).
4. **Add net-new coverage** for the still-never-covered gaps, in priority order:
   **Duplicate Program** → **Payment Details page** → **online templates / authorized-users** → **Program Users management** → **Activity Log content** → **Maintenance page**.
5. **Un-disable Country Dashboard** — currently zero real protection (only test is xfail).
6. ~~**Address the `program_details` date-fix skips** (211823 / 212581) and the **filters "ToDo" skips**.~~ **Done** — all 4 `program_details` date-fix tests un-skipped (fixed the `AddNewProgramCycle` blank-dialog bug behind 211823) and both filters `"ToDo"` stubs implemented as real list-filter tests.
