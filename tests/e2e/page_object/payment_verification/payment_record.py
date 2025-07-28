from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentRecord(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonEdPlan = 'button[data-cy="button-ed-plan"]'
    labelStatus = 'div[data-cy="label-STATUS"]'
    statusContainer = 'div[data-cy="status-container"]'
    labelHousehold = 'div[data-cy="label-Items Group ID"]'
    labelTargetPopulation = 'div[data-cy="label-TARGET POPULATION"]'
    labelDistributionModality = 'div[data-cy="label-DISTRIBUTION MODALITY"]'
    labelAmountReceived = 'div[data-cy="label-AMOUNT RECEIVED"]'
    labelHouseholdId = 'div[data-cy="label-Items Group ID"]'
    labelHeadOfHousehold = 'div[data-cy="label-HEAD OF Items Group"]'
    labelTotalPersonCovered = 'div[data-cy="label-TOTAL PERSON COVERED"]'
    labelPhoneNumber = 'div[data-cy="label-PHONE NUMBER"]'
    labelAltPhoneNumber = 'div[data-cy="label-ALT. PHONE NUMBER"]'
    labelEntitlementQuantity = 'div[data-cy="label-ENTITLEMENT QUANTITY"]'
    labelDeliveredQuantity = 'div[data-cy="label-DELIVERED QUANTITY"]'
    labelCurrency = 'div[data-cy="label-CURRENCY"]'
    labelDeliveryType = 'div[data-cy="label-DELIVERY TYPE"]'
    labelDeliveryDate = 'div[data-cy="label-DELIVERY DATE"]'
    labelEntitlementCardId = 'div[data-cy="label-ENTITLEMENT CARD ID"]'
    labelTransactionReferenceId = 'div[data-cy="label-TRANSACTION REFERENCE ID"]'
    labelEntitlementCardIssueDate = 'div[data-cy="label-ENTITLEMENT CARD ISSUE DATE"]'
    labelFsp = 'div[data-cy="label-FSP"]'
    buttonSubmit = 'button[data-cy="button-submit"]'
    inputReceivedamount = 'input[data-cy="input-receivedAmount"]'
    choiceNotReceived = '[data-cy="choice-not-received"]'

    def getInputReceivedamount(self) -> WebElement:
        return self.wait_for(self.inputReceivedamount)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonEdPlan(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-200)
            """
        )
        return self.wait_for(self.buttonEdPlan)

    def getLabelStatus(self) -> [WebElement]:
        return self.get_elements(self.labelStatus)

    def getStatus(self) -> [WebElement]:
        self.wait_for(self.statusContainer)
        return self.get_elements(self.statusContainer)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def waitForStatusContainer(self, status: str, timeout: int = 20) -> []:
        return self.wait_for_text(status, self.statusContainer, timeout=timeout)

    def getLabelHousehold(self) -> WebElement:
        return self.wait_for(self.labelHousehold)

    def getLabelTargetPopulation(self) -> WebElement:
        return self.wait_for(self.labelTargetPopulation)

    def getLabelDistributionModality(self) -> WebElement:
        return self.wait_for(self.labelDistributionModality)

    def getLabelAmountReceived(self) -> WebElement:
        return self.wait_for(self.labelAmountReceived)

    def getLabelHouseholdId(self) -> WebElement:
        return self.wait_for(self.labelHouseholdId)

    def getLabelHeadOfHousehold(self) -> WebElement:
        return self.wait_for(self.labelHeadOfHousehold)

    def getLabelTotalPersonCovered(self) -> WebElement:
        return self.wait_for(self.labelTotalPersonCovered)

    def getLabelPhoneNumber(self) -> WebElement:
        return self.wait_for(self.labelPhoneNumber)

    def getLabelAltPhoneNumber(self) -> WebElement:
        return self.wait_for(self.labelAltPhoneNumber)

    def getLabelEntitlementQuantity(self) -> WebElement:
        return self.wait_for(self.labelEntitlementQuantity)

    def getLabelDeliveredQuantity(self) -> WebElement:
        return self.wait_for(self.labelDeliveredQuantity)

    def getLabelCurrency(self) -> WebElement:
        return self.wait_for(self.labelCurrency)

    def getLabelDeliveryType(self) -> WebElement:
        return self.wait_for(self.labelDeliveryType)

    def getLabelDeliveryDate(self) -> WebElement:
        return self.wait_for(self.labelDeliveryDate)

    def getLabelEntitlementCardId(self) -> WebElement:
        return self.wait_for(self.labelEntitlementCardId)

    def getLabelTransactionReferenceId(self) -> WebElement:
        return self.wait_for(self.labelTransactionReferenceId)

    def getLabelEntitlementCardIssueDate(self) -> WebElement:
        return self.wait_for(self.labelEntitlementCardIssueDate)

    def getLabelFsp(self) -> WebElement:
        return self.wait_for(self.labelFsp)

    def getButtonSubmit(self) -> WebElement:
        return self.wait_for(self.buttonSubmit)

    def getChoiceNotReceived(self) -> WebElement:
        return self.wait_for(self.choiceNotReceived)
