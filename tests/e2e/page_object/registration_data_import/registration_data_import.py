from time import sleep

from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class RegistrationDataImport(BaseComponents):
    # Locators
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_import = 'button[data-cy="button-import"]'
    filter_search = 'div[data-cy="filter-search"]'
    imported_by_input = 'div[data-cy="Imported By-input"]'
    filter_status = 'div[data-cy="filter-status"]'
    filter_size_min = 'div[data-cy="filter-size-min"]'
    filter_size_max = 'div[data-cy="filter-size-max"]'
    date_picker_filter = 'div[data-cy="date-picker-filter"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    table_title = 'h6[data-cy="table-title"]'
    table_label = 'span[data-cy="table-label"]'
    status_container = 'div[data-cy="status-container"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    table_row = 'tr[role="checkbox"]'
    import_type_select = 'div[data-cy="import-type-select"]'
    kobo_project_select = 'div[data-cy="kobo-project-select"]'
    progress_circle = 'span[role="progressbar"]'
    download_template = 'a[data-cy="a-download-template"]'
    button_import_rdi = 'button[data-cy="button-import-rdi"]'
    excel_item = 'li[data-cy="excel-menu-item"]'
    kobo_item = 'li[data-cy="kobo-menu-item"]'
    input_name = 'input[data-cy="input-name"]'
    input_file = 'input[type="file"]'
    number_of_households = 'div[data-cy="number-of-households"]'
    number_of_individuals = 'div[data-cy="number-of-individuals"]'
    errors_container = 'div[data-cy="errors-container"]'

    # Texts
    title_text = "Registration Data Import"
    import_text = "IMPORT"
    table_title_text = "List of Imports"
    import_type_select_text = "Import From"
    download_template_text = "DOWNLOAD TEMPLATE"
    kobo_item_text = "Kobo"
    excel_item_text = "Excel"
    input_file_text = "UPLOAD FILE"

    # Elements

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_import(self) -> WebElement:
        return self.wait_for(self.button_import)

    def get_filter_search(self) -> WebElement:
        return self.wait_for(self.filter_search)

    def get_imported_by_input(self) -> WebElement:
        return self.wait_for(self.imported_by_input)

    def get_filter_status(self) -> WebElement:
        return self.wait_for(self.filter_status)

    def get_filter_size_min(self) -> WebElement:
        return self.wait_for(self.filter_size_min)

    def get_filter_size_max(self) -> WebElement:
        return self.wait_for(self.filter_size_max)

    def get_date_picker_filter(self) -> WebElement:
        return self.wait_for(self.date_picker_filter)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_table_label(self) -> WebElement:
        return self.get_elements(self.table_label)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_rows(self) -> list[WebElement]:
        return self.get_elements(self.table_row)

    def expected_rows(self, number: int) -> bool:
        for _ in range(15):
            if len(self.get_rows()) == number:
                return True
            sleep(1)
        return False

    def get_import_type_select(self) -> WebElement:
        return self.wait_for(self.import_type_select)

    def get_kobo_project_select(self) -> WebElement:
        return self.wait_for(self.kobo_project_select)

    def check_loading_progress_circle(self) -> None:
        self.wait_for(self.progress_circle)
        self.wait_for_disappear(self.progress_circle)

    def get_download_template(self) -> WebElement:
        return self.wait_for(self.download_template)

    def get_button_import_file(self) -> WebElement:
        return self.wait_for(self.button_import_rdi)

    def disappear_button_import_file(self) -> None:
        self.wait_for_disappear(self.button_import_rdi, timeout=60)

    def get_excel_item(self) -> WebElement:
        return self.wait_for(self.excel_item)

    def get_kobo_item(self) -> WebElement:
        return self.wait_for(self.kobo_item)

    def get_input_name(self) -> WebElement:
        return self.wait_for(self.input_name)

    def get_input_file(self) -> WebElement:
        return self.wait_for(self.input_file)

    def get_number_of_households(self) -> WebElement:
        return self.wait_for(self.number_of_households)

    def get_number_of_individuals(self) -> WebElement:
        return self.wait_for(self.number_of_individuals)

    def get_errors_container(self) -> WebElement:
        return self.wait_for(self.errors_container)

    def button_import_file_is_enabled(self, timeout: int = 30) -> bool:
        for _ in range(timeout):
            if self.get_button_import_file().is_enabled():
                return True
            sleep(1)
        return False
