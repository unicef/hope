from selenium.webdriver.common.by import By

from helpers.hope import HOPE

class ProgrammeManagement(object):

    buttonNewProgram = 'a[data-cy="button-new-program"]'
    inputProgrammeName = 'input[data-cy="input-name"]'
    inputStartDate = 'input[data-cy="date-input-startDate"]'
    inputEndDate = 'input[data-cy="date-input-endDate"]'
    selectSelector = 'div[data-cy="select-sector"]'
#     optionChildProtection = 'li[data-cy="select-option-Child Protection"]'
    inputDataCollectingType = 'div[data-cy="input-data-collecting-type"]'
    optionFull = 'li[data-cy="select-option-Full"]'
    buttonNext = 'button[data-cy="button-next"]'
    buttonSave = 'button[data-cy="button-save"]'
    def optionChildProtection(optionName):
        return f'li[data-cy="select-option-{optionName}"]'


#     pageHeaderTitle = 'h5[data-cy="page-header-title"]'
#     dialogTitle = '[data-cy="page-header-title"]'
#     inputProgrammeName = 'div[data-cy="input-programme-name"]'
#     inputCashAssistScope = 'div[data-cy="input-cash-assist-scope"]'
#     selectOptionUnicef = 'li[data-cy="select-option-Unicef"]'
#     selectOptionForPartners = 'li[data-cy="select-option-For partners"]'
#     inputSector = 'div[data-cy="input-sector"]'
#     selectOptionX = 'li[data-cy="select-option-'
#     inputStartDate = 'div[data-cy="input-start-date"]'
#     inputEndDate = 'div[data-cy="input-end-date"]'
#     inputDescription = 'div[data-cy="input-description"]'
#     inputBudget = 'input[data-cy="input-budget"]'
#     inputAdminArea = 'div[data-cy="input-admin-area"]'
#     inputPopulationGoal = 'div[data-cy="input-population-goal"]'
#     statusFilter = 'div[data-cy="filters-status"]'
#     option = ' li[role = "option"]'
#     buttonApply = 'button[data-cy="button-filters-apply"]'
#     statusContainer = 'div[data-cy="status-container"]'
#     tableRowX = 'tr[data-cy="table-row-'
#     inputFrequencyOfPayment = 'div[data-cy="input-frequency-of-payment"]'
#     inputCashPlus = 'span[data-cy="input-cashPlus"]'
#     inputIndividualDataNeeded = 'div[data-cy="input-individual-data-needed"]'
#     selectDataCollectingTypeCode = 'input[data-cy="select-dataCollectingTypeCode"]'