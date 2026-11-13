# Plan: move old Selenium suite into `tests/e2e/new_selenium`

## Context
`tests/e2e` holds two Selenium suites:
- **old**: raw Selenium with `Common → BaseComponents → PageObject` (`tests/e2e/page_object/**`, `tests/e2e/helpers/helper.py`), class-based tests, autouse `driver/browser/login` fixtures in `tests/e2e/conftest.py`.
- **new**: SeleniumBase `HopeTestBrowser` (`tests/extras/test_utils/selenium.py`) + `browser`/`login`/`grant_permission`/`user_with_no_permissions` in `tests/e2e/new_selenium/conftest.py`, rules in `tests/e2e/SELENIUM_E2E_PATTERNS.md`.

Goal: re-cover every scenario from the old `tests/e2e` suite as a new-style Selenium test in `tests/e2e/new_selenium/`, delete each old test once its scenario is covered, and finally delete the old infrastructure.

## Rules for every migration PR (one module = one PR)
1. Write new tests in `tests/e2e/new_selenium/<module>/` following `SELENIUM_E2E_PATTERNS.md`: plain `def test_*`, no classes, no `sleep`, no autouse data fixtures, no `if/for` in test bodies, factories from `extras.test_utils.factories` (not `old_factories`), `data-cy` CSS selectors, `pytest.mark.parametrize` instead of loops, `grant_permission` for permission scenarios.
2. Domain data fixtures go in the module `conftest.py`; reuse existing ones (`new_selenium/payment_module/conftest.py`, `targeting/conftest.py`, `grievance/conftest.py`, `program_details/conftest.py`, `programme_population/conftest.py`) before writing new ones.
3. Each old test gets one of two outcomes:
   - **NEW** – port the scenario as a new-style Selenium test (file named in the checklist). Several old tests may merge into one parametrized test when they are the same flow with different data.
   - **COVERED** – an existing `new_selenium` test already exercises the same scenario (name it in the PR description). Before deleting the old test, compare it step by step with the new one and add any missing assertions to the new test.
4. Delete the old test file **and** any page object / old conftest fixture that becomes unused in the same PR.
5. Update the counter below in the same PR.
6. Verify: `tox -e tests -- tests/e2e/new_selenium/<module>/` (plus one `-n auto` run to check xdist isolation), `tox -e lint`, `tox -e mypy`.

## Progress counter
Units = old `def test_*` functions (parametrize cases count once). Recount the remaining ones with:
```bash
grep -rcE '^\s*def test_' tests/e2e --include='test_*.py' --exclude-dir=new_selenium | awk -F: '{s+=$2} END {print s}'
```

| # | Module (old path) | Old tests | Migrated | Status |
|---|---|---:|---:|---|
| 1 | `login_via_admin_panel` | 7 | 7 | ✅ |
| 2 | `error_page` + `access_denied` | 3 | 3 | ✅ |
| 3 | `program_log` | 2 | 0 | ⬜ |
| 4 | `programme_user` | 1 | 0 | ⬜ |
| 5 | `country_search` | 3 | 0 | ⬜ |
| 6 | `country_dashboard` | 1 | 0 | ⬜ |
| 7 | `managerial_console` | 2 | 0 | ⬜ |
| 8 | `drawer` | 4 | 0 | ⬜ |
| 9 | `accountability` | 4 | 0 | ⬜ |
| 10 | `programme_population` (hh/ind/PDU) | 12 | 0 | ⬜ |
| 11 | `people` | 7 | 0 | ⬜ |
| 12 | `programme_management` | 8 | 0 | ⬜ |
| 13 | `generic_import` | 15 | 0 | ⬜ |
| 14 | `filters` | 4 | 0 | ⬜ |
| 15 | `payment_verification` | 10 | 0 | ⬜ |
| 16 | `payment_module` | 9 | 0 | ⬜ |
| 17 | `targeting` | 21 | 0 | ⬜ |
| 18 | `grievance/feedback` | 12 | 0 | ⬜ |
| 19 | `grievance/grievance_dashboard` | 2 | 0 | ⬜ |
| 20 | `grievance/grievance_tickets` | 25 | 0 | ⬜ |
| 21 | Old infra cleanup | – | – | ⬜ |
| | **Total** | **155** | **10** | **6 %** |

