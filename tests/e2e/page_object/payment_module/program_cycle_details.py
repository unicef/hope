from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class ProgramCycleDetailsPage(BaseComponents):
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_create_payment_plan = 'a[data-cy="button-create-payment-plan"]'
    button_finish_programme_cycle = 'button[data-cy="button-finish-programme-cycle"]'
    button_reactivate_programme_cycle = 'button[data-cy="button-reactivate-programme-cycle"]'
    status_container = 'div[data-cy="status-container"]'
    label_created_by = 'div[data-cy="label-Created By"]'
    label_start_date = 'div[data-cy="label-Start Date"]'
    label_end_date = 'div[data-cy="label-End Date"]'
    label_programme_start_date = 'div[data-cy="label-Programme Start Date"]'
    label_programme_end_date = 'div[data-cy="label-Programme End Date"]'
    label_frequency_of_payment = 'div[data-cy="label-Frequency of Payment"]'
    select_filter = 'div[data-cy="select-filter"]'
    date_picker_filter_from = 'div[data-cy="date-picker-filter-From"]'
    date_picker_filter_to = 'div[data-cy="date-picker-filter-To"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    table_label = 'span[data-cy="table-label"]'
    table_row = 'tr[data-cy="table-row"]'
    table_pagination = 'div[data-cy="table-pagination"]'

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_create_payment_plan(self) -> WebElement:
        return self.wait_for(self.button_create_payment_plan)

    def get_button_finish_programme_cycle(self) -> WebElement:
        return self.wait_for(self.button_finish_programme_cycle)

    def get_button_reactivate_programme_cycle(self) -> WebElement:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        from time import sleep

        sleep(2)
        return self.wait_for(self.button_reactivate_programme_cycle)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_label_created_by(self) -> WebElement:
        return self.wait_for(self.label_created_by)

    def get_label_start_date(self) -> WebElement:
        return self.wait_for(self.label_start_date)

    def get_label_end_date(self) -> WebElement:
        return self.wait_for(self.label_end_date)

    def get_label_programme_start_date(self) -> WebElement:
        return self.wait_for(self.label_programme_start_date)

    def get_label_programme_end_date(self) -> WebElement:
        return self.wait_for(self.label_programme_end_date)

    def get_label_frequency_of_payment(self) -> WebElement:
        return self.wait_for(self.label_frequency_of_payment)

    def get_select_filter(self) -> WebElement:
        return self.wait_for(self.select_filter)

    def get_date_picker_filter_from(self) -> WebElement:
        return self.wait_for(self.date_picker_filter_from)

    def get_date_picker_filter_to(self) -> WebElement:
        return self.wait_for(self.date_picker_filter_to)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)
