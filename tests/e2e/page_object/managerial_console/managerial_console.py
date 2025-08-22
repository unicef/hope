from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ManagerialConsole(BaseComponents):
    page_header_title = 'h5[data-cy="page-header-title"]'
    title = 'h6[data-cy="title"]'
    approve_button = 'button[data-cy="approve-button"]'
    select_all_approval = 'span[data-cy="select-all-approval"]'
    program_select_approval = 'div[data-cy="program-select-approval"]'
    select_approval = 'span[data-cy="select-approval"]'
    column_field = 'td[data-cy="column-field"]'
    authorize_button = 'button[data-cy="authorize-button"]'
    select_all_authorization = 'span[data-cy="select-all-authorization"]'
    program_select_authorization = 'div[data-cy="program-select-authorization"]'
    select_authorization = 'span[data-cy="select-authorization"]'
    column_field_authorization = 'td[data-cy="column-field-authorization"]'
    release_button = 'button[data-cy="release-button"]'
    select_all_release = 'span[data-cy="select-all-release"]'
    program_select_release = 'div[data-cy="program-select-release"]'
    select_release = 'span[data-cy="select-release"]'
    column_field_release = 'td[data-cy="column-field-release"]'
    search_released = 'div[data-cy="search-released"]'
    program_select_released = 'div[data-cy="program-select-released"]'
    column_field_released = 'td[data-cy="column-field-released"]'
    plans_ids = 'span[data-cy="plans-ids"]'
    button_cancel = 'button[data-cy="button-cancel"]'
    button_save = 'button[data-cy="button-save"]'
    comment_approve = 'div[data-cy="comment-approve"]'

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_title(self) -> WebElement:
        return self.wait_for(self.title)

    def get_approve_button(self) -> WebElement:
        return self.wait_for(self.approve_button)

    def get_select_all_approval(self) -> WebElement:
        return self.wait_for(self.select_all_approval)

    def get_program_select_approval(self) -> WebElement:
        return self.wait_for(self.program_select_approval)

    def get_select_approval(self) -> WebElement:
        return self.wait_for(self.select_approval)

    def get_column_field(self) -> WebElement:
        return self.wait_for(self.column_field)

    def get_authorize_button(self) -> WebElement:
        return self.wait_for(self.authorize_button)

    def get_select_all_authorization(self) -> WebElement:
        return self.wait_for(self.select_all_authorization)

    def get_program_select_authorization(self) -> WebElement:
        return self.wait_for(self.program_select_authorization)

    def get_select_authorization(self) -> WebElement:
        return self.wait_for(self.select_authorization)

    def get_column_field_authorization(self) -> WebElement:
        return self.wait_for(self.column_field_authorization)

    def get_release_button(self) -> WebElement:
        return self.wait_for(self.release_button)

    def get_select_all_release(self) -> WebElement:
        return self.wait_for(self.select_all_release)

    def get_program_select_release(self) -> WebElement:
        return self.wait_for(self.program_select_release)

    def get_select_release(self) -> WebElement:
        return self.wait_for(self.select_release)

    def get_column_field_release(self) -> WebElement:
        return self.wait_for(self.column_field_release)

    def get_search_released(self) -> WebElement:
        return self.wait_for(self.search_released)

    def get_program_select_released(self) -> WebElement:
        return self.wait_for(self.program_select_released)

    def get_column_field_released(self) -> WebElement:
        return self.wait_for(self.column_field_released)

    def get_plans_ids(self) -> WebElement:
        return self.wait_for(self.plans_ids)

    def get_button_cancel(self) -> WebElement:
        return self.wait_for(self.button_cancel)

    def get_button_save(self) -> WebElement:
        return self.wait_for(self.button_save)

    def get_comment_approve(self) -> WebElement:
        return self.wait_for(self.comment_approve)