`[█░░░░░░░░░░░░░░░░░░░] 10 / 155`. Update it after each PR: 1 block per ~8 tests.

The new suite already has 46 test files and ~250 test functions. These do not count toward the 155.

Order: small, isolated modules first (1–9) to settle shared fixtures, then population/programme (10–14), then payments/targeting/grievance (15–20), which overlap most with tests already in the new suite.

---

## Per-module action points

Legend: `NEW <new_selenium/...>` · `COVERED <existing new test>` (verify assertions, then delete).

### 1. `login_via_admin_panel/test_login.py` (7) → `new_selenium/auth/test_admin_login.py`
- [x] test_login_superuser → NEW `test_admin_login[superuser]`
- [x] test_login_normal_user → NEW `test_admin_login[staff-without-permissions]`
- [x] test_login_with_valid_username_and_invalid_password → NEW `test_admin_login_with_invalid_credentials_shows_error[invalid-password]`
- [x] test_login_with_invalid_username_and_valid_password → NEW `…[invalid-username]`
- [x] test_login_with_invalid_username_and_invalid_password → NEW `…[invalid-username-and-password]`
- [x] test_not_logged_main_page → NEW `test_anonymous_user_sees_login_page`
- [x] test_log_out_via_admin_panel → NEW `test_log_out_via_admin_panel`
- [ ] `page_object/admin_panel/` and the `page_admin_panel` fixture are still used by `grievance_tickets/test_e2e_grievance_tickets.py::test_grievance_tickets_go_to_admin_panel_button`. Delete them in module 20.

### 2. `error_page/` (2) + `access_denied/` (1) → `new_selenium/error_page/test_error_pages.py`
- [x] test_page_not_found_for_missing_program → NEW `test_page_not_found[missing-program]`
- [x] test_page_not_found_for_unknown_route → NEW `test_page_not_found[unknown-route]`
- [x] test_access_denied_for_user_without_business_area → NEW `test_access_denied_for_user_without_business_area`
- [x] Delete `page_object/error_page/` and the `page_error` / `page_access_denied` fixtures

### 3. `program_log/test_program_log.py` (2) → `new_selenium/activity_log/test_activity_log.py`
- [ ] test_smoke_program_log → NEW (programme log lists an entry created by a factory)
- [ ] test_smoke_activity_log → NEW
- [ ] Delete `page_object/program_log/`

### 4. `programme_user/test_programme_user.py` (1) → `new_selenium/program_details/test_programme_users.py`
- [ ] test_smoke_programme_users → NEW
- [ ] Delete `page_object/programme_users/`

### 5. `country_search/test_country_search.py` (3) → `new_selenium/country_search/test_country_search.py`
- [ ] test_country_search_finds_household_by_id → NEW, parametrize household / individual
- [ ] test_country_search_finds_individual_by_id → NEW (param)
- [ ] test_country_search_shows_no_results_for_unknown_id → NEW
- [ ] Delete `page_object/country_search/`

### 6. `country_dashboard/test_country_dashboard.py` (1) → `new_selenium/dashboard/test_country_dashboard.py`
- [ ] test_smoke_country_dashboard → NEW (assert values from factory data, not only labels)
- [ ] Delete `page_object/country_dashboard/`

### 7. `managerial_console/test_managerial_console.py` (2) → `new_selenium/managerial_console/test_managerial_console.py`
- [ ] test_managerial_console_renders_all_sections → NEW
- [ ] test_managerial_console_happy_path → NEW
- [ ] Delete `page_object/managerial_console/`

### 8. `drawer/test_drawer.py` (4) → `new_selenium/navigation/test_drawer.py`
- [ ] test_social_worker_program_drawer_order → NEW, parametrize social worker / normal / all programmes
- [ ] test_normal_program_drawer_order → NEW (param)
- [ ] test_all_program_drawer_order → NEW (param)
- [ ] test_inactive_draft_subheader → NEW

