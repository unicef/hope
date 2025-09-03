from typing import Union

from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class Individuals(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    ind_filters_search = 'div[data-cy="ind-filters-search"]'
    filter_document_type = 'div[data-cy="filters-document-type"]'
    ind_filters_gender = 'div[data-cy="ind-filters-gender"]'
    ind_filters_age_from = 'div[data-cy="ind-filters-age-from"]'
    ind_filters_age_to = 'div[data-cy="ind-filters-age-to"]'
    ind_filters_flags = 'div[data-cy="ind-filters-flags"]'
    ind_filters_order_by = 'div[data-cy="ind-filters-order-by"]'
    ind_filters_status = 'div[data-cy="ind-filters-status"]'
    date_picker_filter = 'div[data-cy="date-picker-filter"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    page_details_container = 'div[data-cy="page-details-container"]'
    table_title = 'h6[data-cy="table-title"]'
    sanction_list_possible_match = 'th[data-cy="sanction-list-possible-match"]'
    table_label = 'span[data-cy="table-label"]'
    individual_id = 'th[data-cy="individual-id"]'
    individual_name = 'th[data-cy="individual-name"]'
    household_id = 'th[data-cy="household-id"]'
    relationship = 'th[data-cy="relationship"]'
    individual_age = 'th[data-cy="individual-age"]'
    individual_sex = 'th[data-cy="individual-sex"]'
    individual_location = 'th[data-cy="individual-location"]'
    table_row = 'tr[data-cy="table-row"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    individual_table_row = 'tr[data-cy="individual-table-row"'

    # PDU
    tab_periodic_data_updates = 'button[data-cy="tab-periodic-data-updates"]'
    button_import = 'button[data-cy="button-import"]'
    dialog_import = 'div[data-cy="dialog-import"]'
    file_input = 'input[data-cy="file-input"]'
    close_button = 'button[data-cy="close-button"]'
    button_import_submit = 'button[data-cy="button-import-submit"]'
    update_status = 'td[data-cy="update-status-{}"]'
    template_status = 'td[data-cy="template-status-{}"]'
    template_action = 'td[data-cy="template-action-{}"]'
    update_details_btn = 'button[data-cy="update-details-btn-{}"]'
    download_btn = 'a[data-cy="download-btn-{}"]'
    export_btn = 'button[data-cy="export-btn-{}"]'
    pdu_updates = 'button[data-cy="pdu-updates"]'
    status_container = '[data-cy="status-container"]'
    pdu_form_errors = 'div[data-cy="pdu-form-errors"]'
    pdu_upload_error = 'div[data-cy="pdu-upload-error"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_ind_filters_search(self) -> WebElement:
        return self.wait_for(self.ind_filters_search)

    def get_filter_document_type(self) -> WebElement:
        return self.wait_for(self.filter_document_type)

    def get_ind_filters_gender(self) -> WebElement:
        return self.wait_for(self.ind_filters_gender)

    def get_ind_filters_age_from(self) -> WebElement:
        return self.wait_for(self.ind_filters_age_from)

    def get_ind_filters_age_to(self) -> WebElement:
        return self.wait_for(self.ind_filters_age_to)

    def get_ind_filters_flags(self) -> WebElement:
        return self.wait_for(self.ind_filters_flags)

    def get_ind_filters_order_by(self) -> WebElement:
        return self.wait_for(self.ind_filters_order_by)

    def get_ind_filters_status(self) -> WebElement:
        return self.wait_for(self.ind_filters_status)

    def get_date_picker_filter(self) -> WebElement:
        return self.wait_for(self.date_picker_filter)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_page_details_container(self) -> WebElement:
        return self.wait_for(self.page_details_container)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_sanction_list_possible_match(self) -> WebElement:
        return self.wait_for(self.sanction_list_possible_match)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_individual_id(self) -> WebElement:
        return self.wait_for(self.individual_id)

    def get_individual_name(self) -> WebElement:
        return self.wait_for(self.individual_name)

    def get_household_id(self) -> WebElement:
        return self.wait_for(self.household_id)

    def get_relationship(self) -> WebElement:
        return self.wait_for(self.relationship)

    def get_individual_age(self) -> WebElement:
        return self.wait_for(self.individual_age)

    def get_individual_sex(self) -> WebElement:
        return self.wait_for(self.individual_sex)

    def get_individual_location(self) -> WebElement:
        return self.wait_for(self.individual_location)

    def get_table_row(self) -> [WebElement]:
        return self.get_elements(self.table_row)

    def get_individual_table_row(self) -> [WebElement]:
        self.wait_for(self.individual_table_row)
        return self.get_elements(self.individual_table_row)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    # PDU
    def get_tab_periodic_data_updates(self) -> WebElement:
        return self.wait_for(self.tab_periodic_data_updates)

    def get_button_import(self) -> WebElement:
        return self.wait_for(self.button_import)

    def get_dialog_import(self) -> WebElement:
        return self.wait_for(self.dialog_import)

    def get_file_input(self) -> WebElement:
        return self.wait_for(self.file_input)

    def get_close_button(self) -> WebElement:
        return self.wait_for(self.close_button)

    def get_button_import_submit(self) -> WebElement:
        return self.wait_for(self.button_import_submit)

    def get_update_status(self, pk: Union[int, str]) -> WebElement:
        return self.wait_for(self.update_status.format(pk))

    def get_download_btn(self, pk: Union[int, str]) -> WebElement:
        return self.wait_for(self.download_btn.format(pk))

    def get_export_btn(self, pk: Union[int, str]) -> WebElement:
        return self.wait_for(self.export_btn.format(pk))

    def get_update_details_btn(self, pk: Union[int, str]) -> WebElement:
        return self.wait_for(self.update_details_btn.format(pk))

    def get_pdu_updates(self) -> WebElement:
        return self.wait_for(self.pdu_updates)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_pdu_form_errors(self) -> WebElement:
        return self.wait_for(self.pdu_form_errors)

    def get_pdu_upload_error(self) -> WebElement:
        return self.wait_for(self.pdu_upload_error)

    def get_template_status(self, pk: Union[int, str]) -> WebElement:
        return self.wait_for(self.template_status.format(pk))
