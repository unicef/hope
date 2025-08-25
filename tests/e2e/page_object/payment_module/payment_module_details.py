from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentModuleDetails(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    pp_unicef_id = 'span[data-cy="pp-unicef-id"]'
    status_container = 'div[data-cy="status-container"]'
    button_export_xlsx = 'button[data-cy="button-export-xlsx"]'
    button_download_xlsx = 'a[data-cy="button-download-xlsx"]'
    label_created_by = 'div[data-cy="label-Created By"]'
    label_target_population = 'div[data-cy="label-Target Population"]'
    label_currency = 'div[data-cy="label-Currency"]'
    label_start_date = 'div[data-cy="label-Start Date"]'
    label_end_date = 'div[data-cy="label-End Date"]'
    label_dispersion_start_date = 'div[data-cy="label-Dispersion Start Date"]'
    label_dispersion_end_date = 'div[data-cy="label-Dispersion End Date"]'
    label_related_follow_up_payment_plans = 'div[data-cy="label-Related Follow-Up Payment Plans"]'
    button_set_up_fsp = 'a[data-cy="button-set-up-fsp"]'
    button_create_exclusions = 'button[data-cy="button-create-exclusions"]'
    button_save_exclusions = 'button[data-cy="button-save-exclusions"]'
    supporting_documents_title = 'h6[data-cy="supporting-documents-title"]'
    supporting_documents_empty = 'div[data-cy="supporting-documents-empty"]'
    input_exclusion = 'textarea[data-cy="input-exclusion"]'
    input_exclusion_reason = 'textarea[data-cy="input-exclusionReason"]'
    input_households_ids = '[data-cy="input-households-ids"]'
    input_beneficiaries_ids = '[data-cy="input-beneficiaries-ids"]'
    button_apply_exclusions = 'button[data-cy="button-apply-exclusions"]'
    label_female_children = 'div[data-cy="label-Female Children"]'
    label_female_adults = 'div[data-cy="label-Female Adults"]'
    label_male_children = 'div[data-cy="label-Male Children"]'
    label_male_adults = 'div[data-cy="label-Male Adults"]'
    chart_container = 'div[data-cy="chart-container"]'
    label_total_number_of_households = 'div[data-cy="label-Total Number of Items Groups"]'
    label_total_number_of_people = 'div[data-cy="label-Total Number of People"]'
    label_targeted_individuals = 'div[data-cy="label-Targeted Items"]'
    table_title = 'h6[data-cy="table-title"]'
    button_import = 'button[data-cy="button-import"]'
    table_label = 'span[data-cy="table-label"]'
    table_row = 'tr[data-cy="table-row"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    label_delivered_fully = 'div[data-cy="label-Delivered fully"]'
    label_delivered_partially = 'div[data-cy="label-Delivered partially"]'
    label_not_delivered = 'div[data-cy="label-Not delivered"]'
    label_unsuccessful = 'div[data-cy="label-Unsuccessful"]'
    label_pending = 'div[data-cy="label-Pending"]'
    label_number_of_payments = 'div[data-cy="label-Number of payments"]'
    label_reconciled = 'div[data-cy="label-Reconciled"]'
    label_total_entitled_quantity = 'div[data-cy="label-Total Entitled Quantity"]'
    button_lock_plan = 'button[data-cy="button-lock-plan"'
    button_submit = 'button[data-cy="button-submit"]'
    input_entitlement_formula = 'div[data-cy="input-entitlement-formula"]'
    button_apply_steficon = 'button[data-cy="button-apply-steficon"]'
    select_delivery_mechanism = 'div[data-cy="select-deliveryMechanisms[0].deliveryMechanism"]'
    select_delivery_mechanisms_fsp = 'div[data-cy="select-deliveryMechanisms[0].fsp"]'
    button_next_save = 'button[data-cy="button-next-save"]'
    button_send_for_approval = 'button[data-cy="button-send-for-approval"]'
    button_approve = 'button[data-cy="button-approve"]'
    button_authorize = 'button[data-cy="button-authorize"]'
    button_mark_as_released = 'button[data-cy="button-mark-as-released"]'
    button_upload_reconciliation_info = 'button[data-cy="button-import"]'
    button_import_submit = 'button[data-cy="button-import-submit"]'
    errors_container = 'div[data-cy="errors-container"]'
    delete_button = 'button[data-cy="button-delete-pp"]'
    upload_file_button = 'button[data-cy="upload-file-button"]'
    title_input = 'div[data-cy="title-input"]'

    def get_button_lock_plan(self) -> WebElement:
        return self.wait_for(self.button_lock_plan)

    def get_button_submit(self) -> WebElement:
        submit_button = self.wait_for(self.button_submit)
        self.element_clickable(self.button_submit)
        return submit_button

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_pp_unicef_id(self) -> WebElement:
        return self.wait_for(self.pp_unicef_id)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_button_export_xlsx(self) -> WebElement:
        return self.wait_for(self.button_export_xlsx)

    def get_button_download_xlsx(self) -> WebElement:
        return self.wait_for(self.button_download_xlsx)

    def get_button_upload_reconciliation_info(self) -> WebElement:
        return self.wait_for(self.button_upload_reconciliation_info)

    def get_errors_container(self) -> WebElement:
        return self.wait_for(self.errors_container)

    def get_button_import_submit(self) -> WebElement:
        return self.wait_for(self.button_import_submit)

    def get_delete_button(self) -> WebElement:
        return self.wait_for(self.delete_button)

    def get_upload_file_button(self) -> WebElement:
        return self.wait_for(self.upload_file_button)

    def get_title_input(self) -> WebElement:
        return self.wait_for(self.title_input)

    def get_label_created_by(self) -> WebElement:
        return self.wait_for(self.label_created_by)

    def get_label_target_population(self) -> WebElement:
        return self.wait_for(self.label_target_population)

    def get_label_currency(self) -> WebElement:
        return self.wait_for(self.label_currency)

    def get_label_start_date(self) -> WebElement:
        return self.wait_for(self.label_start_date)

    def get_label_end_date(self) -> WebElement:
        return self.wait_for(self.label_end_date)

    def get_label_dispersion_start_date(self) -> WebElement:
        return self.wait_for(self.label_dispersion_start_date)

    def get_label_dispersion_end_date(self) -> WebElement:
        return self.wait_for(self.label_dispersion_end_date)

    def get_label_related_follow_up_payment_plans(self) -> WebElement:
        return self.wait_for(self.label_related_follow_up_payment_plans)

    def get_button_create_exclusions(self) -> WebElement:
        return self.wait_for(self.button_create_exclusions)

    def get_button_save_exclusions(self) -> WebElement:
        return self.wait_for(self.button_save_exclusions)

    def get_input_households_ids(self) -> WebElement:
        return self.wait_for(self.input_households_ids)

    def get_input_beneficiaries_ids(self) -> WebElement:
        return self.wait_for(self.input_beneficiaries_ids)

    def get_input_exclusion_reason(self) -> WebElement:
        return self.wait_for(self.input_exclusion_reason)

    def get_button_apply_exclusions(self) -> WebElement:
        return self.wait_for(self.button_apply_exclusions)

    def get_label_female_children(self) -> WebElement:
        return self.wait_for(self.label_female_children)

    def get_label_female_adults(self) -> WebElement:
        return self.wait_for(self.label_female_adults)

    def get_label_male_children(self) -> WebElement:
        return self.wait_for(self.label_male_children)

    def get_label_male_adults(self) -> WebElement:
        return self.wait_for(self.label_male_adults)

    def get_chart_container(self) -> WebElement:
        return self.wait_for(self.chart_container)

    def get_label_total_number_of_households(self) -> WebElement:
        return self.wait_for(self.label_total_number_of_households)

    def get_label_total_number_of_people(self) -> WebElement:
        return self.wait_for(self.label_total_number_of_people)

    def get_label_targeted_individuals(self) -> WebElement:
        return self.wait_for(self.label_targeted_individuals)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_button_import(self) -> WebElement:
        return self.wait_for(self.button_import)

    def get_table_label(self) -> [WebElement]:
        return self.get_elements(self.table_label)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_label_delivered_fully(self) -> WebElement:
        return self.wait_for(self.label_delivered_fully)

    def get_label_delivered_partially(self) -> WebElement:
        return self.wait_for(self.label_delivered_partially)

    def get_label_not_delivered(self) -> WebElement:
        return self.wait_for(self.label_not_delivered)

    def get_label_unsuccessful(self) -> WebElement:
        return self.wait_for(self.label_unsuccessful)

    def get_label_pending(self) -> WebElement:
        return self.wait_for(self.label_pending)

    def get_label_number_of_payments(self) -> WebElement:
        return self.wait_for(self.label_number_of_payments)

    def get_label_reconciled(self) -> WebElement:
        return self.wait_for(self.label_reconciled)

    def get_label_total_entitled_quantity(self) -> WebElement:
        return self.wait_for(self.label_total_entitled_quantity)

    def get_input_entitlement_formula(self) -> WebElement:
        return self.wait_for(self.input_entitlement_formula)

    def get_button_apply_steficon(self) -> WebElement:
        return self.wait_for(self.button_apply_steficon)

    def get_select_delivery_mechanism(self) -> WebElement:
        return self.wait_for(self.select_delivery_mechanism)

    def get_select_delivery_mechanism_fsp(self) -> WebElement:
        return self.wait_for(self.select_delivery_mechanisms_fsp)

    def get_button_next_save(self) -> WebElement:
        return self.wait_for(self.button_next_save)

    def get_button_send_for_approval(self) -> WebElement:
        return self.wait_for(self.button_send_for_approval)

    def click_button(self, locator: str) -> None:
        self.wait_for(locator)
        self.element_clickable(locator)
        sleep(5)
        self.get(locator).click()

    def click_button_send_for_approval(self) -> None:
        self.click_button(self.button_send_for_approval)

    def get_button_approve(self) -> WebElement:
        return self.wait_for(self.button_approve)

    def click_button_approve(self) -> None:
        self.click_button(self.button_approve)

    def click_button_lock_plan(self) -> None:
        self.click_button(self.button_lock_plan)

    def get_button_authorize(self) -> WebElement:
        return self.wait_for(self.button_authorize)

    def click_button_authorize(self) -> None:
        self.click_button(self.button_authorize)

    def click_button_mark_as_released(self) -> None:
        self.click_button(self.button_mark_as_released)

    def click_button_export_xlsx(self) -> None:
        self.click_button(self.button_export_xlsx)

    def get_button_mark_as_released(self) -> WebElement:
        return self.wait_for(self.button_mark_as_released)

    def check_status(self, status: str) -> None:
        self.wait_for_text(status, self.status_container)

    def get_supporting_documents_title(self) -> WebElement:
        return self.wait_for(self.supporting_documents_title)

    def get_supporting_documents_empty(self) -> WebElement:
        return self.wait_for(self.supporting_documents_empty)
