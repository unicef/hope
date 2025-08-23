from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class AccountabilityCommunicationDetails(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    label_created_by = 'div[data-cy="label-Created By"]'
    label_date_created = 'div[data-cy="label-Date Created"]'
    label_target_population = 'div[data-cy="label-Target Population"]'
    table_title = 'h6[data-cy="table-title"]'
    household_id = 'th[data-cy="household-id"]'
    table_label = 'span[data-cy="table-label"]'
    status = 'th[data-cy="status"]'
    household_head_name = 'th[data-cy="household-head-name"]'
    household_size = 'th[data-cy="household-size"]'
    household_location = 'th[data-cy="household-location"]'
    household_residence_status = 'th[data-cy="household-residence-status"]'
    household_registration_date = 'th[data-cy="household-registration-date"]'
    table_row = 'tr[data-cy="table-row"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    communication_message_details = 'div[data-cy="communication-message-details"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_label_created_by(self) -> WebElement:
        return self.wait_for(self.label_created_by)

    def get_label_date_created(self) -> WebElement:
        return self.wait_for(self.label_date_created)

    def get_label_target_population(self) -> WebElement:
        return self.wait_for(self.label_target_population)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_household_id(self) -> WebElement:
        return self.wait_for(self.household_id)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_status(self) -> WebElement:
        return self.wait_for(self.status)

    def get_household_head_name(self) -> WebElement:
        return self.wait_for(self.household_head_name)

    def get_household_size(self) -> WebElement:
        return self.wait_for(self.household_size)

    def get_household_location(self) -> WebElement:
        return self.wait_for(self.household_location)

    def get_household_residence_status(self) -> WebElement:
        return self.wait_for(self.household_residence_status)

    def get_household_registration_date(self) -> WebElement:
        return self.wait_for(self.household_registration_date)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_communication_message_details(self) -> WebElement:
        return self.wait_for(self.communication_message_details)
