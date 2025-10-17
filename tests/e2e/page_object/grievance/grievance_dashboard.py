from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class GrievanceDashboard(BaseComponents):
    # Locators
    page_header_title = 'h5[data-cy="page-header-title"]'
    total_number_of_tickets_top_number = 'div[data-cy="total-number-of-tickets-top-number"]'
    labelized_field_container_total_number_of_tickets_system_generated = (
        'div[data-cy="labelized-field-container-total-number-of-tickets-system-generated"]'
    )
    label_system_generated = 'div[data-cy="label-SYSTEM-GENERATED"]'
    labelized_field_container_total_number_of_tickets_user_generated = (
        'div[data-cy="labelized-field-container-total-number-of-tickets-user-generated"]'
    )
    label_user_generated = 'div[data-cy="label-USER-GENERATED"]'
    total_number_of_closed_tickets_top_number = 'div[data-cy="total-number-of-closed-tickets-top-number"]'
    labelized_field_container_total_number_of_closed_tickets_system_generated = (
        'div[data-cy="labelized-field-container-total-number-of-closed-tickets-system-generated"]'
    )
    labelized_field_container_total_number_of_closed_tickets_user_generated = (
        'div[data-cy="labelized-field-container-total-number-of-closed-tickets-user-generated"]'
    )
    tickets_average_resolution_top_number = 'div[data-cy="tickets-average-resolution-top-number"]'
    labelized_field_container_tickets_average_resolution_system_generated = (
        'div[data-cy="labelized-field-container-tickets-average-resolution-system-generated"]'
    )
    labelized_field_container_tickets_average_resolution_user_generated = (
        'div[data-cy="labelized-field-container-tickets-average-resolution-user-generated"]'
    )

    # Texts
    text_title = "Grievance Dashboard"

    # Elements

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_total_number_of_tickets_top_number(self) -> WebElement:
        return self.wait_for(self.total_number_of_tickets_top_number)

    def get_labelized_field_container_total_number_of_tickets_system_generated(
        self,
    ) -> WebElement:
        return self.wait_for(self.labelized_field_container_total_number_of_tickets_system_generated)

    def get_label_system_generated(self) -> WebElement:
        return self.wait_for(self.label_system_generated)

    def get_labelized_field_container_total_number_of_tickets_user_generated(
        self,
    ) -> WebElement:
        return self.wait_for(self.labelized_field_container_total_number_of_tickets_user_generated)

    def get_label_user_generated(self) -> WebElement:
        return self.wait_for(self.label_user_generated)

    def get_total_number_of_closed_tickets_top_number(self) -> WebElement:
        return self.wait_for(self.total_number_of_closed_tickets_top_number)

    def get_labelized_field_container_total_number_of_closed_tickets_system_generated(
        self,
    ) -> WebElement:
        return self.wait_for(self.labelized_field_container_total_number_of_closed_tickets_system_generated)

    def get_labelized_field_container_total_number_of_closed_tickets_user_generated(
        self,
    ) -> WebElement:
        return self.wait_for(self.labelized_field_container_total_number_of_closed_tickets_user_generated)

    def get_tickets_average_resolution_top_number(self) -> WebElement:
        return self.wait_for(self.tickets_average_resolution_top_number)

    def get_labelized_field_container_tickets_average_resolution_system_generated(
        self,
    ) -> WebElement:
        return self.wait_for(self.labelized_field_container_tickets_average_resolution_system_generated)

    def get_labelized_field_container_tickets_average_resolution_user_generated(
        self,
    ) -> WebElement:
        return self.wait_for(self.labelized_field_container_tickets_average_resolution_user_generated)
