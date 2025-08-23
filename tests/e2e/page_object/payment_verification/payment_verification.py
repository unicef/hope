from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentVerification(BaseComponents):
    # Locators
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    filter_search = 'div[data-cy="filter-search"]'
    select_filter = 'div[data-cy="select-filter"]'
    filter_status = 'div[data-cy="filter-status"]'
    filter_fsp = 'div[data-cy="filter-fsp"]'
    filter_modality = 'div[data-cy="filter-Modality"]'
    filter_start_date = 'div[data-cy="filter-start-date"]'
    filter_end_date = 'div[data-cy="filter-end-date"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    table_title = 'h6[data-cy="table-title"]'
    unicef_id = 'th[data-cy="unicefId"]'
    table_label = 'span[data-cy="table-label"]'
    verification_status = 'th[data-cy="verificationStatus"]'
    total_delivered_quantity = 'th[data-cy="totalDeliveredQuantity"]'
    start_date = 'th[data-cy="startDate"]'
    cycle_title_header = 'th[data-cy="cycleTitle"]'
    cycle_title = 'td[data-cy="cycle-title"]'
    updated_at = 'th[data-cy="updatedAt"]'
    cash_plan_table_row = 'tr[data-cy="cash-plan-table-row"]'
    status_container = 'div[data-cy="status-container"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    button_new_plan = 'button[data-cy="button-new-plan"]'
    tab_full_list = 'button[data-cy="tab-full-list"]'
    tab_random_sampling = 'button[data-cy="tab-random-sampling"]'
    select_excluded_admin_areas_full = 'div[data-cy="select-excludedAdminAreasFull"]'
    checkbox_verification_channel = 'div[data-cy="checkbox-verification-channel"]'
    slider_confidence_interval = 'span[data-cy="slider-confidence-interval"]'
    slider_margin_of_error = 'span[data-cy="slider-margin-of-error"]'
    input_admin_checkbox = 'span[data-cy="input-adminCheckbox"]'
    input_age_checkbox = 'span[data-cy="input-ageCheckbox"]'
    input_sex_checkbox = 'span[data-cy="input-sexCheckbox"]'
    dialog_actions_container = 'div[data-cy="dialog-actions-container"]'
    button_cancel = 'button[data-cy="button-cancel"]'
    button_submit = 'button[data-cy="button-submit"]'
    radio_rapidpro = 'span[data-cy="radio-rapidpro"]'
    radio_xlsx = 'span[data-cy="radio-xlsx"]'
    radio_manual = 'span[data-cy="radio-manual"]'
    radio_verification_channel = 'span[data-cy="radio-{}"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_filter_search(self) -> WebElement:
        return self.wait_for(self.filter_search)

    def get_select_filter(self) -> WebElement:
        return self.wait_for(self.select_filter)

    def get_filter_status(self) -> WebElement:
        return self.wait_for(self.filter_status)

    def get_filter_fsp(self) -> WebElement:
        return self.wait_for(self.filter_fsp)

    def get_filter_modality(self) -> WebElement:
        return self.wait_for(self.filter_modality)

    def get_filter_start_date(self) -> WebElement:
        return self.wait_for(self.filter_start_date)

    def get_filter_end_date(self) -> WebElement:
        return self.wait_for(self.filter_end_date)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_unicef_id(self) -> WebElement:
        return self.wait_for(self.unicef_id)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_verification_status(self) -> WebElement:
        return self.wait_for(self.verification_status)

    def get_total_delivered_quantity(self) -> WebElement:
        return self.wait_for(self.total_delivered_quantity)

    def get_start_date(self) -> WebElement:
        return self.wait_for(self.start_date)

    def get_cycle_title_header(self) -> WebElement:
        return self.wait_for(self.cycle_title_header)

    def get_cycle_title(self) -> WebElement:
        return self.wait_for(self.cycle_title)

    def get_updated_at(self) -> WebElement:
        return self.wait_for(self.updated_at)

    def get_cash_plan_table_row(self) -> WebElement:
        return self.wait_for(self.cash_plan_table_row)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_button_new_plan(self) -> WebElement:
        return self.wait_for(self.button_new_plan)

    def get_tab_full_list(self) -> WebElement:
        return self.wait_for(self.tab_full_list)

    def get_tab_random_sampling(self) -> WebElement:
        return self.wait_for(self.tab_random_sampling)

    def get_select_excluded_admin_areas_full(self) -> WebElement:
        return self.wait_for(self.select_excluded_admin_areas_full)

    def get_checkbox_verification_channel(self) -> WebElement:
        return self.wait_for(self.checkbox_verification_channel)

    def get_radio_rapidpro(self) -> WebElement:
        return self.wait_for(self.radio_rapidpro)

    def get_radio_xlsx(self) -> WebElement:
        return self.wait_for(self.radio_xlsx)

    def get_radio_manual(self) -> WebElement:
        return self.wait_for(self.radio_manual)

    def get_radio_verification_channel(self, name: str) -> WebElement:
        return self.wait_for(self.radio_verification_channel.format(name))

    def get_slider_confidence_interval(self) -> WebElement:
        return self.wait_for(self.slider_confidence_interval)

    def get_slider_margin_of_error(self) -> WebElement:
        return self.wait_for(self.slider_margin_of_error)

    def get_input_admin_checkbox(self) -> WebElement:
        return self.wait_for(self.input_admin_checkbox)

    def get_input_age_checkbox(self) -> WebElement:
        return self.wait_for(self.input_age_checkbox)

    def get_input_sex_checkbox(self) -> WebElement:
        return self.wait_for(self.input_sex_checkbox)

    def get_dialog_actions_container(self) -> WebElement:
        return self.wait_for(self.dialog_actions_container)

    def get_button_cancel(self) -> WebElement:
        return self.wait_for(self.button_cancel)

    def get_button_submit(self) -> WebElement:
        return self.wait_for(self.button_submit)
