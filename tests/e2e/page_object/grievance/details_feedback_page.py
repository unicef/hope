from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class FeedbackDetailsPage(BaseComponents):
    # Locators
    page_header_container = 'div[data-cy="page-header-container"]'
    title_page = 'h5[data-cy="page-header-title"]'
    button_edit = 'a[data-cy="button-edit"]'
    label_category = 'div[data-cy="label-Category"]'
    label_issue_type = 'div[data-cy="label-Issue Type"]'
    label_household_id = 'div[data-cy="label-Group ID"]'
    label_individual_id = 'div[data-cy="label-Member ID"]'
    label_programme = 'div[data-cy="label-Programme"]'
    label_created_by = 'div[data-cy="label-Created By"]'
    label_date_created = 'div[data-cy="label-Date Created"]'
    label_last_modified_date = 'div[data-cy="label-Last Modified Date"]'
    label_administrative_level2 = 'div[data-cy="label-Administrative Level 2"]'
    label_area_village_pay_point = 'div[data-cy="label-Area / Village / Pay point"]'
    label_languages_spoken = 'div[data-cy="label-Languages Spoken"  ]'
    label_description = 'div[data-cy="label-Description"]'
    label_comments = 'div[data-cy="label-Comments"]'
    button_create_linked_ticket = 'button[data-cy="button-create-linked-ticket"]'
    label_ticket_id = 'div[data-cy="label-Ticket Id"]'

    # Texts
    text_title = "Feedback ID: "
    text_category = "Feedback"
    text_issue_type = "Negative Feedback"
    text_description = "Negative Feedback"

    # Elements
    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_title_page(self) -> WebElement:
        return self.wait_for(self.title_page)

    def get_button_edit(self) -> WebElement:
        return self.wait_for(self.button_edit)

    def get_category(self) -> WebElement:
        return self.wait_for(self.label_category)

    def get_issue_type(self) -> WebElement:
        return self.wait_for(self.label_issue_type)

    def get_household_id(self) -> WebElement:
        return self.wait_for(self.label_household_id)

    def get_individual_id(self) -> WebElement:
        return self.wait_for(self.label_individual_id)

    def get_programme(self) -> WebElement:
        return self.wait_for(self.label_programme)

    def get_created_by(self) -> WebElement:
        return self.wait_for(self.label_created_by)

    def get_date_created(self) -> WebElement:
        return self.wait_for(self.label_date_created)

    def get_last_modified_date(self) -> WebElement:
        return self.wait_for(self.label_last_modified_date)

    def get_administrative_level2(self) -> WebElement:
        return self.wait_for(self.label_administrative_level2)

    def get_area_village_pay_point(self) -> WebElement:
        return self.wait_for(self.label_area_village_pay_point)

    def get_languages_spoken(self) -> WebElement:
        return self.wait_for(self.label_languages_spoken)

    def get_description(self) -> WebElement:
        return self.wait_for(self.label_description)

    def get_comments(self) -> WebElement:
        return self.wait_for(self.label_comments)

    def get_button_create_linked_ticket(self) -> WebElement:
        return self.wait_for(self.button_create_linked_ticket)

    def get_label_ticket_id(self) -> WebElement:
        return self.wait_for(self.label_ticket_id)
