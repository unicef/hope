from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class PaymentVerificationDetails(BaseComponents):
    # Locators
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_new_plan = 'button[data-cy="button-new-plan"]'
    button_edit_plan = 'button[data-cy="button-edit-plan"]'
    div_payment_plan_details = 'div[data-cy="div-payment-plan-details"]'
    grid_payment_plan_details = 'div[data-cy="grid-payment-plan-details"]'
    label_programme_name = 'div[data-cy="label-PROGRAMME NAME"]'
    label_payment_records = 'div[data-cy="label-PAYMENT RECORDS"]'
    label_start_date = 'div[data-cy="label-START DATE"]'
    label_end_date = 'div[data-cy="label-END DATE"]'
    grid_bank_reconciliation = 'div[data-cy="grid-bank-reconciliation"]'
    table_label = 'h6[data-cy="table-label"]'
    label_successful = 'div[data-cy="label-SUCCESSFUL"]'
    label_erroneous = 'div[data-cy="label-ERRONEOUS"]'
    grid_verification_plans_summary = 'div[data-cy="grid-verification-plans-summary"]'
    label_status = 'div[data-cy="label-Status"]'
    verification_plans_summary_status = 'div[data-cy="verification-plans-summary-status"]'
    labelized_field_container_summary_activation_date = (
        'div[data-cy="labelized-field-container-summary-activation-date"]'
    )
    label_activation_date = 'div[data-cy="label-Activation Date"]'
    labelized_field_container_summary_completion_date = (
        'div[data-cy="labelized-field-container-summary-completion-date"]'
    )
    label_completion_date = 'div[data-cy="label-Completion Date"]'
    labelized_field_container_summary_number_of_plans = (
        'div[data-cy="labelized-field-container-summary-number-of-plans"]'
    )
    label_number_of_verification_plans = 'div[data-cy="label-Number of Verification Plans"]'
    button_delete_plan = 'button[data-cy="button-delete-plan"]'
    verification_plan = 'h6[data-cy="verification-plan-{}"]'
    verification_plan_prefix = 'h6[data-cy^="verification-plan"]'
    button_activate_plan = 'button[data-cy="button-activate-plan"]'
    export_xlsx = 'button[data-cy="export-xlsx"]'
    download_xlsx = 'button[data-cy="download-xlsx"]'
    button_mark_as_invalid = '[data-cy="button-mark-as-invalid"]'
    import_xlsx = 'div[data-cy="import-xlsx"]'
    button_import_entitlement = 'button[data-cy="button-import-entitlement"]'
    verification_plan_status = 'div[data-cy="verification-plan-status"]'
    label_sampling = 'div[data-cy="label-SAMPLING"]'
    label_responded = 'div[data-cy="label-RESPONDED"]'
    label_received_with_issues = 'div[data-cy="label-RECEIVED WITH ISSUES"]'
    label_verification_channel = 'div[data-cy="label-VERIFICATION CHANNEL"]'
    label_sample_size = 'div[data-cy="label-SAMPLE SIZE"]'
    label_received = 'div[data-cy="label-RECEIVED"]'
    label_not_received = 'div[data-cy="label-NOT RECEIVED"]'
    label_status_div = 'div[data-cy="label-STATUS"]'
    label_activation_date_div = 'div[data-cy="label-ACTIVATION DATE"]'
    label_completion_date_div = 'div[data-cy="label-COMPLETION DATE"]'
    button_submit = 'button[data-cy="button-submit"]'
    button_finish = 'button[data-cy="button-ed-plan"]'
    rows = 'tr[role="checkbox"]'
    button_discard = 'button[data-cy="button-discard-plan"]'
    age_min_input = 'input[data-cy="input-filterAgeMin"]'
    age_max_input = 'input[data-cy="input-filterAgeMax"]'
    sex_select = 'div[data-cy="select-filterSex"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_new_plan(self) -> WebElement:
        return self.wait_for(self.button_new_plan)

    def get_button_edit_plan(self) -> WebElement:
        return self.wait_for(self.button_edit_plan)

    def get_div_payment_plan_details(self) -> WebElement:
        return self.wait_for(self.div_payment_plan_details)

    def get_grid_payment_plan_details(self) -> WebElement:
        return self.wait_for(self.grid_payment_plan_details)

    def get_label_programme_name(self) -> WebElement:
        return self.wait_for(self.label_programme_name)

    def get_label_payment_records(self) -> WebElement:
        return self.wait_for(self.label_payment_records)

    def get_label_start_date(self) -> WebElement:
        return self.wait_for(self.label_start_date)

    def get_label_end_date(self) -> WebElement:
        return self.wait_for(self.label_end_date)

    def get_grid_bank_reconciliation(self) -> WebElement:
        return self.wait_for(self.grid_bank_reconciliation)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_label_successful(self) -> WebElement:
        return self.wait_for(self.label_successful)

    def get_label_erroneous(self) -> WebElement:
        return self.wait_for(self.label_erroneous)

    def get_grid_verification_plans_summary(self) -> WebElement:
        return self.wait_for(self.grid_verification_plans_summary)

    def get_label_status(self) -> WebElement:
        return self.wait_for(self.label_status)

    def get_verification_plans_summary_status(self) -> WebElement:
        return self.wait_for(self.verification_plans_summary_status)

    def get_labelized_field_container_summary_activation_date(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_summary_activation_date)

    def get_label_activation_date(self) -> WebElement:
        return self.wait_for(self.label_activation_date)

    def get_labelized_field_container_summary_completion_date(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_summary_completion_date)

    def get_label_completion_date(self) -> WebElement:
        return self.wait_for(self.label_completion_date)

    def get_labelized_field_container_summary_number_of_plans(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_summary_number_of_plans)

    def get_label_number_of_verification_plans(self) -> WebElement:
        return self.wait_for(self.label_number_of_verification_plans)

    def get_button_delete_plan(self) -> WebElement:
        return self.wait_for(self.button_delete_plan)

    def delete_verification_plan_by_number(self, number: int) -> None:
        self.get_elements(self.button_delete_plan)[number].click()

    def get_verification_plan_name(self, name: str) -> WebElement:
        return self.wait_for(self.verification_plan.format(name))

    def get_verification_plan_prefix(self) -> [WebElement]:
        return self.get_elements(self.verification_plan_prefix)

    def get_button_activate_plan(self) -> WebElement:
        return self.wait_for(self.button_activate_plan)

    def get_export_xlsx(self) -> WebElement:
        return self.wait_for(self.export_xlsx, timeout=120)

    def get_download_xlsx(self) -> WebElement:
        return self.wait_for(self.download_xlsx)

    def get_button_mark_as_invalid(self) -> WebElement:
        return self.wait_for(self.button_mark_as_invalid)

    def get_button_discard(self) -> WebElement:
        return self.wait_for(self.button_discard)

    def get_import_xlsx(self) -> WebElement:
        return self.wait_for(self.import_xlsx)

    def get_button_import_entitlement(self) -> WebElement:
        return self.wait_for(self.button_import_entitlement)

    def get_verification_plan_status(self) -> WebElement:
        return self.wait_for(self.verification_plan_status)

    def get_label_sampling(self) -> WebElement:
        return self.wait_for(self.label_sampling)

    def get_label_responded(self) -> WebElement:
        return self.wait_for(self.label_responded)

    def get_label_received_with_issues(self) -> WebElement:
        return self.wait_for(self.label_received_with_issues)

    def get_label_verification_channel(self) -> WebElement:
        return self.wait_for(self.label_verification_channel)

    def get_label_sample_size(self) -> WebElement:
        return self.wait_for(self.label_sample_size)

    def get_label_received(self) -> WebElement:
        return self.wait_for(self.label_received)

    def get_label_not_received(self) -> WebElement:
        return self.wait_for(self.label_not_received)

    def get_label_activation_date_div(self) -> WebElement:
        return self.wait_for(self.label_activation_date_div)

    def get_label_completion_date_div(self) -> WebElement:
        return self.wait_for(self.label_completion_date_div)

    def get_label_status_div(self) -> WebElement:
        return self.wait_for(self.label_status_div)

    def get_button_submit(self) -> WebElement:
        return self.wait_for(self.button_submit)

    def get_button_finish(self) -> WebElement:
        return self.wait_for(self.button_finish)

    def get_rows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)

    def get_age_min_input(self) -> WebElement:
        return self.wait_for(self.age_min_input)

    def get_age_max_input(self) -> WebElement:
        return self.wait_for(self.age_max_input)

    def get_sex_select(self) -> WebElement:
        return self.wait_for(self.sex_select)