### 9. `accountability/` (4) → `new_selenium/accountability/`
- [ ] test_smoke_accountability_communication → NEW `test_communication.py`
- [ ] test_smoke_accountability_communication_details → NEW `test_communication.py`
- [ ] test_smoke_accountability_surveys → NEW `test_surveys.py`
- [ ] test_smoke_accountability_surveys_details → NEW `test_surveys.py`
- [ ] Delete `page_object/accountability/`

### 10. `programme_population/` (12) → `new_selenium/programme_population/`
- [ ] test_smoke_page_households → NEW `test_households.py`
- [ ] test_smoke_page_households_details → NEW `test_households.py`
- [ ] test_smoke_page_individuals → NEW `test_individuals.py`
- [ ] test_smoke_page_individuals_details → NEW `test_individuals.py`
- [ ] test_periodic_data_template_export_and_download → NEW `test_periodic_data_templates.py`
- [ ] test_periodic_data_template_list → NEW `test_periodic_data_templates.py`
- [ ] test_periodic_data_template_details → NEW `test_periodic_data_templates.py`
- [ ] test_periodic_data_template_create_and_download → NEW `test_periodic_data_templates.py`
- [ ] test_periodic_data_update_upload_success → NEW `test_periodic_data_xlsx_upload.py`
- [ ] test_periodic_data_update_upload_form_error → NEW `test_periodic_data_xlsx_upload.py`, parametrize form error / upload error
- [ ] test_periodic_data_update_upload_error → NEW (param)
- [ ] test_periodic_data_uploads_list → NEW `test_periodic_data_xlsx_upload.py`
- [ ] Delete `page_object/programme_population/`

### 11. `people/` (7) → `new_selenium/people/`
- [ ] test_smoke_page_people → NEW `test_people.py`
- [ ] test_smoke_page_details_people → NEW `test_people.py`
- [ ] test_people_happy_path → NEW `test_people.py`
- [ ] test_check_people_data_after_grievance_ticket_processed → NEW `test_people.py` (keep the parametrize)
- [ ] test_people_periodic_data_update_upload_success → NEW `test_people_periodic_data_update.py` (share fixtures with module 10)
- [ ] test_people_periodic_data_update_upload_form_error → NEW `test_people_periodic_data_update.py`
- [ ] test_people_periodic_data_uploads_list → NEW `test_people_periodic_data_update.py`
- [ ] Delete `page_object/people/`

### 12. `programme_management/test_programme_management.py` (8) → `new_selenium/program_details/`
Already in new suite: `test_create_program.py`, `test_edit_program.py`, `test_duplicate_program.py`.
- [ ] test_create_programme_check → COVERED `test_create_programme_mandatory_fields_only` / `_all_fields` (add any parametrize case that is missing)
- [ ] test_create_programme_delete_partners → NEW `test_programme_partners.py`
- [ ] test_create_programme_add_partners_business_area → NEW `test_programme_partners.py`
- [ ] test_create_programme_back_scenarios → NEW `test_create_program.py`
- [ ] test_create_programme_chose_dates_via_calendar → NEW `test_create_program.py` (use `helpers/date_picker`)
- [ ] test_create_programme_accesses → NEW `test_programme_partners.py` (keep the parametrize)
- [ ] test_programme_partners → NEW `test_programme_partners.py`
- [ ] test_edit_programme_with_rdi → NEW `test_edit_program.py`
- [ ] Delete `page_object/programme_management/`, `page_object/programme_details/`

