from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class TargetingDetails(BaseComponents):
    # Locators
    title_page = 'h5[data-cy="page-header-title"]'
    status = 'div[data-cy="target-population-status"]'
    criteria_container = 'div[data-cy="criteria-container"]'
    lock_button = 'button[data-cy="button-target-population-lock"]'
    lock_popup_button = 'button[data-cy="button-target-population-modal-lock"]'
    household_table_cell = "table tr:nth-of-type({}) td:nth-of-type({})"
    household_table_rows = '[data-cy="target-population-household-row"]'
    people_table_rows = '[data-cy="target-population-people-row"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_target_population_duplicate = 'button[data-cy="button-target-population-duplicate"]'
    input_name = 'input[data-cy="input-name"]'
    button_delete = 'button[data-cy="button-delete"]'
    button_edit = 'a[data-cy="button-edit"]'
    button_save = 'button[data-cy="button-save"]'
    button_icon_edit = 'button[data-cy="button-edit"]'
    button_rebuild = 'button[data-cy="button-rebuild"]'
    button_target_population_lock = 'button[data-cy="button-target-population-lock"]'
    details_title = 'div[data-cy="details-title"]'
    details_grid = 'div[data-cy="details-grid"]'
    label_status = 'div[data-cy="label-Status"]'
    button_mark_ready = 'button[data-cy="button-target-population-send-to-hope"]'
    button_popup_mark_ready = 'button[data-cy="button-target-population-modal-send-to-hope"]'
    target_population_status = 'div[data-cy="target-population-status"]'
    labelized_field_container_created_by = 'div[data-cy="labelized-field-container-created-by"]'
    label_created_by = 'div[data-cy="label-created by"]'
    labelized_field_container_close_date = 'div[data-cy="labelized-field-container-close-date"]'
    label_programme_population_close_date = 'div[data-cy="label-Programme population close date"]'
    labelized_field_container_program_name = 'div[data-cy="labelized-field-container-program-name"]'
    label_programme = 'div[data-cy="label-Programme"]'
    labelized_field_container_send_by = 'div[data-cy="labelized-field-container-send-by"]'
    label_send_by = 'div[data-cy="label-Send by"]'
    labelized_field_container_send_date = 'div[data-cy="labelized-field-container-send-date"]'
    label_send_date = 'div[data-cy="label-Send date"]'
    checkbox_exclude_if_active_adjudication_ticket = 'span[data-cy="checkbox-exclude-if-active-adjudication-ticket"]'
    checkbox_exclude_people_if_active_adjudication_ticket = (
        'span[data-cy="checkbox-exclude-people-if-active-adjudication-ticket"]'
    )
    checkbox_exclude_if_on_sanction_list = 'span[data-cy="checkbox-exclude-if-on-sanction-list"]'
    icon_selected = '[data-testid="CheckBoxIcon"]'
    label_female_children = 'div[data-cy="label-Female Children"]'
    label_female_adults = 'div[data-cy="label-Female Adults"]'
    label_male_children = 'div[data-cy="label-Male Children"]'
    label_male_adults = 'div[data-cy="label-Male Adults"]'
    label_total_number_of_households = 'div[data-cy="label-Total Number of Items Groups"]'
    label_targeted_individuals = 'div[data-cy="label-Targeted Items"]'
    table_title = 'h6[data-cy="table-title"]'
    table_label = 'span[data-cy="table-label"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    status_container = 'div[data-cy="status-container"]'
    household_size_from = 'input[data-cy="input-householdsFiltersBlocks[0].value.from"]'
    household_size_to = 'input[data-cy="input-householdsFiltersBlocks[0].value.to"]'
    dialog_box = 'div[role="dialog"]'
    button_target_population_add_criteria = 'div[data-cy="button-target-population-add-criteria"]'

    # Texts
    # Elements

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def wait_for_text_title_page(self, text: str) -> bool:
        return self.wait_for_text(text, self.title_page)

    def get_button_target_population_duplicate(self) -> WebElement:
        return self.wait_for(self.button_target_population_duplicate)

    def get_input_name(self) -> WebElement:
        return self.wait_for(self.input_name)

    def disappear_input_name(self) -> WebElement:
        return self.wait_for_disappear(self.input_name)

    def get_button_delete(self) -> WebElement:
        return self.wait_for(self.button_delete)

    def get_button_edit(self) -> WebElement:
        return self.wait_for(self.button_edit)

    def get_button_save(self) -> WebElement:
        return self.wait_for(self.button_save)

    def get_button_icon_edit(self) -> WebElement:
        return self.wait_for(self.button_icon_edit)

    def get_button_rebuild(self) -> WebElement:
        return self.wait_for(self.button_rebuild)

    def get_button_target_population_lock(self) -> WebElement:
        return self.wait_for(self.button_target_population_lock)

    def get_details_title(self) -> WebElement:
        return self.wait_for(self.details_title)

    def get_details_grid(self) -> WebElement:
        return self.wait_for(self.details_grid)

    def get_label_status(self) -> WebElement:
        return self.wait_for(self.label_status)

    def wait_for_label_status(self, status: str) -> WebElement:
        for _ in range(20):
            sleep(1)
            if status.upper() in self.get_label_status().text:
                return self.wait_for(self.label_status)
        raise Exception(f"Status: {status.capitalize()} does not occur.")

    def get_target_population_status(self) -> WebElement:
        return self.wait_for(self.target_population_status)

    def get_button_mark_ready(self) -> WebElement:
        return self.wait_for(self.button_mark_ready)

    def get_button_popup_mark_ready(self) -> WebElement:
        return self.wait_for(self.button_popup_mark_ready)

    def get_labelized_field_container_created_by(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_created_by)

    def get_label_created_by(self) -> WebElement:
        return self.wait_for(self.label_created_by)

    def get_labelized_field_container_close_date(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_close_date)

    def get_label_programme_population_close_date(self) -> WebElement:
        return self.wait_for(self.label_programme_population_close_date)

    def get_labelized_field_container_program_name(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_program_name)

    def get_label_programme(self) -> WebElement:
        return self.wait_for(self.label_programme)

    def get_labelized_field_container_send_by(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_send_by)

    def get_label_send_by(self) -> WebElement:
        return self.wait_for(self.label_send_by)

    def get_labelized_field_container_send_date(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_send_date)

    def get_label_send_date(self) -> WebElement:
        return self.wait_for(self.label_send_date)

    def get_criteria_container(self) -> WebElement:
        return self.wait_for(self.criteria_container)

    def get_checkbox_exclude_if_active_adjudication_ticket(self) -> WebElement:
        return self.get(self.checkbox_exclude_if_active_adjudication_ticket)

    def get_checkbox_exclude_people_if_active_adjudication_ticket(self) -> WebElement:
        return self.get(self.checkbox_exclude_people_if_active_adjudication_ticket)

    def get_checkbox_exclude_if_on_sanction_list(self) -> WebElement:
        return self.wait_for(self.checkbox_exclude_if_on_sanction_list)

    def get_icon_selected(self) -> WebElement:
        return self.wait_for(self.icon_selected)

    def get_label_female_children(self) -> WebElement:
        return self.wait_for(self.label_female_children)

    def get_label_female_adults(self) -> WebElement:
        return self.wait_for(self.label_female_adults)

    def get_label_male_children(self) -> WebElement:
        return self.wait_for(self.label_male_children)

    def get_label_male_adults(self) -> WebElement:
        return self.wait_for(self.label_male_adults)

    def get_label_total_number_of_households(self) -> WebElement:
        return self.wait_for(self.label_total_number_of_households)

    def get_label_targeted_individuals(self) -> WebElement:
        return self.wait_for(self.label_targeted_individuals)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_table_label(self) -> [WebElement]:
        return self.get_elements(self.table_label)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_title_page(self) -> WebElement:
        return self.wait_for(self.title_page)

    def get_status(self) -> WebElement:
        return self.wait_for(self.status)

    def get_lock_button(self) -> WebElement:
        return self.wait_for(self.lock_button)

    def get_lock_popup_button(self) -> WebElement:
        return self.wait_for(self.lock_popup_button)

    def get_household_table_cell(self, row: int, column: int) -> WebElement:
        return self.wait_for(self.household_table_cell.format(row, column))

    def get_people_table_rows(self) -> list[WebElement]:
        return self.get_elements(self.people_table_rows)

    def get_household_table_rows(self) -> list[WebElement]:
        return self.get_elements(self.household_table_rows)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def disappear_status_container(self) -> bool:
        return self.wait_for_disappear(self.status_container)

    def get_household_size_from(self) -> WebElement:
        return self.wait_for(self.household_size_from)

    def get_household_size_to(self) -> WebElement:
        return self.wait_for(self.household_size_to)

    def get_dialog_box(self) -> WebElement:
        return self.wait_for(self.dialog_box)

    def get_button_target_population_add_criteria(self) -> WebElement:
        return self.wait_for(self.button_target_population_add_criteria)
