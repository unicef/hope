from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class NewPaymentPlan(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_save_payment_plan = 'button[data-cy="button-save-payment-plan"]'
    input_target_population = 'div[data-cy="input-target-population"]'
    select_targeting_id = 'div[data-cy="select-targetingId"]'
    input_start_date = 'div[data-cy="input-start-date"]'
    input_start_date_error = 'div[data-cy="input-dispersion-start-date"]'
    input_end_date = 'div[data-cy="input-end-date"]'
    input_end_date_error = 'div[data-cy="input-dispersion-end-date"]'
    input_currency = 'div[data-cy="input-currency"]'
    input_dispersion_start_date = 'div[data-cy="input-dispersion-start-date"]'
    input_dispersion_end_date = 'div[data-cy="input-dispersion-end-date"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_save_payment_plan(self) -> WebElement:
        return self.wait_for(self.button_save_payment_plan)

    def get_input_target_population(self) -> WebElement:
        return self.wait_for(self.input_target_population)

    def get_select_targeting_id(self) -> WebElement:
        return self.wait_for(self.select_targeting_id)

    def get_input_start_date(self) -> WebElement:
        self.wait_for(self.input_start_date)
        return self.wait_for(self.input_start_date).find_elements(By.TAG_NAME, "input")[0]

    def get_input_end_date(self) -> WebElement:
        self.wait_for(self.input_end_date)
        return self.wait_for(self.input_end_date).find_elements(By.TAG_NAME, "input")[0]

    def get_input_start_date_error(self) -> WebElement:
        return self.wait_for(self.input_start_date_error)

    def get_input_end_date_error(self) -> WebElement:
        return self.wait_for(self.input_end_date_error)

    def get_input_currency(self) -> WebElement:
        return self.wait_for(self.input_currency)

    def get_input_dispersion_start_date(self) -> WebElement:
        return self.wait_for(self.input_dispersion_start_date).find_elements(By.TAG_NAME, "input")[0]

    def get_input_dispersion_end_date(self) -> WebElement:
        return self.wait_for(self.input_dispersion_end_date).find_elements(By.TAG_NAME, "input")[0]
