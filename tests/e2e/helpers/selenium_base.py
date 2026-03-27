from django.conf import settings
from seleniumbase import BaseCase


class HopeTestBrowser(BaseCase):
    """SeleniumBase browser wrapper for HOPE E2E tests.

    Modeled on Aurora's AuroraSeleniumTC:
    https://github.com/unicef/hope-aurora/blob/develop/tests/extras/testutils/selenium.py
    """

    live_server_url: str = ""

    def setUp(self, masterqa_mode=False):
        super().setUp()

    def tearDown(self):
        self.save_teardown_screenshot()
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
        self.click('//*[@id="login-form"]/div[3]/input', by="xpath")
        self.sleep(0.3)
        self.open("/")
        self.wait_for_ready_state_complete()

    def select_listbox_element(self, name: str, timeout: int = 10):
        self.wait_for_element_visible('ul[role="listbox"]', timeout=timeout)
        self.sleep(1)
        self.click(f'ul[role="listbox"] li:contains("{name}")')
        self.wait_for_element_absent('ul[role="listbox"]')

    def select_option_by_name(self, option_name: str):
        selector = f'li[data-cy="select-option-{option_name}"]'
        self.wait_for_element_visible(selector)
        self.click(selector)
        self.wait_for_element_absent(selector)

    def scroll_main_content(self, scroll_by: int = 600):
        self.execute_script(
            f"""
            var container = document.querySelector("div[data-cy='main-content']");
            if (container) container.scrollBy(0, {scroll_by});
            """
        )
        self.sleep(1)
