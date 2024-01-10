from base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class ProgrammeManagement(BaseComponents):

    buttonNewProgram = 'a[data-cy="button-new-program"]'
    inputProgrammeName = 'input[data-cy="input-name"]'
    inputStartDate = 'input[data-cy="date-input-startDate"]'
    inputEndDate = 'input[data-cy="date-input-endDate"]'
    selectSelector = 'div[data-cy="select-sector"]'
    inputDataCollectingType = 'div[data-cy="input-data-collecting-type"]'
    inputFreqOfPaymentOneOff = '//*[@data-cy="input-frequency-of-payment"]/div[1]/div/span/span[1]/input'
    inputFreqOfPaymentRegular = '//*[@data-cy="input-frequency-of-payment"]/div[2]/div/span/span[1]/input'
    buttonNext = 'button[data-cy="button-next"]'
    buttonSave = 'button[data-cy="button-save"]'

    filtersSearch = '//*[@data-cy="filters-search"]/div/input'
    buttonApply = 'button[data-cy="button-filters-clear"]'

    def getInputProgrammeName(self):
        return self.wait_for(self.inputProgrammeName)

    def getInputFreqOfPaymentOneOff(self):
        return self.wait_for(self.inputFreqOfPaymentOneOff, By.XPATH)

    def getInputStartDate(self):
        return self.wait_for(self.inputStartDate)

    def getInputEndDate(self):
        return self.wait_for(self.inputEndDate)

    def getButtonNext(self):
        return self.wait_for(self.buttonNext)

    def getButtonSave(self):
        return self.wait_for(self.buttonSave)

    def chooseOptionSelector(self, optionName):
        selectOption = f'li[data-cy="select-option-{optionName}"]'
        self.wait_for(self.selectSelector).click()
        self.wait_for(selectOption).click()
        self.wait_for_disappear(selectOption)

    def chooseOptionDataCollectingType(self, optionName):
        selectOption = f'li[data-cy="select-option-{optionName}"]'
        self.wait_for(self.inputDataCollectingType).click()
        self.wait_for(selectOption).click()
        self.wait_for_disappear(selectOption)

    def getButtonNewProgram(self):
        return self.wait_for(self.buttonNewProgram)

    def fillFiltersSearch(self, filterText):
        self.wait_for(self.filtersSearch, By.XPATH).send_keys(filterText)
        self.wait_for(self.filtersSearch, By.XPATH).send_keys(Keys.ENTER)

    def getButtonApply(self):
        return self.wait_for(self.buttonApply)


