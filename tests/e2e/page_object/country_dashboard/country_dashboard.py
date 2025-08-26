from time import sleep
from typing import List

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait


class CountryDashboard(BaseComponents):
    nav_resources_release_note = 'a[data-cy="nav-resources-Release Note"]'
    main_content = 'div[data-cy="main-content"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    iframe_locator = 'iframe[title="Dashboard"]'
    total_amount_paid = "div#total-amount-paid"
    total_amount_paid_local = "div#total-amount-paid-local"
    number_of_payments = "div#number-of-payments"
    outstanding_payments = "div#outstanding-payments"
    households_reached = "div#households-reached"
    pwd_reached = "div#pwd-reached"
    children_reached = "div#children-reached"
    individuals_reached = "div#individuals-reached"
    spinner_selector = ".spinner-border"
    reconciliation_percentage = "div.reconciliation-percentage"
    pending_reconciliation_percentage = "div.pending-reconciliation-percentage"

    def switch_to_dashboard_iframe(self) -> None:
        retries = 3
        for _ in range(retries):
            try:
                iframe = WebDriverWait(self.driver, 30).until(
                    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="Dashboard"]'))
                )
                self.driver.switch_to.frame(iframe)
                return
            except TimeoutException:
                pass
            sleep(2)
        raise NoSuchElementException("Could not locate iframe with title 'Dashboard' after multiple attempts.")

    def switch_to_default_content(self) -> None:
        self.driver.switch_to.default_content()

    def get_nav_resources_release_note(self) -> WebElement:
        return self.wait_for(self.nav_resources_release_note)

    def get_main_content(self) -> WebElement:
        return self.wait_for(self.main_content)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_total_amount_paid(self) -> WebElement:
        return self.wait_for(self.total_amount_paid)

    def get_total_amount_paid_local(self) -> WebElement:
        return self.wait_for(self.total_amount_paid_local)

    def get_number_of_payments(self) -> WebElement:
        return self.wait_for(self.number_of_payments)

    def get_outstanding_payments(self) -> WebElement:
        return self.wait_for(self.outstanding_payments)

    def get_households_reached(self) -> WebElement:
        return self.wait_for(self.households_reached)

    def get_pwd_reached(self) -> WebElement:
        return self.wait_for(self.pwd_reached)

    def get_children_reached(self) -> WebElement:
        return self.wait_for(self.children_reached)

    def get_table_label(self) -> [WebElement]:
        self.wait_for(self.table_label)
        return self.get_elements(self.table_label)

    def get_individuals_reached(self) -> WebElement:
        return self.wait_for(self.individuals_reached)

    def get_reconciliation_percentage(self) -> WebElement:
        return self.wait_for(self.reconciliation_percentage)

    def get_pending_reconciliation_percentage(self) -> WebElement:
        return self.wait_for(self.pending_reconciliation_percentage)

    def get_spinner_elements(self) -> List[WebElement]:
        return self.get_elements(self.spinner_selector)
