from page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

class ProgrammeManagement(BaseComponents):

    buttonNewProgram = 'a[data-cy="button-new-program"]'
    inputProgrammeName = 'input[data-cy="input-name"]'
    inputStartDate = 'input[data-cy="date-input-startDate"]'
    inputEndDate = 'input[data-cy="date-input-endDate"]'
    selectSelector = 'div[data-cy="select-sector"]'
    inputDataCollectingType = 'div[data-cy="input-data-collecting-type"]'
    inputCashPlus = 'span[data-cy="input-cashPlus"]'
    inputDescription = 'textarea[data-cy="input-description"]'
    inputBudget = 'input[data-cy="input-budget"]'
    inputAdministrativeAreasOfImplementation = 'input[data-cy="input-administrativeAreasOfImplementation"]'
    inputPopulation = 'input[data-cy="input-populationGoal"]'
    inputFreqOfPaymentOneOff = '//*[@data-cy="input-frequency-of-payment"]/div[1]/div/span/span[1]'
    inputFreqOfPaymentRegular = '//*[@data-cy="input-frequency-of-payment"]/div[2]/div/span/span[1]'
    buttonNext = 'button[data-cy="button-next"]'
    buttonSave = 'button[data-cy="button-save"]'
    buttonAddPartner = 'button[data-cy="button-add-partner"]'
    inputPartner = 'div[data-cy="select-partners[0].id"]'
    buttonDelete = 'button[data-cy="button-delete"]'
    selectOption = 'li[data-cy="select-option-undefined"]'

    filtersSearch = '//*[@data-cy="filters-search"]/div/input'
    buttonApply = 'button[data-cy="button-filters-clear"]'

    def getRowByProgramName(self, programName):
        locator = f'tr[data-cy="table-row-{programName}"]'
        self.wait_for(locator)
        return self.get_elements(locator)[0].text.split("\n")

    def getButtonAddPartner(self):
        return self.wait_for(self.buttonAddPartner)

    def choosePartnerOption(self, optionName):
        # Todo: Change undefined to name of Partner
        selectOption = f'li[data-cy="select-option-undefined"]'
        self.wait_for(self.inputPartner).click()
        self.wait_for(selectOption).click()
        self.wait_for_disappear(selectOption)

    def getInputProgrammeName(self):
        return self.wait_for(self.inputProgrammeName)

    def getInputCashPlus(self):
        return self.wait_for(self.inputCashPlus)

    def getInputFreqOfPaymentOneOff(self):
        return self.wait_for(self.inputFreqOfPaymentOneOff, By.XPATH)

    def getInputFreqOfPaymentRegular(self):
        return self.wait_for(self.inputFreqOfPaymentRegular, By.XPATH)

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
        # ToDo: Delete sleep
        sleep(1)
        self.wait_for(self.filtersSearch, By.XPATH).send_keys(Keys.ENTER)

    def getButtonApply(self):
        return self.wait_for(self.buttonApply)

    def getInputDescription(self):
        return self.wait_for(self.inputDescription)

    def getInputBudget(self):
        return self.wait_for(self.inputBudget)

    def getInputAdministrativeAreasOfImplementation(self):
        return self.wait_for(self.inputAdministrativeAreasOfImplementation)

    def getInputPopulation(self):
        return self.wait_for(self.inputPopulation)

