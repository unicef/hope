from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class NewPaymentPlan(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonSavePaymentPlan = 'button[data-cy="button-save-payment-plan"]'
    inputTargetPopulation = 'div[data-cy="input-target-population"]'
    selectTargetingID = 'div[data-cy="select-targetingId"]'
    datePickerFilter = 'div[data-cy="date-picker-filter"]'
    inputCurrency = 'div[data-cy="input-currency"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonSavePaymentPlan(self) -> WebElement:
        return self.wait_for(self.buttonSavePaymentPlan)

    def getInputTargetPopulation(self) -> WebElement:
        return self.wait_for(self.inputTargetPopulation)

    def getSelectTargetingID(self) -> WebElement:
        return self.wait_for(self.selectTargetingID)

    def getDatePickerFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter)

    def getInputCurrency(self) -> WebElement:
        return self.wait_for(self.inputCurrency)
