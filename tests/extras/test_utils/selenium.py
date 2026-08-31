import time

from django.conf import settings
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from seleniumbase import BaseCase

from e2e.helpers.date_picker import fill_mui_date


class HopeTestBrowser(BaseCase):
    """SeleniumBase browser wrapper for HOPE E2E tests.

    Modeled on Aurora's AuroraSeleniumTC:
    https://github.com/unicef/hope-aurora/blob/develop/tests/extras/testutils/selenium.py
    """

    live_server_url: str = ""

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def base_method(self):
        pass

    def open(self, url: str):
        # maximize_window() is a no-op in headless Chrome, leaving the small
        # default viewport that breaks layout-sensitive click targets on CI.
        self.set_window_size(1920, 1080)
        return super().open(f"{self.live_server_url}{url}")

    def login(self, username: str = "superuser", password: str = "testtest2", *, wait_for_drawer: bool = True):
        self.open(f"/api/{settings.ADMIN_PANEL_URL}/")
        self.execute_script(
            """
            window.indexedDB.databases().then(dbs => dbs.forEach(db => {
                indexedDB.deleteDatabase(db.name);
            }));
            window.localStorage.clear();
            window.sessionStorage.clear();
            """
        )
        self.wait_for_element_visible("#id_username")
        self.type("#id_username", username)
        self.type("#id_password", password)
        self.click('#login-form input[type="submit"]')
        self.wait_for_ready_state_complete()
        if wait_for_drawer:
            # Django admin login redirects back to /api/admin/, not the SPA.
            # Navigate explicitly to the frontend root.
            self.open("/")
            self.wait_for_ready_state_complete()
            # wait_for_ready_state_complete only checks document.readyState; the React
            # app mounts after that. Wait for the authenticated layout's drawer so
            # callers can click nav items immediately without racing the first paint.
            self.wait_for_element_visible('[data-cy="drawer-items"]', timeout=30)

    def select_listbox_element(self, name: str, selector: str = 'ul[role="listbox"]', timeout: int = 10):
        self.wait_for_element_visible(selector, timeout=timeout)
        # A click can be dropped during the MUI open transition; if the listbox
        # stays open after the pick, click the option once more.
        self._click_listbox_option(name, selector, timeout)
        if not self._listbox_closed(selector):
            self._click_listbox_option(name, selector, timeout)
        self.wait_for_element_absent(selector)

    def _click_listbox_option(
        self,
        name: str,
        selector: str,
        timeout: int = 10,
        not_found_message: str | None = None,
    ) -> None:
        """Click the option labelled exactly `name`, retrying while an async listbox re-renders."""
        deadline = time.monotonic() + timeout
        labels: list[str] = []
        while True:
            try:
                options = self.find_elements(f"{selector} li")
                labels = [option.text.strip() for option in options]
                matches = [option for option, label in zip(options, labels, strict=True) if label == name]
                if matches:
                    # Clicking the node avoids landing on a neighbour mid-transform.
                    self.execute_script("arguments[0].click()", matches[0])
                    return
            except StaleElementReferenceException:
                labels = []
            if time.monotonic() >= deadline:
                message = not_found_message or f"Option '{name}' not found in listbox"
                raise AssertionError(f"{message}. Available: {labels}")
            time.sleep(0.1)

    def _listbox_closed(self, selector: str, timeout: int = 5) -> bool:
        try:
            self.wait_for_element_absent(selector, timeout=timeout)
            return True
        except Exception:  # noqa: BLE001
            return False

    def select_option_by_name(self, option_name: str, selector: str | None = None) -> None:
        if selector is None:
            selector = f'li[data-cy="select-option-{option_name}"]'
        self._click_menu_option(selector)
        if not self._listbox_closed(selector):
            self._click_menu_option(selector)
        self.wait_for_element_absent(selector)

    def _click_menu_option(self, selector: str) -> None:
        """Click the option matching `selector`, on the node so the click cannot miss mid-transform."""
        option = self.wait_for_element_clickable(selector)
        self.execute_script("arguments[0].click()", option)

    def select_dropdown_option(self, field_name: str, option_name: str) -> None:
        """Open a FormikSelectField by its Formik field name and pick an option by its visible name.

        FormikSelectField sets `data-cy="select-{field_name}"` on the Select trigger and
        `data-cy="select-option-{name}"` on each MenuItem, so callers need only the field
        name and option label — no data-cy strings.
        """
        self.click(f'[data-cy="select-{field_name}"]')
        self.select_option_by_name(option_name)

    def fill_date(self, selector: str, value: str, timeout: int = 10) -> None:
        """Type a yyyy-MM-dd date into a MUI X date picker located by `selector`.

        MUI X v9 fields have no single typeable input; `selector` should match the
        field's hidden value input (e.g. `input[name="startDate"]`), which is not
        visible, so we locate it by presence and drive the editable section list.
        """
        field_element = self.wait_for_element_present(selector, timeout=timeout)
        fill_mui_date(self.driver, field_element, value)

    def assert_value(self, selector: str, expected: str, timeout: int = 10):
        actual = self.get_value(selector, timeout=timeout)
        assert actual == expected, f"Expected value '{expected}' for {selector}, got '{actual}'"

    def select_chip_option(self, name: str, select_selector: str) -> None:
        """Pick one option from a MUI multiple-Select chip field and dismiss the listbox.

        MUI multiple-Select keeps the listbox open after each pick. A JavaScript
        Escape dispatch closes the Popover without requiring a visible backdrop click.
        """
        # Click the inner input rather than the wrapper — when chips are already
        # selected, a click on the wrapper may land on a chip and fail to focus
        # the Autocomplete input.
        inner_input = f"{select_selector} input"
        if self.is_element_present(inner_input):
            self.click(inner_input)
        else:
            self.click(select_selector)
        self.wait_for_element_visible('ul[role="listbox"]')
        self._click_listbox_option(
            name,
            'ul[role="listbox"]',
            not_found_message=f"Chip option '{name}' not found in select",
        )
        self.execute_script(
            "document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', keyCode:27, bubbles:true}))"
        )
        self.wait_for_element_absent('ul[role="listbox"]')

    def set_value(self, selector: str, text: str) -> None:
        """Type text into a React-controlled input or textarea without macOS autocorrect interference.

        Disables spellcheck on the element before typing so the OS cannot silently
        drop or replace characters mid-input, then restores the original attribute.
        """
        elem = self.find_element(selector)
        original = self.execute_script("return arguments[0].getAttribute('spellcheck')", elem)
        self.execute_script("arguments[0].setAttribute('spellcheck', 'false')", elem)
        self.triple_click(selector)
        self.send_keys(selector, text)
        if original is None:
            self.execute_script("arguments[0].removeAttribute('spellcheck')", elem)
        else:
            self.execute_script("arguments[0].setAttribute('spellcheck', arguments[1])", elem, original)

    def triple_click(self, selector: str):
        """Triple-click an element to select all of its text content."""
        elem = self.find_element(selector)
        actions = ActionChains(self.driver)
        actions.move_to_element(elem).click(elem).click(elem).click(elem).perform()

    def scroll_main_content(self, scroll_by: int = 600):
        self.execute_script(
            f"""
            var container = document.querySelector("div[data-cy='main-content']");
            if (container) container.scrollBy(0, {scroll_by});
            """
        )
        self.wait_for_ready_state_complete()
