from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class NewPaymentPlan(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonSavePaymentPlan = 'button[data-cy="button-save-payment-plan"]'
    inputTargetPopulation = 'div[data-cy="input-target-population"]'
    selectTargetingid = 'div[data-cy="select-targetingId"]'
    inputStartDate = 'div[data-cy="input-start-date"]'
    inputStartDateError = 'div[data-cy="input-dispersion-start-date"]'
    inputEndDate = 'div[data-cy="input-end-date"]'
    inputEndDateError = 'div[data-cy="input-dispersion-end-date"]'
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
        self.wait_for(self.inputStartDate)
        return self.wait_for(self.inputStartDate).find_elements(By.TAG_NAME, "input")[0]

    def getInputEndDate(self) -> WebElement:
        self.wait_for(self.inputEndDate)
        return self.wait_for(self.inputEndDate).find_elements(By.TAG_NAME, "input")[0]

    def getInputStartDateError(self) -> WebElement:
        return self.wait_for(self.inputStartDateError)

    def getInputEndDateError(self) -> WebElement:
        return self.wait_for(self.inputEndDateError)

    def getInputCurrency(self) -> WebElement:
        return self.wait_for(self.inputCurrency)

    def getInputDispersionStartDate(self) -> WebElement:
        return self.wait_for(self.inputDispersionStartDate).find_elements(By.TAG_NAME, "input")[0]

    def getInputDispersionEndDate(self) -> WebElement:
        return self.wait_for(self.inputDispersionEndDate).find_elements(By.TAG_NAME, "input")[0]
