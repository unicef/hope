from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class ProgrammeDetails(BaseComponents):
    header_title = 'h5[data-cy="page-header-title"]'
    copy_program = 'a[data-cy="button-copy-program"]'
    program_status = 'div[data-cy="status-container"]'
    label_start_date = 'div[data-cy="label-START DATE"]'
    label_end_date = 'div[data-cy="label-END DATE"]'
    label_selector = 'div[data-cy="label-Sector"]'
    label_data_collecting_type = 'div[data-cy="label-Data Collecting Type"]'
    label_freq_of_payment = 'div[data-cy="label-Frequency of Payment"]'
    label_administrative_areas = 'div[data-cy="label-Administrative Areas of implementation"]'
    label_cash_plus = 'div[data-cy="label-CASH+"]'
    label_program_size = 'div[data-cy="label-Programme size"]'
    label_description = 'div[data-cy="label-Description"]'
    label_area_access = 'div[data-cy="label-Area Access"]'
    label_admin_area1 = 'div[data-cy="labelized-field-container-admin-area-1-total-count"]'
    label_admin_area2 = 'div[data-cy="label-Admin Area 2"]'
    label_partner_name = 'h6[data-cy="label-partner-name"]'
    label_partner_access = 'div[data-cy="label-Partner Access"]'
    button_remove_program = 'button[data-cy="button-remove-program"]'
    button_edit_program = 'button[data-cy="button-edit-program"]'
    select_edit_program_details = 'li[data-cy="menu-item-edit-details"]'
    select_edit_program_partners = 'li[data-cy="menu-item-edit-partners"]'
    button_activate_program = 'button[data-cy="button-activate-program"]'
    button_activate_program_modal = 'button[data-cy="button-activate-program-modal"]'
    label_programme_code = 'div[data-cy="label-Programme Code"]'
    button_finish_program = 'button[data-cy="button-finish-program"]'
    table_title = 'h6[data-cy="table-title"]'
    button_add_new_programme_cycle = 'button[data-cy="button-add-new-programme-cycle"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    program_cycle_row = 'tr[data-cy="program-cycle-row"]'
    program_cycle_id = 'td[data-cy="program-cycle-id"]'
    program_cycle_title = 'td[data-cy="program-cycle-title"]'
    program_cycle_status = 'td[data-cy="program-cycle-status"]'
    status_container = 'div[data-cy="status-container"]'
    program_cycle_total_entitled_quantity_usd = 'td[data-cy="program-cycle-total-entitled-quantity-usd"]'
    program_cycle_total_undelivered_quantity_usd = 'td[data-cy="program-cycle-total-undelivered-quantity-usd"]'
    program_cycle_total_delivered_quantity_usd = 'td[data-cy="program-cycle-total-delivered-quantity-usd"]'
    program_cycle_start_date = 'td[data-cy="program-cycle-start-date"]'
    program_cycle_end_date = 'td[data-cy="program-cycle-end-date"]'
    program_cycle_details_btn = 'td[data-cy="program-cycle-details-btn"]'
    button_edit_program_cycle = 'button[data-cy="button-edit-program-cycle"]'
    start_date_cycle = 'div[data-cy="start-date-cycle"]'
    data_picker_filter = 'div[data-cy="date-picker-filter"]'
    end_date_cycle = 'div[data-cy="end-date-cycle"]'
    button_next = 'button[data-cy="button-update-program-cycle-modal"]'
    button_save = 'button[data-cy="button-save"]'
    button_create_program_cycle = 'button[data-cy="button-create-program-cycle"]'
    input_title = 'input[data-cy="input-title"]'
    delete_programme_cycle = 'button[data-cy="delete-programme-cycle"]'
    button_delete = 'button[data-cy="button-delete"]'
    button_cancel = 'button[data-cy="button-cancel"]'

    def get_program_cycle_row(self) -> [WebElement]:
        self.wait_for(self.program_cycle_row)
        return self.get_elements(self.program_cycle_row)

    def get_delete_programme_cycle(self) -> [WebElement]:
        self.wait_for(self.delete_programme_cycle)
        return self.get_elements(self.delete_programme_cycle)

    def get_program_cycle_id(self) -> [WebElement]:
        self.wait_for(self.program_cycle_id)
        return self.get_elements(self.program_cycle_id)

    def get_program_cycle_title(self) -> [WebElement]:
        self.wait_for(self.program_cycle_title)
        return self.get_elements(self.program_cycle_title)

    def get_program_cycle_status(self) -> [WebElement]:
        self.wait_for(self.program_cycle_status)
        return self.get_elements(self.program_cycle_status)

    def get_status_container(self) -> [WebElement]:
        self.wait_for(self.status_container)
        return self.get_elements(self.status_container)

    def get_program_cycle_total_entitled_quantity_usd(self) -> [WebElement]:
        self.wait_for(self.program_cycle_total_entitled_quantity_usd)
        return self.get_elements(self.program_cycle_total_entitled_quantity_usd)

    def get_program_cycle_total_undelivered_quantity_usd(self) -> [WebElement]:
        self.wait_for(self.program_cycle_total_undelivered_quantity_usd)
        return self.get_elements(self.program_cycle_total_undelivered_quantity_usd)

    def get_program_cycle_total_delivered_quantity_usd(self) -> [WebElement]:
        self.wait_for(self.program_cycle_total_delivered_quantity_usd)
        return self.get_elements(self.program_cycle_total_delivered_quantity_usd)

    def get_program_cycle_start_date(self) -> [WebElement]:
        self.wait_for(self.program_cycle_start_date)
        return self.get_elements(self.program_cycle_start_date)

    def get_program_cycle_end_date(self) -> [WebElement]:
        self.wait_for(self.program_cycle_end_date)
        return self.get_elements(self.program_cycle_end_date)

    def get_program_cycle_details_btn(self) -> [WebElement]:
        self.wait_for(self.program_cycle_details_btn)
        return self.get_elements(self.program_cycle_details_btn)

    def get_button_edit_program_cycle(self) -> [WebElement]:
        self.wait_for(self.button_edit_program_cycle)
        return self.get_elements(self.button_edit_program_cycle)

    def get_data_picker_filter(self) -> WebElement:
        self.wait_for(self.data_picker_filter)
        return self.get_elements(self.data_picker_filter)[0].find_elements("tag name", "input")[0]

    def get_button_next(self) -> WebElement:
        return self.wait_for(self.button_next)

    def get_button_save(self) -> WebElement:
        return self.wait_for(self.button_save)

    def get_input_title(self) -> WebElement:
        return self.wait_for(self.input_title)

    def get_start_date_cycle(self) -> WebElement:
        return self.wait_for(self.start_date_cycle).find_elements("tag name", "input")[0]

    def get_end_date_cycle(self) -> WebElement:
        return self.wait_for(self.end_date_cycle).find_elements("tag name", "input")[0]

    def get_start_date_cycle_div(self) -> WebElement:
        return self.wait_for(self.start_date_cycle)

    def get_end_date_cycle_div(self) -> WebElement:
        return self.wait_for(self.end_date_cycle)

    def get_button_create_program_cycle(self) -> WebElement:
        return self.wait_for(self.button_create_program_cycle)

    def get_label_partner_name(self) -> WebElement:
        return self.wait_for(self.label_partner_name)

    def get_label_area_access(self) -> WebElement:
        return self.wait_for(self.label_area_access)

    def get_label_partner_access(self) -> WebElement:
        return self.wait_for(self.label_partner_access)

    def get_label_admin_area1(self) -> WebElement:
        return self.wait_for(self.label_admin_area1)

    def get_label_admin_area2(self) -> WebElement:
        return self.wait_for(self.label_admin_area2)

    def get_program_status(self) -> WebElement:
        return self.wait_for(self.program_status)

    def get_header_title(self) -> WebElement:
        return self.wait_for(self.header_title)

    def get_label_start_date(self) -> WebElement:
        return self.wait_for(self.label_start_date)

    def get_label_end_date(self) -> WebElement:
        return self.wait_for(self.label_end_date)

    def get_label_selector(self) -> WebElement:
        return self.wait_for(self.label_selector)

    def get_label_data_collecting_type(self) -> WebElement:
        return self.wait_for(self.label_data_collecting_type)

    def get_label_freq_of_payment(self) -> WebElement:
        return self.wait_for(self.label_freq_of_payment)

    def get_label_administrative_areas(self) -> WebElement:
        return self.wait_for(self.label_administrative_areas)

    def get_label_cash_plus(self) -> WebElement:
        return self.wait_for(self.label_cash_plus)

    def get_label_program_size(self) -> WebElement:
        return self.wait_for(self.label_program_size)

    def get_copy_program(self) -> WebElement:
        return self.wait_for(self.copy_program)

    def get_label_description(self) -> WebElement:
        return self.wait_for(self.label_description)

    def get_button_remove_program(self) -> WebElement:
        return self.wait_for(self.button_remove_program)

    def get_button_edit_program(self) -> WebElement:
        return self.wait_for(self.button_edit_program)

    def get_select_edit_program_details(self) -> WebElement:
        return self.wait_for(self.select_edit_program_details)

    def get_sselect_edit_program_partners(self) -> WebElement:
        return self.wait_for(self.select_edit_program_partners)

    def get_button_activate_program(self) -> WebElement:
        return self.wait_for(self.button_activate_program)

    def get_button_activate_program_modal(self) -> WebElement:
        return self.wait_for(self.button_activate_program_modal)

    def get_label_programme_code(self) -> WebElement:
        return self.wait_for(self.label_programme_code)

    def get_button_finish_program(self) -> WebElement:
        return self.wait_for(self.button_finish_program)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_button_add_new_programme_cycle(self) -> WebElement:
        return self.wait_for(self.button_add_new_programme_cycle)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_button_delete(self) -> WebElement:
        return self.wait_for(self.button_delete)

    def get_button_cancel(self) -> WebElement:
        return self.wait_for(self.button_cancel)

    def click_button_finish_program_popup(self) -> None:
        self.wait_for('[data-cy="dialog-actions-container"]')
        self.get_elements(self.button_finish_program)[1].click()
        self.wait_for_disappear('[data-cy="dialog-actions-container"]')