### 13. `generic_import/test_generic_import.py` (15) → `new_selenium/generic_import/test_generic_import_form.py`
Already in new suite: `test_generic_import_data.py`.
- [ ] test_xlsx_file_path → NEW (fixture file is valid and loads; fold into the happy-path setup if it's only a sanity check)
- [ ] test_happy_path_full_import → COVERED `test_generic_import_creates_rdi_with_household_individual_document_and_account`
- [ ] test_business_area_is_required_field → NEW
- [ ] test_program_select_disabled_until_ba_selected → NEW
- [ ] test_file_upload_field_exists → NEW (merge into the form-render test)
- [ ] test_validation_invalid_file_extension → NEW
- [ ] test_dynamic_program_loading → NEW
- [ ] test_business_area_change_resets_program → NEW
- [ ] test_drag_and_drop_file_upload → NEW
- [ ] test_autoselect_single_business_area → NEW, parametrize business area / program
- [ ] test_autoselect_single_program → NEW (param)
- [ ] test_no_permission_access_denied → NEW (uses `user_with_no_permissions`)
- [ ] test_import_with_validation_errors → NEW (uses `helpers/e2e_generic_import_invalid.xlsx`)
- [ ] test_file_size_display → NEW
- [ ] test_submit_button_state_during_upload → NEW
- [ ] Delete `page_object/generic_import/`

### 14. `filters/test_filters.py` (4) → filter tests go in each domain module (pattern: `targeting/test_tp_list.py::test_tp_list_filter`)
- [ ] test_filters_selected_program → NEW `new_selenium/filters/test_list_filters.py` (keep the parametrize over pages), or split per domain module
- [ ] test_filters_happy_path_search_filter → NEW (same file)
- [ ] test_grievance_tickets_filters_of_households_and_individuals → NEW `new_selenium/grievance/test_ticket_list.py`
- [ ] test_payment_verification_list_filters → NEW `new_selenium/payment_verification/test_verification_list.py`
- [ ] Delete `page_object/filters.py` and the `filters` fixture

### 15. `payment_verification/test_payment_verification.py` (10) → `new_selenium/payment_verification/`
Already in new suite: `test_activate_verification_plan.py`.
- [ ] test_smoke_payment_verification → NEW `test_verification_list.py`
- [ ] test_smoke_payment_verification_details → NEW `test_verification_list.py`
- [ ] test_happy_path_payment_verification → COVERED `test_activate_verification_plan_flow` (extend it to finish the plan if needed)
- [ ] test_payment_verification_successful_not_received → NEW `test_manual_verification.py`
- [ ] test_payment_verification_partially_successful_received_and_grievance_ticket → NEW `test_manual_verification.py`
- [ ] test_payment_verification_xlsx_successful → NEW `test_xlsx_verification.py`, parametrize successful / partially / not received
- [ ] test_payment_verification_xlsx_partially_successful → NEW (param)
- [ ] test_payment_verification_xlsx_not_received → NEW (param)
- [ ] test_payment_verification_discard → NEW `test_activate_verification_plan.py`
- [ ] test_payment_verification_xlsx_invalid → NEW `test_xlsx_verification.py`
- [ ] Delete `page_object/payment_verification/`

### 16. `payment_module/test_e2e_payment_plans.py` (9) → `new_selenium/payment_module/`
Already in new suite: lifecycle, entitlement, top-up, group, details, close, follow-up, cycles.
- [ ] test_smoke_payment_plan → NEW `test_payment_plan_list.py`
- [ ] test_smoke_new_payment_plan → NEW `test_create_payment_plan.py`
- [ ] test_smoke_details_payment_plan → NEW `test_payment_plan_details.py`, unless `test_payment_details.py` already asserts the same sections
- [ ] test_payment_plan_happy_path → NEW `test_create_payment_plan.py` (create → lock → entitlement → approve → authorize → release)
- [ ] test_payment_plan_exclude_not_lock_error → NEW `test_payment_plan_exclusions.py`
- [ ] test_payment_plan_save_exclude_people → NEW `test_payment_plan_exclusions.py`, parametrize people / households
- [ ] test_payment_plan_save_exclude → NEW (param)
- [ ] test_payment_plan_creation_error → NEW `test_create_payment_plan.py`
- [ ] test_payment_plan_supporting_documents → NEW `test_supporting_documents.py`
- [ ] Delete `page_object/payment_module/`

### 17. `targeting/test_targeting.py` (21) → `new_selenium/targeting/`
Already in new suite: target population, criteria, list, permissions, status flow, vulnerability score, social-worker exclusions.
- [ ] test_smoke_targeting_page → COVERED `test_tp_list.py` / `test_tp_list_shows_group_header_row`
- [ ] test_smoke_targeting_create_use_filters → COVERED `test_tp_criteria.py`
- [ ] test_smoke_targeting_create_use_ids → NEW `test_tp_by_ids.py`
- [ ] test_smoke_targeting_details_page → COVERED `test_tp_details_shows_group_and_purpose`
- [ ] test_create_targeting_for_people → NEW `test_tp_criteria.py` (social worker programme)
- [ ] test_create_targeting_for_normal_program → COVERED `test_household_size_rule_targets_only_matching_households`
- [ ] test_create_targeting_with_pdu_string_criteria → NEW `test_tp_pdu_criteria.py`, parametrize string / bool / decimal / date / null
- [ ] test_create_targeting_with_pdu_bool_criteria → NEW (param)
- [ ] test_create_targeting_with_pdu_decimal_criteria → NEW (param)
- [ ] test_create_targeting_with_pdu_date_criteria → NEW (param)
- [ ] test_create_targeting_with_pdu_null_criteria → NEW (param)
- [ ] test_create_targeting_for_people_with_pdu → NEW `test_tp_pdu_criteria.py`
- [ ] test_targeting_create_use_ids_hh → NEW `test_tp_by_ids.py`, parametrize household / individual
- [ ] test_targeting_create_use_ids_individual → NEW (param)
- [ ] test_copy_targeting → COVERED `test_duplicate_tp_with_group_and_purpose` / `test_duplicate_locked_tp_creates_open_copy`
- [ ] test_edit_targeting → COVERED `test_edit_tp_shows_group_and_purpose`
- [ ] test_exclude_households_with_sanction_screen_flag → NEW `test_tp_criteria.py` (next to the adjudication flag test)
- [ ] test_targeting_info_button → NEW `test_target_population.py`
- [ ] test_targeting_and_labels → NEW `test_tp_criteria.py`
- [ ] test_targeting_parametrized_rules_filters → NEW `test_tp_criteria.py` (keep the parametrize)
- [ ] test_targeting_parametrized_rules_filters_and_or → COVERED `test_or_criteria_target_households_matching_either_rule` (add missing cases)
- [ ] Delete `page_object/targeting/`

### 18. `grievance/feedback/test_feedback.py` (12) → `new_selenium/grievance/test_feedback.py`
- [ ] test_check_feedback_page → NEW
- [ ] test_check_feedback_details_page → NEW
- [ ] test_create_feedback_mandatory_fields → NEW (keep the parametrize)
- [ ] test_create_feedback_optional_fields → NEW (keep the parametrize)
- [ ] test_check_feedback_filtering_by_chosen_programme → NEW
- [ ] test_create_feedback_with_household → NEW, parametrize household / household+individual / individual
- [ ] test_create_feedback_with_household_and_individual → NEW (param)
- [ ] test_create_feedback_with_individual → NEW (param)
- [ ] test_edit_feedback → NEW
- [ ] test_create_linked_ticket → NEW
- [ ] test_feedback_errors → NEW
- [ ] test_feedback_identity_verification → NEW

### 19. `grievance/grievance_dashboard/test_grievance_dashboard.py` (2) → `new_selenium/grievance/test_grievance_dashboard.py`
- [ ] test_smoke_grievance_dashboard → NEW
- [ ] test_grievance_dashboard_happy_path → NEW (numbers come from factory tickets)

### 20. `grievance/grievance_tickets/test_e2e_grievance_tickets.py` (25) → `new_selenium/grievance/`
Already in new suite: `test_grievance_tickets.py` (referral), `test_my_tasks.py`, `test_needs_adjudication_management.py`, `test_household_data_update_admin_area.py`, `test_latin_names_data_change.py`. Split into 3 PRs: list/details, create, process.
- [ ] test_check_grievance_tickets_user_generated_page → NEW `test_ticket_list.py`, parametrize user / system generated
- [ ] test_check_grievance_tickets_system_generated_page → NEW (param)
- [ ] test_check_grievance_tickets_details_page → NEW `test_ticket_details.py`, parametrize programme type
- [ ] test_check_grievance_tickets_details_page_normal_program → NEW (param)
- [ ] test_check_grievance_tickets_details_page_social_worker_program → NEW (param)
- [ ] test_grievance_tickets_create_new_tickets → NEW `test_grievance_tickets.py` (extend the parametrize next to referral)
- [ ] test_grievance_tickets_create_new_tickets_social_program → NEW (param)
- [ ] test_grievance_tickets_create_new_ticket_data_change_add_individual_all_fields → NEW `test_data_change_tickets.py`
- [ ] test_grievance_tickets_create_new_ticket_data_change_add_individual_mandatory_fields → NEW `test_data_change_tickets.py` (check overlap with `test_latin_names_data_change.py`)
- [ ] test_hh_grievance_tickets_create_new_ticket → NEW `test_data_change_tickets.py` (keep the parametrize)
- [ ] test_grievance_tickets_create_new_ticket → NEW `test_data_change_tickets.py` (keep the parametrize)
- [ ] test_grievance_tickets_create_new_tickets_grievance_complaint_partner_related_complaint → NEW `test_grievance_tickets.py`, parametrize partner / payment complaint
- [ ] test_grievance_tickets_create_new_tickets_grievance_complaint_payment_related_complaint → NEW (param)
- [ ] test_grievance_tickets_look_up_linked_ticket → NEW `test_ticket_details.py`
- [ ] test_grievance_tickets_add_documentation → NEW `test_ticket_details.py`
- [ ] test_grievance_tickets_check_identity_verification → NEW `test_ticket_details.py`
- [ ] test_grievance_tickets_edit_tickets_from_main_grievance_page → NEW `test_ticket_list.py` (check overlap with `test_my_tasks.py::test_bulk_assign_*`)
- [ ] test_grievance_tickets_process_tickets → NEW `test_ticket_processing.py`
- [ ] test_grievance_tickets_add_note → NEW `test_ticket_details.py`
- [ ] test_grievance_tickets_activity_log → NEW `test_ticket_details.py`
- [ ] test_grievance_tickets_go_to_admin_panel_button → NEW `test_ticket_details.py`
- [ ] test_grievance_tickets_needs_adjudication → COVERED `test_needs_adjudication_management.py`, if the ticket-details NA flow is covered; otherwise NEW `test_ticket_processing.py`
- [ ] test_grievance_tickets_create_new_error → NEW `test_grievance_tickets.py`
- [ ] test_grievance_tickets_individual_data_update_with_photo → NEW `test_data_change_tickets.py`, parametrize update / add (uses `helpers/document_example.png`)
- [ ] test_grievance_tickets_add_individual_with_photo → NEW (param)
- [ ] Delete `page_object/grievance/`

### 21. Old infrastructure cleanup (after the counter reaches 155/155)
- [ ] Delete `tests/e2e/page_object/` (incl. `base_components.py`), `tests/e2e/helpers/helper.py`, `helpers/fixtures.py`, `helpers/date_time_format.py` if unused, `tools/tag_name_finder.py`
- [ ] Strip `tests/e2e/conftest.py` of `driver`, the autouse `browser`, `login`, `page_*`/`filters` fixtures, `create_session`, and `screenshot_path`/`download_path` if unused. Keep the DB/cache autouse fixtures and `live_server_with_static`.
- [ ] Remove the "Existing raw Selenium tests…" note from `SELENIUM_E2E_PATTERNS.md`, update `tests/e2e/README.md`
- [ ] Check CI / tox / compose files (`compose.selenium.yml`, `.github/workflows`) for paths to old dirs
- [ ] Final: `tox -e tests -- tests/e2e`, `tox -e lint`, `tox -e mypy` green; the recount command prints 0

## Verification (per PR)
- `tox -e tests -- tests/e2e/new_selenium/<module>/` green, plus one `-n auto` run for xdist isolation
- `tox -e lint`, `tox -e mypy`
- Old test file removed and the counter table updated
