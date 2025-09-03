from time import sleep

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class GrievanceTickets(BaseComponents):
    # Locators
    title_page = 'h5[data-cy="page-header-title"]'
    search_filter = 'div[data-cy="filters-search"]'
    document_type_filter = 'div[data-cy="filters-document-type"]'
    ticket_id = 'li[data-value="ticket_id"]'
    household_id = 'li[data-value="ticket_hh_id"]'
    family_name = 'li[data-value="full_name"]'
    tab_system_generated = 'button[data-cy="tab-SYSTEM-GENERATED"]'
    tab_user_generated = 'button[data-cy="tab-USER-GENERATED"]'
    button_close_ticket = 'button[data-cy="button-close-ticket"]'
    button_confirm = 'button[data-cy="button-confirm"]'
    creation_date_from_filter = 'div[data-cy="filters-creation-date-from"]'
    creation_date_to_filter = 'div[data-cy="filters-creation-date-to"]'
    status_filter = 'div[data-cy="filters-status"]'
    fsp_filter = 'div[data-cy="filters-fsp"]'
    category_filter = 'div[data-cy="filters-category"]'
    assignee_filter = 'div[data-cy="filters-assignee"]'
    admin_level_filter = 'div[data-cy="filters-admin-level-2"]'
    registration_data_import_filter = 'div[data-cy="filters-registration-data-import"]'
    preferred_language_filter = 'div[data-cy="filters-preferred-language"]'
    priority_filter = 'div[data-cy="filters-priority'
    urgency_filter = 'div[data-cy="filters-urgency'
    active_tickets_filter = 'div[data-cy="filters-active-tickets'
    similarity_score_from_filter = 'div[data-cy="filters-similarity-score-from'
    similarity_score_to_filter = 'div[data-cy="filters-similarity-score-to'
    button_apply = 'button[data-cy="button-filters-apply"]'
    button_clear = 'button[data-cy="button-filters-clear"]'
    button_new_ticket = 'a[data-cy="button-new-ticket"]'
    tab_title = 'h6[data-cy="table-title"]'
    tab_ticket_id = 'th[data-cy="ticket-id"]'
    tab_status = 'th[data-cy="status"]'
    tab_assigned_to = 'th[data-cy="assignedTo"]'
    tab_category = 'th[data-cy="category"]'
    tab_issue_type = 'th[data-cy="issueType"]'
    tab_household_id = 'th[data-cy="householdId"]'
    tab_priority = 'th[data-cy="priority"]'
    tab_urgency = 'th[data-cy="urgency"]'
    tab_linked_tickets = 'th[data-cy="linkedTickets"]'
    tab_creation_data = 'th[data-cy="createdAt"]'
    tab_last_modified_date = 'th[data-cy="userModified"]'
    tab_total_days = 'th[data-cy="totalDays"]'
    ticket_list_row = 'tr[role="checkbox"]'
    status_options = 'li[role="option"]'
    filters_created_by = 'div[data-cy="filters-created-by-input"]'
    select_all = 'span[data-cy="checkbox-select-all"]'
    table_label = 'span[data-cy="table-label"]'
    button_assign = 'button[data-cy="button-Assign"]'
    button_set_priority = 'button[data-cy="button-Set priority"]'
    button_set_urgency = 'button[data-cy="button-Set Urgency"]'
    button_add_note = 'button[data-cy="button-add note"]'
    selected_tickets = 'span[data-cy="selected-tickets"]'
    button_cancel = 'button[data-cy="button-cancel"]'
    button_save = 'button[data-cy="button-save"]'
    dropdown = 'tbody[data-cy="dropdown"]'
    status_container = '[data-cy="status-container"]'
    date_title_filter_popup = 'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]'
    days_filter_popup = (
        'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]'
    )

    # Texts
    text_title = "Grievance Tickets"
    text_tab_title = "Grievance Tickets List"

    # Elements
    def get_dropdown(self) -> WebElement:
        return self.wait_for(self.dropdown)

    def get_status_container(self) -> [WebElement]:
        self.wait_for(self.status_container)
        return self.get_elements(self.status_container)

    def get_button_cancel(self) -> WebElement:
        return self.wait_for(self.button_cancel)

    def get_button_save(self) -> WebElement:
        return self.wait_for(self.button_save)

    def get_selected_tickets(self) -> WebElement:
        return self.wait_for(self.selected_tickets)

    def get_grievance_title(self) -> WebElement:
        return self.wait_for(self.title_page)

    def get_tab_title(self) -> WebElement:
        return self.wait_for(self.tab_title)

    def get_search_filter(self) -> WebElement:
        return self.wait_for(self.search_filter)

    def get_ticket_type_filter(self) -> WebElement:
        return self.wait_for(self.document_type_filter)

    def get_creation_date_from_filter(self) -> WebElement:
        return self.wait_for(self.creation_date_from_filter)

    def get_creation_date_to_filter(self) -> WebElement:
        return self.wait_for(self.creation_date_to_filter)

    def get_status_filter(self) -> WebElement:
        return self.wait_for(self.status_filter)

    def get_fsp_filter(self) -> WebElement:
        return self.wait_for(self.fsp_filter)

    def get_category_filter(self) -> WebElement:
        return self.wait_for(self.category_filter)

    def get_assignee_filter(self) -> WebElement:
        return self.wait_for(self.assignee_filter)

    def get_admin_level_filter(self) -> WebElement:
        return self.wait_for(self.admin_level_filter)

    def get_registration_data_import_filter(self) -> WebElement:
        return self.wait_for(self.registration_data_import_filter)

    def get_preferred_language_filter(self) -> WebElement:
        return self.wait_for(self.preferred_language_filter)

    def get_priority_filter(self) -> WebElement:
        return self.wait_for(self.priority_filter)

    def get_urgency_filter(self) -> WebElement:
        return self.wait_for(self.urgency_filter)

    def get_active_tickets_filter(self) -> WebElement:
        return self.wait_for(self.active_tickets_filter)

    def get_filters_created_by(self) -> WebElement:
        return self.wait_for(self.filters_created_by)

    def get_similarity_score_from_filter(self) -> WebElement:
        return self.wait_for(self.similarity_score_from_filter)

    def get_similarity_score_to_filter(self) -> WebElement:
        return self.wait_for(self.similarity_score_to_filter)

    def get_button_apply(self) -> WebElement:
        return self.wait_for(self.button_apply)

    def get_button_clear(self) -> WebElement:
        return self.wait_for(self.button_clear)

    def get_button_new_ticket(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.get(self.button_new_ticket)

    def get_ticket_id(self) -> WebElement:
        return self.wait_for(self.ticket_id)

    def get_household_id(self) -> WebElement:
        return self.wait_for(self.household_id)

    def get_family_name(self) -> WebElement:
        return self.wait_for(self.family_name)

    def get_tab_ticket_id(self) -> WebElement:
        return self.wait_for(self.tab_ticket_id)

    def get_tab_status(self) -> WebElement:
        return self.wait_for(self.tab_status)

    def get_tab_assigned_to(self) -> WebElement:
        return self.wait_for(self.tab_assigned_to)

    def get_tab_category(self) -> WebElement:
        return self.wait_for(self.tab_category)

    def get_tab_issue_type(self) -> WebElement:
        return self.wait_for(self.tab_issue_type)

    def get_tab_household_id(self) -> WebElement:
        return self.wait_for(self.tab_household_id)

    def get_tab_priority(self) -> WebElement:
        return self.wait_for(self.tab_priority)

    def get_tab_urgency(self) -> WebElement:
        return self.wait_for(self.tab_urgency)

    def get_tab_linked_tickets(self) -> WebElement:
        return self.wait_for(self.tab_linked_tickets)

    def get_tab_creation_data(self) -> WebElement:
        return self.wait_for(self.tab_creation_data)

    def get_tab_last_modified_date(self) -> WebElement:
        return self.wait_for(self.tab_last_modified_date)

    def get_tab_total_days(self) -> WebElement:
        return self.wait_for(self.tab_total_days)

    def get_tab_system_generated(self) -> WebElement:
        return self.wait_for(self.tab_system_generated)

    def get_tab_user_generated(self) -> WebElement:
        return self.wait_for(self.tab_user_generated)

    def get_ticket_list_row(self) -> [WebElement]:
        self.wait_for(self.ticket_list_row)
        return self.get_elements(self.ticket_list_row)

    def get_table_label(self) -> [WebElement]:
        return self.get_elements(self.table_label)

    def get_date_title_filter_popup(self) -> WebElement:
        return self.wait_for(self.date_title_filter_popup)

    def get_days_filter_popup(self) -> WebElement:
        return self.wait_for(self.days_filter_popup)

    def get_options(self) -> WebElement:
        return self.wait_for(self.status_options)

    def get_select_all(self) -> WebElement:
        return self.wait_for(self.select_all)

    def get_button_assign(self) -> WebElement:
        return self.wait_for(self.button_assign)

    def get_button_set_priority(self) -> WebElement:
        return self.wait_for(self.button_set_priority)

    def get_button_set_urgency(self) -> WebElement:
        return self.wait_for(self.button_set_urgency)

    def get_button_add_note(self) -> WebElement:
        return self.wait_for(self.button_add_note)

    def get_button_close_ticket(self) -> WebElement:
        return self.wait_for(self.button_close_ticket)

    def get_button_confirm(self) -> WebElement:
        return self.wait_for(self.button_confirm)

    def check_if_text_exist_in_a_row(self, row_index: int, text: str, max_attempts: int = 5) -> None:
        attempt = 0
        exception = None
        while attempt < max_attempts:
            try:
                self.wait_for_rows()
                self.wait_for_row_with_text(row_index, text)
                return
            except StaleElementReferenceException as e:
                attempt += 1
                exception = e
        raise exception
