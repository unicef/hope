from time import sleep
from typing import List

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CountryDashboard(BaseComponents):
    navResourcesReleaseNote = 'a[data-cy="nav-resources-Release Note"]'
    mainContent = 'div[data-cy="main-content"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
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
        for attempt in range(retries):
            try:
                iframe = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="Dashboard"]'))
                )
                self.driver.switch_to.frame(iframe)
                return
            except TimeoutException:
                print(f"Attempt {attempt + 1} - Could not locate iframe 'Dashboard'. Checking all iframes on page.")
            sleep(2)
        raise NoSuchElementException("Could not locate iframe with title 'Dashboard' after multiple attempts.")

    def switch_to_default_content(self) -> None:
        self.driver.switch_to.default_content()

    def get_nav_resources_release_note(self) -> WebElement:
        return self.wait_for(self.navResourcesReleaseNote)

    def get_main_content(self) -> WebElement:
        return self.wait_for(self.mainContent)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

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

    def getTableLabel(self) -> [WebElement]:
        self.wait_for(self.tableLabel)
        return self.get_elements(self.tableLabel)

    def get_individuals_reached(self) -> WebElement:
        return self.wait_for(self.individuals_reached)

    def get_reconciliation_percentage(self) -> WebElement:
        return self.wait_for(self.reconciliation_percentage)

    def get_pending_reconciliation_percentage(self) -> WebElement:
        return self.wait_for(self.pending_reconciliation_percentage)

    def get_spinner_elements(self) -> List[WebElement]:
        return self.get_elements(self.spinner_selector)
