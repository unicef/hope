from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ProgramLog(BaseComponents):
    main_activity_log_table = 'div[data-cy="main-activity-log-table"]'
    table_collapse = 'div[data-cy="table-collapse"]'
    activity_log_table = 'div[data-cy="activity-log-table"]'
    table_header_row = 'div[data-cy="table-header-row"]'
    header_cell_date = 'div[data-cy="header-cell-date"]'
    header_cell_user = 'div[data-cy="header-cell-user"]'
    header_cell_content_type__name = 'div[data-cy="header-cell-content_type__name"]'
    header_cell_object = 'div[data-cy="header-cell-object"]'
    header_cell_action = 'div[data-cy="header-cell-action"]'
    header_cell_changes = 'div[data-cy="header-cell-changes"]'
    header_cell_changefrom = 'div[data-cy="header-cell-changeFrom"]'
    header_cell_changeto = 'div[data-cy="header-cell-changeTo"]'
    log_row_single_change = 'div[data-cy="log-row-single-change"]'
    timestamp_cell = 'div[data-cy="timestamp-cell"]'
    user_cell = 'div[data-cy="user-cell"]'
    content_type_cell = 'div[data-cy="content-type-cell"]'
    object_representation_cell = 'div[data-cy="object-representation-cell"]'
    action_cell = 'div[data-cy="action-cell"]'
    change_key_cell = 'div[data-cy="change-key-cell"]'
    from_value_cell = 'div[data-cy="from-value-cell"]'
    to_value_cell = 'div[data-cy="to-value-cell"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    pagination_actions = 'div[data-cy="pagination-actions"]'
    previous_page_button = 'button[data-cy="previous-page-button"]'
    next_page_button = 'button[data-cy="next-page-button"]'
    page_header_title = 'h5[data-cy="page-header-title"]'

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_main_activity_log_table(self) -> WebElement:
        return self.wait_for(self.main_activity_log_table)

    def get_table_collapse(self) -> WebElement:
        return self.wait_for(self.table_collapse)

    def get_activity_log_table(self) -> WebElement:
        return self.wait_for(self.activity_log_table)

    def get_table_header_row(self) -> WebElement:
        return self.wait_for(self.table_header_row)

    def get_header_cell_date(self) -> WebElement:
        return self.wait_for(self.header_cell_date)

    def get_header_cell_user(self) -> WebElement:
        return self.wait_for(self.header_cell_user)

    def get_header_cell_content_type__name(self) -> WebElement:
        return self.wait_for(self.header_cell_content_type__name)

    def get_header_cell_object(self) -> WebElement:
        return self.wait_for(self.header_cell_object)

    def get_header_cell_action(self) -> WebElement:
        return self.wait_for(self.header_cell_action)

    def get_header_cell_changes(self) -> WebElement:
        return self.wait_for(self.header_cell_changes)

    def get_header_cell_changefrom(self) -> WebElement:
        return self.wait_for(self.header_cell_changefrom)

    def get_header_cell_changeto(self) -> WebElement:
        return self.wait_for(self.header_cell_changeto)

    def get_log_row_single_change(self) -> WebElement:
        return self.wait_for(self.log_row_single_change)

    def get_timestamp_cell(self) -> WebElement:
        return self.wait_for(self.timestamp_cell)

    def get_user_cell(self) -> WebElement:
        return self.wait_for(self.user_cell)

    def get_content_type_cell(self) -> WebElement:
        return self.wait_for(self.content_type_cell)

    def get_object_representation_cell(self) -> WebElement:
        return self.wait_for(self.object_representation_cell)

    def get_action_cell(self) -> WebElement:
        return self.wait_for(self.action_cell)

    def get_change_key_cell(self) -> WebElement:
        return self.wait_for(self.change_key_cell)

    def get_from_value_cell(self) -> WebElement:
        return self.wait_for(self.from_value_cell)

    def get_to_value_cell(self) -> WebElement:
        return self.wait_for(self.to_value_cell)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_pagination_actions(self) -> WebElement:
        return self.wait_for(self.pagination_actions)

    def get_previous_page_button(self) -> WebElement:
        return self.wait_for(self.previous_page_button)

    def get_next_page_button(self) -> WebElement:
        return self.wait_for(self.next_page_button)
