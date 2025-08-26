from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class Feedback(BaseComponents):
    # Locators
    title_page = 'h5[data-cy="page-header-title"]'
    button_submit_new_feedback = 'a[data-cy="button-submit-new-feedback"]'
    filter_search = 'div[data-cy="filters-search"]'
    filter_issue_type = 'div[data-cy="filters-issue-type"]'
    filter_created_by = 'div[data-cy="Created by-input"]'
    filter_creation_date_from = 'div[data-cy="filters-creation-date-from"]'
    filter_creation_date_to = 'div[data-cy="filters-creation-date-to"]'
    button_clear = 'button[data-cy="button-filters-clear"]'
    button_apply = 'button[data-cy="button-filters-apply"]'
    table_title = 'h6[data-cy="table-title"]'
    table_columns = 'span[data-cy="table-label"]'
    table_row = 'tr[role="checkbox"]'
    search_filter = 'div[data-cy="filters-search"]'
    days_filter_popup = (
        'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]'
    )
    creation_date_to_filter = 'div[data-cy="filters-creation-date-to"]'
    date_title_filter_popup = 'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]'
    issue_type_filter = 'div[data-cy="filters-issue-type"]'
    option = 'li[role="option"]'
    table_row_loading = 'tr[data-cy="table-row"]'

    # Texts
    text_title = "Feedback"
    text_table_title = "Feedbacks List"
    text_feedback_id = "Feedback ID"
    text_issue_type = "Issue Type"
    text_household_id = "Group ID"
    text_linked_grievance = "Linked Grievance"
    text_created_by = "Created by"
    text_creation_date = "Creation Date"

    # Elements
    def get_title_page(self) -> WebElement:
        return self.wait_for(self.title_page)

    def get_button_submit_new_feedback(self) -> WebElement:
        return self.wait_for(self.button_submit_new_feedback)

    def get_filter_search(self) -> WebElement:
        return self.wait_for(self.filter_search)

    def get_filter_issue_type(self) -> WebElement:
        return self.wait_for(self.filter_issue_type)

    def get_filter_created_by(self) -> WebElement:
        return self.wait_for(self.filter_created_by)

    def get_filter_creation_date_from(self) -> WebElement:
        return self.get_elements(self.filter_creation_date_from)

    def get_filter_creation_date_to(self) -> WebElement:
        return self.get_elements(self.filter_creation_date_to)

    def get_button_clear(self) -> WebElement:
        return self.wait_for(self.button_clear)

    def get_button_apply(self) -> WebElement:
        return self.wait_for(self.button_apply)

    def get_search_filter(self) -> WebElement:
        return self.wait_for(self.search_filter)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_feedback_id(self) -> WebElement:
        return self.get_elements(self.table_columns)[0]

    def get_issue_type(self) -> WebElement:
        return self.get_elements(self.table_columns)[1]

    def get_household_id(self) -> WebElement:
        return self.get_elements(self.table_columns)[2]

    def get_linked_grievance(self) -> WebElement:
        return self.get_elements(self.table_columns)[3]

    def get_created_by(self) -> WebElement:
        return self.get_elements(self.table_columns)[4]

    def get_creation_date(self) -> WebElement:
        return self.get_elements(self.table_columns)[5]

    def get_rows(self) -> list[WebElement]:
        return self.get_elements(self.table_row)

    def get_row(self, number: int) -> WebElement:
        for _ in range(10):
            if len(self.get_elements(self.table_row)) == number + 1:
                break
            sleep(1)
        return self.get_elements(self.table_row)[number]

    def get_days_filter_popup(self) -> WebElement:
        return self.wait_for(self.days_filter_popup)

    def get_creation_date_to_filter(self) -> WebElement:
        return self.wait_for(self.creation_date_to_filter)

    def get_date_title_filter_popup(self) -> WebElement:
        return self.wait_for(self.date_title_filter_popup)

    def get_issue_type_filter(self) -> WebElement:
        return self.wait_for(self.issue_type_filter)

    def disappear_table_row_loading(self) -> WebElement:
        return self.wait_for_disappear(self.table_row_loading)

    def get_table_row_loading(self) -> WebElement:
        return self.wait_for(self.table_row_loading)

    def get_option(self) -> WebElement:
        return self.wait_for(self.option)
