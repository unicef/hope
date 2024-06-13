from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class NewPaymentPlan(BaseComponents):

    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonSavePaymentPlan = 'button[data-cy="button-save-payment-plan"]'
    inputTargetPopulation = 'div[data-cy="input-target-population"]'
    selectTargetingid = 'div[data-cy="select-targetingId"]'
    inputStartDate = 'div[data-cy="input-start-date"]'
    inputEndDate = 'div[data-cy="input-end-date"]'
    inputCurrency = 'div[data-cy="input-currency"]'
    inputDispersionStartDate = 'div[data-cy="input-dispersion-start-date"]'
    inputDispersionEndDate = 'div[data-cy="input-dispersion-end-date"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonSavePaymentPlan(self) -> WebElement:
        return self.wait_for(self.buttonSavePaymentPlan)

    def getInputTargetPopulation(self) -> WebElement:
        return self.wait_for(self.inputTargetPopulation)

    def getSelectTargetingid(self) -> WebElement:
        return self.wait_for(self.selectTargetingid)

    def getInputStartDate(self) -> WebElement:
        return self.wait_for(self.inputStartDate)

    def getInputEndDate(self) -> WebElement:
        return self.wait_for(self.inputEndDate)

    def getInputCurrency(self) -> WebElement:
        return self.wait_for(self.inputCurrency)

    def getInputDispersionStartDate(self) -> WebElement:
        return self.wait_for(self.inputDispersionStartDate)

    def getInputDispersionEndDate(self) -> WebElement:
        return self.wait_for(self.inputDispersionEndDate)
