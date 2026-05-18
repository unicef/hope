from django.conf import settings
from seleniumbase import BaseCase


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
        self.maximize_window()
        return super().open(f"{self.live_server_url}{url}")

    def login(self, username: str = "superuser", password: str = "testtest2"):
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
        elements = self.find_elements(f"{selector} li")
        for element in elements:
            if element.text.strip() == name:
                element.click()
                self.wait_for_element_absent(selector)
                return
        raise AssertionError(f"Option '{name}' not found in listbox. Available: {[e.text.strip() for e in elements]}")

    def select_option_by_name(self, option_name: str, selector: str | None = None):
        if selector is None:
            selector = f'li[data-cy="select-option-{option_name}"]'
        self.wait_for_element_visible(selector)
        self.click(selector)
        self.wait_for_element_absent(selector)

    def select_dropdown_option(self, field_name: str, option_name: str) -> None:
        """Open a FormikSelectField by its Formik field name and pick an option by its visible name.

        FormikSelectField sets `data-cy="select-{field_name}"` on the Select trigger and
        `data-cy="select-option-{name}"` on each MenuItem, so callers need only the field
        name and option label — no data-cy strings.
        """
        self.click(f'[data-cy="select-{field_name}"]')
        self.select_option_by_name(option_name)

    def assert_value(self, selector: str, expected: str, timeout: int = 10):
        actual = self.get_value(selector, timeout=timeout)
        assert actual == expected, f"Expected value '{expected}' for {selector}, got '{actual}'"

    def select_chip_option(self, name: str, select_selector: str) -> None:
        """Pick one option from a MUI multiple-Select chip field and dismiss the listbox.

        MUI multiple-Select keeps the listbox open after each pick. A JavaScript
        Escape dispatch closes the Popover without requiring a visible backdrop click.
        """
        self.click(select_selector)
        self.wait_for_element_visible('ul[role="listbox"]')
        elements = self.find_elements('ul[role="listbox"] li')
        for element in elements:
            if element.text.strip() == name:
                element.click()
                break
        else:
            raise AssertionError(
                f"Chip option '{name}' not found in select. Available: {[e.text.strip() for e in elements]}"
            )
        self.execute_script(
            "document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', keyCode:27, bubbles:true}))"
        )
        self.wait_for_element_absent('ul[role="listbox"]')

    def scroll_main_content(self, scroll_by: int = 600):
        self.execute_script(
            f"""
            var container = document.querySelector("div[data-cy='main-content']");
            if (container) container.scrollBy(0, {scroll_by});
            """
        )
        self.wait_for_ready_state_complete()
