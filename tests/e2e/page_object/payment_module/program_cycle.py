from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ProgramCyclePage(BaseComponents):
    main_content = 'div[data-cy="main-content"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    select_filter = 'div[data-cy="select-filter"]'
    date_picker_filter = 'div[data-cy="date-picker-filter-"]'
    date_picker_filter_from = 'div[data-cy="date-picker-filter-"]'
    date_picker_filter_to = 'div[data-cy="date-picker-filter-"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    table_title = 'h6[data-cy="table-title"]'
    head_cell_id = 'th[data-cy="head-cell-id"]'
    table_label = 'span[data-cy="table-label"]'
    head_cell_programme_cycles_title = 'th[data-cy="head-cell-programme-cycles-title"]'
    head_cell_status = 'th[data-cy="head-cell-status"]'
    head_cell_total_entitled_quantity = 'th[data-cy="head-cell-total-entitled-quantity"]'
    head_cell_total_entitled_quantity_usd = 'th[data-cy="head-cell-total-entitled-quantity-usd"]'
    head_cell_start_date = 'th[data-cy="head-cell-start-date"]'
    head_cell_end_date = 'th[data-cy="head-cell-end-date"]'
    head_cell_empty = 'th[data-cy="head-cell-empty"]'
    program_cycle_row = 'tr[data-cy="program-cycle-row"]'
    program_cycle_id = 'td[data-cy="program-cycle-id"]'
    program_cycle_title = 'td[data-cy="program-cycle-title"]'
    program_cycle_status = 'td[data-cy="program-cycle-status"]'
    program_cycle_total_entitled_quantity_usd = 'td[data-cy="program-cycle-total-entitled-quantity-usd"]'
    program_cycle_start_date = 'td[data-cy="program-cycle-start-date"]'
    program_cycle_end_date = 'td[data-cy="program-cycle-end-date"]'
    program_cycle_details_btn = 'td[data-cy="program-cycle-details-btn"]'
    table_pagination = 'div[data-cy="table-pagination"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_select_filter(self) -> WebElement:
        return self.wait_for(self.select_filter)

    def get_date_picker_filter(self) -> WebElement:
        return self.wait_for(self.date_picker_filter)

    def get_date_picker_filter_from(self) -> WebElement:
        return self.wait_for(self.date_picker_filter_from)

    def get_date_picker_filter_to(self) -> WebElement:
        return self.wait_for(self.date_picker_filter_to)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_head_cell_id(self) -> WebElement:
        return self.wait_for(self.head_cell_id)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_head_cell_programme_cycles_title(self) -> WebElement:
        return self.wait_for(self.head_cell_programme_cycles_title)

    def get_head_cell_status(self) -> WebElement:
        return self.wait_for(self.head_cell_status)

    def get_head_cell_total_entitled_quantity_usd(self) -> WebElement:
        return self.wait_for(self.head_cell_total_entitled_quantity_usd)

    def get_head_cell_start_date(self) -> WebElement:
        return self.wait_for(self.head_cell_start_date)

    def get_head_cell_end_date(self) -> WebElement:
        return self.wait_for(self.head_cell_end_date)

    def get_head_cell_empty(self) -> WebElement:
        return self.wait_for(self.head_cell_empty)

    def get_program_cycle_row(self) -> [WebElement]:
        self.wait_for(self.program_cycle_row)
        return self.get_elements(self.program_cycle_row)

    def get_program_cycle_status(self) -> WebElement:
        return self.wait_for(self.program_cycle_status)

    def get_program_cycle_total_entitled_quantity_usd(self) -> WebElement:
        return self.wait_for(self.program_cycle_total_entitled_quantity_usd)

    def get_program_cycle_start_date(self) -> WebElement:
        return self.wait_for(self.program_cycle_start_date)

    def get_program_cycle_end_date(self) -> WebElement:
        return self.wait_for(self.program_cycle_end_date)

    def get_program_cycle_start_date_list(self) -> [WebElement]:
        self.wait_for(self.program_cycle_start_date)
        return self.get_elements(self.program_cycle_start_date)

    def get_program_cycle_end_date_list(self) -> [WebElement]:
        self.wait_for(self.program_cycle_end_date)
        return self.get_elements(self.program_cycle_end_date)

    def get_program_cycle_details_btn(self) -> WebElement:
        return self.wait_for(self.program_cycle_details_btn)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_table_program_cycle_title(self) -> [WebElement]:
        return self.get_elements(self.program_cycle_title)

    def get_program_cycle_id(self) -> WebElement:
        return self.wait_for(self.program_cycle_id)
