from time import sleep

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from e2e.page_object.base_components import BaseComponents


class GenericImport(BaseComponents):
    """Page Object for Generic Import upload page."""

    # Locators - Form elements
    page_title = "h1.generic-import-title"
    form = "#generic-import-form"
    select_business_area = "#id_business_area"
    select_program = "#id_program"
    input_file = "#id_file"
    button_submit = "button.submit-button"

    # File upload area
    file_upload_label = ".file-upload-label"
    file_upload_text_main = ".file-upload-text .main-text"
    file_upload_text_sub = ".file-upload-text .sub-text"
    file_name_display = "#file-name-display"

    # Messages
    messages_container = ".messages"
    message_success = ".message.success"
    message_error = ".message.error"
    message_warning = ".message.warning"
    message_info = ".message.info"

    # Error display
    error_list = ".error-list"

    # Texts
    title_text = "Generic Import - Upload File"
    button_submit_text = "Upload and Process"
    button_uploading_text = "Uploading..."
    loading_programs_text = "Loading programs..."
    select_program_placeholder = "First select a Business Area"
    no_programs_text = "No programs available"

    def get_page_title(self) -> WebElement:
        return self.wait_for(self.page_title)

    def get_form(self) -> WebElement:
        return self.wait_for(self.form)

    def get_select_business_area(self) -> WebElement:
        return self.wait_for(self.select_business_area)

    def get_select_program(self) -> WebElement:
        return self.wait_for(self.select_program)

    def get_input_file(self) -> WebElement:
        """Get file input - uses presence not visibility since input is hidden."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions

        return self._wait(30).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, self.input_file)))

    def get_button_submit(self) -> WebElement:
        return self.wait_for(self.button_submit)

    def get_file_upload_label(self) -> WebElement:
        return self.wait_for(self.file_upload_label)

    def get_file_name_display(self) -> WebElement:
        return self.wait_for(self.file_name_display)

    def get_message_success(self) -> WebElement:
        return self.wait_for(self.message_success)

    def get_message_error(self) -> WebElement:
        return self.wait_for(self.message_error)

    def get_error_list(self) -> WebElement:
        return self.wait_for(self.error_list)

    # Helper methods

    def navigate_to_generic_import(self) -> None:
        """Navigate to Generic Import upload page."""
        self.driver.get(f"{self.driver.live_server.url}/api/generic-import/upload/")

    def select_business_area_by_name(self, name: str) -> None:
        """Select business area from dropdown by visible text."""
        select = Select(self.get_select_business_area())
        select.select_by_visible_text(name)

    def select_business_area_by_index(self, index: int) -> None:
        """Select business area from dropdown by index."""
        select = Select(self.get_select_business_area())
        select.select_by_index(index)

    def select_program_by_name(self, name: str) -> None:
        """Select program from dropdown by visible text."""
        select = Select(self.get_select_program())
        select.select_by_visible_text(name)

    def select_program_by_index(self, index: int) -> None:
        """Select program from dropdown by index."""
        select = Select(self.get_select_program())
        select.select_by_index(index)

    def upload_file(self, file_path: str) -> None:
        """Upload file using the file input."""
        file_input = self.get_input_file()
        file_input.send_keys(file_path)

    def click_submit(self) -> None:
        """Click the submit button."""
        self.get_button_submit().click()

    def is_program_select_disabled(self) -> bool:
        """Check if program select is disabled."""
        return not self.get_select_program().is_enabled()

    def is_program_select_enabled(self) -> bool:
        """Check if program select is enabled."""
        return self.get_select_program().is_enabled()

    def is_submit_button_disabled(self) -> bool:
        """Check if submit button is disabled."""
        return not self.get_button_submit().is_enabled()

    def get_submit_button_text(self) -> str:
        """Get submit button text."""
        return self.get_button_submit().text

    def get_program_select_text(self) -> str:
        """Get currently selected program text or placeholder."""
        select = Select(self.get_select_program())
        return select.first_selected_option.text

    def get_business_area_select_text(self) -> str:
        """Get currently selected business area text."""
        select = Select(self.get_select_business_area())
        return select.first_selected_option.text

    def get_file_name_display_text(self) -> str:
        """Get displayed file name text."""
        return self.get_file_name_display().text

    def is_file_name_displayed(self) -> bool:
        """Check if file name display is visible."""
        element = self.get_file_name_display()
        return element.is_displayed() and element.value_of_css_property("display") != "none"

    def get_business_area_options_count(self) -> int:
        """Get number of business area options."""
        select = Select(self.get_select_business_area())
        return len(select.options)

    def get_program_options_count(self) -> int:
        """Get number of program options."""
        select = Select(self.get_select_program())
        return len(select.options)

    def wait_for_programs_to_load(self, timeout: int = 30) -> bool:
        """Wait for programs to load after selecting business area."""
        for _ in range(timeout):
            if self.is_program_select_enabled():
                text = self.get_program_select_text()
                if text not in [self.loading_programs_text, self.select_program_placeholder]:
                    return True
            sleep(1)
        return False

    def wait_for_program_select_enabled(self, timeout: int = 30) -> bool:
        """Wait for program select to become enabled."""
        for _ in range(timeout):
            if self.is_program_select_enabled():
                return True
            sleep(1)
        return False

    def wait_for_success_alert(self, timeout: int = 30) -> bool:
        """Wait for success alert dialog."""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            return True
        except Exception:
            return False

    def accept_alert(self) -> str:
        """Accept alert and return its text."""
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text

    def dismiss_alert(self) -> str:
        """Dismiss alert and return its text."""
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.dismiss()
        return text

    def get_alert_text(self) -> str:
        """Get alert text without dismissing."""
        alert = self.driver.switch_to.alert
        return alert.text

    def drag_and_drop_file(self, file_path: str) -> None:
        """Simulate drag and drop file upload.

        Note: Selenium doesn't support actual drag & drop from file system,
        so we use send_keys on the hidden input instead.
        """
        self.upload_file(file_path)

    def get_selected_business_area_slug(self) -> str:
        """Get data-slug attribute of selected business area."""
        select = Select(self.get_select_business_area())
        option = select.first_selected_option
        return option.get_attribute("data-slug") or ""

    def get_selected_program_slug(self) -> str:
        """Get data-slug attribute of selected program."""
        select = Select(self.get_select_program())
        option = select.first_selected_option
        return option.get_attribute("data-slug") or ""
