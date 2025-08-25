from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentRecord(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_ed_plan = 'button[data-cy="button-ed-plan"]'
    label_status = 'div[data-cy="label-STATUS"]'
    status_container = 'div[data-cy="status-container"]'
    label_household = 'div[data-cy="label-Items Group ID"]'
    label_target_population = 'div[data-cy="label-TARGET POPULATION"]'
    label_distribution_modality = 'div[data-cy="label-DISTRIBUTION MODALITY"]'
    label_amount_received = 'div[data-cy="label-AMOUNT RECEIVED"]'
    label_household_id = 'div[data-cy="label-Items Group ID"]'
    label_head_of_household = 'div[data-cy="label-HEAD OF Items Group"]'
    label_total_person_covered = 'div[data-cy="label-TOTAL PERSON COVERED"]'
    label_phone_number = 'div[data-cy="label-PHONE NUMBER"]'
    label_alt_phone_number = 'div[data-cy="label-ALT. PHONE NUMBER"]'
    label_entitlement_quantity = 'div[data-cy="label-ENTITLEMENT QUANTITY"]'
    label_delivered_quantity = 'div[data-cy="label-DELIVERED QUANTITY"]'
    label_currency = 'div[data-cy="label-CURRENCY"]'
    label_delivery_type = 'div[data-cy="label-DELIVERY TYPE"]'
    label_delivery_date = 'div[data-cy="label-DELIVERY DATE"]'
    label_entitlement_card_id = 'div[data-cy="label-ENTITLEMENT CARD ID"]'
    label_transaction_reference_id = 'div[data-cy="label-TRANSACTION REFERENCE ID"]'
    label_entitlement_card_issue_date = 'div[data-cy="label-ENTITLEMENT CARD ISSUE DATE"]'
    label_fsp = 'div[data-cy="label-FSP"]'
    button_submit = 'button[data-cy="button-submit"]'
    input_received_amount = 'input[data-cy="input-receivedAmount"]'
    choice_not_received = '[data-cy="choice-not-received"]'

    def get_input_received_amount(self) -> WebElement:
        return self.wait_for(self.input_received_amount)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_ed_plan(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-200)
            """
        )
        return self.wait_for(self.button_ed_plan)

    def get_label_status(self) -> [WebElement]:
        return self.get_elements(self.label_status)

    def get_status(self) -> [WebElement]:
        self.wait_for(self.status_container)
        return self.get_elements(self.status_container)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def wait_for_status_container(self, status: str, timeout: int = 20) -> []:
        return self.wait_for_text_to_be_exact(status, self.status_container, timeout=timeout)

    def get_label_household(self) -> WebElement:
        return self.wait_for(self.label_household)

    def get_label_target_population(self) -> WebElement:
        return self.wait_for(self.label_target_population)

    def get_label_distribution_modality(self) -> WebElement:
        return self.wait_for(self.label_distribution_modality)

    def get_label_amount_received(self) -> WebElement:
        return self.wait_for(self.label_amount_received)

    def get_label_household_id(self) -> WebElement:
        return self.wait_for(self.label_household_id)

    def get_label_head_of_household(self) -> WebElement:
        return self.wait_for(self.label_head_of_household)

    def get_label_total_person_covered(self) -> WebElement:
        return self.wait_for(self.label_total_person_covered)

    def get_label_phone_number(self) -> WebElement:
        return self.wait_for(self.label_phone_number)

    def get_label_alt_phone_number(self) -> WebElement:
        return self.wait_for(self.label_alt_phone_number)

    def get_label_entitlement_quantity(self) -> WebElement:
        return self.wait_for(self.label_entitlement_quantity)

    def get_label_delivered_quantity(self) -> WebElement:
        return self.wait_for(self.label_delivered_quantity)

    def get_label_currency(self) -> WebElement:
        return self.wait_for(self.label_currency)

    def get_label_delivery_type(self) -> WebElement:
        return self.wait_for(self.label_delivery_type)

    def get_label_delivery_date(self) -> WebElement:
        return self.wait_for(self.label_delivery_date)

    def get_label_entitlement_card_id(self) -> WebElement:
        return self.wait_for(self.label_entitlement_card_id)

    def get_label_transaction_reference_id(self) -> WebElement:
        return self.wait_for(self.label_transaction_reference_id)

    def get_label_entitlement_card_issue_date(self) -> WebElement:
        return self.wait_for(self.label_entitlement_card_issue_date)

    def get_label_fsp(self) -> WebElement:
        return self.wait_for(self.label_fsp)

    def get_button_submit(self) -> WebElement:
        return self.wait_for(self.button_submit)

    def get_choice_not_received(self) -> WebElement:
        return self.wait_for(self.choice_not_received)
