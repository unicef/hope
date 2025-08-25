import sys
from time import sleep

from e2e.helpers.helper import Common
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class BaseComponents(Common):
    # Labels
    business_area_container = 'div[data-cy="business-area-container"]'
    global_program_filter_container = 'div[data-cy="global-program-filter-container"]'
    global_program_filter = 'button[data-cy="global-program-filter"]'
    menu_user_profile = 'button[data-cy="menu-user-profile"]'
    side_nav = 'div[data-cy="side-nav"]'
    nav_country_dashboard = 'a[data-cy="nav-Country Dashboard"]'
    nav_registration_data_import = 'a[data-cy="nav-Registration Data Import"]'
    nav_programme_population = 'a[data-cy="nav-{}"]'
    nav_household_members = 'a[data-cy="nav-{}"]'
    nav_households = 'a[data-cy="nav-{}"]'
    nav_individuals = 'a[data-cy="nav-{}"]'
    nav_people = 'a[data-cy="nav-People"]'
    nav_programme_management = 'a[data-cy="nav-Programmes"]'
    nav_managerial_console = 'a[data-cy="nav-Managerial Console"]'
    nav_programme_details = 'a[data-cy="nav-Programme Details"]'
    nav_targeting = 'a[data-cy="nav-Targeting"]'
    nav_cash_assist = 'a[data-cy="nav-Cash Assist"]'
    nav_payment_module = 'a[data-cy="nav-Payment Module"]'
    nav_programme_cycles = 'a[data-cy="nav-Programme Cycles"]'
    nav_payment_plans = 'a[data-cy="nav-Payment Plans"]'
    nav_payment_verification = 'a[data-cy="nav-Payment Verification"]'
    nav_grievance = 'a[data-cy="nav-Grievance"]'
    nav_grievance_tickets = 'a[data-cy="nav-Grievance Tickets"]'
    nav_grievance_dashboard = 'a[data-cy="nav-Grievance Dashboard"]'
    nav_feedback = 'a[data-cy="nav-Feedback"]'
    nav_accountability = 'a[data-cy="nav-Accountability"]'
    nav_communication = 'a[data-cy="nav-Communication"]'
    nav_surveys = 'a[data-cy="nav-Surveys"]'
    nav_programme_users = 'a[data-cy="nav-Programme Users"]'
    nav_activity_log = 'a[data-cy="nav-Activity Log"]'
    nav_resources_knowledge_base = 'a[data-cy="nav-resources-Knowledge Base"]'
    nav_resources_conversations = 'a[data-cy="nav-resources-Conversations"]'
    nav_resources_tools_and_materials = 'a[data-cy="nav-resources-Tools and Materials"]'
    nav_resources_release_note = 'a[data-cy="nav-resources-Release Note"]'
    nav_program_log = 'a[data-cy="nav-Programme Log"]'
    main_content = 'div[data-cy="main-content"]'
    drawer_items = 'div[data-cy="drawer-items"]'
    drawer_inactive_subheader = 'div[data-cy="program-inactive-subheader"]'
    menu_item_clear_cache = 'li[data-cy="menu-item-clear-cache"]'
    global_program_filter_search_input = 'input[data-cy="search-input-gpf"]'
    global_program_filter_search_button = 'button[data-cy="search-icon"]'
    global_program_filter_clear_button = 'button[data-cy="clear-icon"]'
    rows = 'tr[role="checkbox"]'
    row_index_template = 'tr[role="checkbox"]:nth-child({})'
    alert = '[role="alert"]'
    breadcrumbs_chevron_icon = 'svg[data-cy="breadcrumbs-chevron-icon"]'
    arrow_back = 'div[data-cy="arrow_back"]'

    # Text
    global_program_filter_text = "All Programmes"

    def navigate_to_page(self, business_area_slug: str, program_slug: str) -> None:
        self.driver.get(self.get_page_url(business_area_slug, program_slug))

    def get_page_url(self, business_area_slug: str, program_slug: str) -> str:
        return f"{self.driver.live_server.url}/{business_area_slug}/programs/{program_slug}"

    def get_main_content(self) -> WebElement:
        return self.wait_for(self.main_content)

    def get_business_area_container(self) -> WebElement:
        return self.wait_for(self.business_area_container)

    def get_global_program_filter_container(self) -> WebElement:
        return self.wait_for(self.global_program_filter_container)

    def get_global_program_filter(self) -> WebElement:
        return self.wait_for(self.global_program_filter)

    def get_menu_user_profile(self) -> WebElement:
        return self.wait_for(self.menu_user_profile)

    def get_side_nav(self) -> WebElement:
        return self.wait_for(self.side_nav)

    def get_nav_country_dashboard(self) -> WebElement:
        return self.wait_for(self.nav_country_dashboard)

    def get_nav_registration_data_import(self) -> WebElement:
        return self.wait_for(self.nav_registration_data_import)

    def get_nav_programme_population(self, name: str = "Main Menu") -> WebElement:
        return self.wait_for(self.nav_programme_population.format(name))

    def get_nav_household_members(self, name: str = "Items") -> WebElement:
        return self.wait_for(self.nav_household_members.format(name))

    def get_nav_households(self, name: str = "Items Groups") -> WebElement:
        return self.wait_for(self.nav_households.format(name))

    def get_nav_individuals(self, name: str = "Items") -> WebElement:
        return self.wait_for(self.nav_individuals.format(name))

    def get_nav_people(self) -> WebElement:
        return self.wait_for(self.nav_people)

    def get_nav_programme_management(self) -> WebElement:
        return self.wait_for(self.nav_programme_management)

    def get_nav_managerial_console(self) -> WebElement:
        return self.wait_for(self.nav_managerial_console)

    def get_nav_programme_details(self) -> WebElement:
        return self.wait_for(self.nav_programme_details)

    def get_nav_targeting(self) -> WebElement:
        return self.wait_for(self.nav_targeting)

    def get_nav_cash_assist(self) -> WebElement:
        return self.wait_for(self.nav_cash_assist)

    def get_nav_payment_module(self) -> WebElement:
        return self.wait_for(self.nav_payment_module)

    def get_nav_payment_plans(self) -> WebElement:
        return self.wait_for(self.nav_payment_plans)

    def get_nav_programme_cycles(self) -> WebElement:
        return self.wait_for(self.nav_programme_cycles)

    def get_nav_payment_verification(self) -> WebElement:
        return self.wait_for(self.nav_payment_verification)

    def get_nav_grievance(self) -> WebElement:
        return self.wait_for(self.nav_grievance)

    def get_nav_grievance_tickets(self) -> WebElement:
        return self.wait_for(self.nav_grievance_tickets)

    def get_nav_grievance_dashboard(self) -> WebElement:
        return self.wait_for(self.nav_grievance_dashboard)

    def get_nav_feedback(self) -> WebElement:
        return self.wait_for(self.nav_feedback)

    def get_nav_accountability(self) -> WebElement:
        return self.wait_for(self.nav_accountability)

    def get_nav_communication(self) -> WebElement:
        return self.wait_for(self.nav_communication)

    def get_nav_surveys(self) -> WebElement:
        return self.wait_for(self.nav_surveys)

    def get_nav_programme_users(self) -> WebElement:
        return self.wait_for(self.nav_programme_users)

    def get_nav_activity_log(self) -> WebElement:
        return self.wait_for(self.nav_activity_log)

    def get_nav_resources_knowledge_base(self) -> WebElement:
        return self.wait_for(self.nav_resources_knowledge_base)

    def get_nav_resources_conversations(self) -> WebElement:
        return self.wait_for(self.nav_resources_conversations)

    def get_nav_resources_tools_and_materials(self) -> WebElement:
        return self.wait_for(self.nav_resources_tools_and_materials)

    def get_nav_resources_release_note(self) -> WebElement:
        return self.wait_for(self.nav_resources_release_note)

    def get_drawer_items(self) -> WebElement:
        return self.wait_for(self.drawer_items)

    def select_global_program_filter(self, name: str) -> None:
        # TODO: remove this one after fix bug with cache
        # self.get_menu_user_profile().click()
        # self.get_menu_item_clear_cache().click()

        self.get_global_program_filter().click()
        self.get_global_program_filter_search_input().clear()
        self.clear_input(self.get_global_program_filter_search_input())
        for _ in range(len(self.get_global_program_filter_search_input().get_attribute("value"))):
            self.get_global_program_filter_search_input().send_keys(Keys.BACKSPACE)
        self.get_global_program_filter_search_button().click()
        if name != "All Programmes":
            self.get_global_program_filter_search_input().send_keys(name)
            self.get_global_program_filter_search_button().click()
            self.wait_for_text_disappear("All Programmes", '[data-cy="select-option-name"]')

        self.select_listbox_element(name)

    def get_drawer_inactive_subheader(self, timeout: int = Common.DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_for(self.drawer_inactive_subheader, timeout=timeout)

    def get_menu_item_clear_cache(self) -> WebElement:
        return self.wait_for(self.menu_item_clear_cache)

    def get_global_program_filter_search_button(self) -> WebElement:
        return self.wait_for(self.global_program_filter_search_button)

    def get_global_program_filter_search_input(self) -> WebElement:
        return self.wait_for(self.global_program_filter_search_input)

    def get_breadcrumbs_chevron_icon(self) -> WebElement:
        return self.wait_for(self.breadcrumbs_chevron_icon)

    def get_arrow_back(self) -> WebElement:
        self.scroll(scroll_by=-600)
        return self.wait_for(self.arrow_back)

    def get_nav_program_log(self) -> WebElement:
        return self.wait_for(self.nav_program_log)

    def wait_for_rows(self) -> [WebElement]:
        self.wait_for(self.rows)
        WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, self.rows)))
        return self.get_elements(self.rows)

    def wait_for_row_with_text(self, index: int, text: str) -> None:
        import time

        timeout = 10
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.01)
            if text in self.wait_for(self.row_index_template.format(index + 1)).text:
                return
        assert text in self.wait_for(self.row_index_.format(index + 1)).text

    def get_rows(self) -> [WebElement]:
        return self.get_elements(self.rows)

    def get_alert(self) -> WebElement:
        return self.wait_for(self.alert)

    def check_alert(self, text: str) -> None:
        self.get_alert()
        for _ in range(300):
            if text in self.get_alert().text:
                break
            sleep(0.1)
        assert text in self.get_alert().text

    def wait_for_number_of_rows(self, number: int) -> bool:
        for _ in range(5):
            if len(self.get_rows()) == number:
                return True
            sleep(1)
        return False

    def clear_input(self, element: WebElement) -> None:
        """
        Clear an input element, cross-platform.
        """
        key = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
        element.click()
        element.send_keys(key, "a")
        element.send_keys(Keys.DELETE)
