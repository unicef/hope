from helpers.helper import Common
from selenium.webdriver.remote.webelement import WebElement


class Filters(Common):
    filtersSearch = 'div[data-cy="filters-search"]'
    filtersStatus = 'div[data-cy="filters-status"]'
    filtersSector = 'div[data-cy="filters-sector"]'
    filtersNumberOfHouseholdsMin = 'div[data-cy="filters-number-of-households-min"]'
    filtersNumberOfHouseholdsMax = 'div[data-cy="filters-number-of-households-max"]'
    filtersBudgetMin = 'div[data-cy="filters-budget-min"]'
    filtersBudgetMax = 'div[data-cy="filters-budget-max"]'
    filtersDataCollectingType = 'div[data-cy="filters-data-collecting-type"]'
    filtersProgram = 'div[data-cy="filters-program"]'
    filtersDocumentType = 'div[data-cy="filters-document-type"]'
    filtersDocumentNumber = 'div[data-cy="filters-document-number"]'
    filtersFsp = 'div[data-cy="filters-fsp"]'
    filtersCategory = 'div[data-cy="filters-category"]'
    filtersAdminLevel = 'div[data-cy="filters-admin-level"]'
    filtersAssignee = 'div[data-cy="filters-assignee"]'
    filtersCreatedByAutocomplete = 'div[data-cy="filters-created-by-autocomplete"]'
    filtersRegistrationDataImport = 'div[data-cy="filters-registration-data-import"]'
    filtersPreferredLanguage = 'div[data-cy="filters-preferred-language"]'
    filtersPriority = 'div[data-cy="filters-priority"]'
    filtersUrgency = 'div[data-cy="filters-urgency"]'
    filtersActiveTickets = 'div[data-cy="filters-active-tickets"]'
    filtersProgramState = 'div[data-cy="filters-program-state"]'
    filtersResidenceStatus = 'div[data-cy="filters-residence-status"]'
    hhFiltersSearch = 'div[data-cy="hh-filters-search"]'
    hhFiltersResidenceStatus = 'div[data-cy="hh-filters-residence-status"]'
    hhFiltersAdmin2 = 'div[data-cy="hh-filters-admin2"]'
    hhFiltersHouseholdSizeFrom = 'div[data-cy="hh-filters-household-size-from"]'
    hhFiltersHouseholdSizeTo = 'div[data-cy="hh-filters-household-size-to"]'
    hhFiltersOrderBy = 'div[data-cy="hh-filters-order-by"]'
    hhFiltersStatus = 'div[data-cy="hh-filters-status"]'
    menuItemFiltersText = 'div[data-cy="menu-item-filters-text"]'
    filtersTotalHouseholdsCountMin = 'div[data-cy="filters-total-households-count-min"]'
    filtersTotalHouseholdsCountMax = 'div[data-cy="filters-total-households-count-max"]'
    globalProgramFilterContainer = 'div[data-cy="global-program-filter-container"]'
    filterSearch = 'div[data-cy="filter-search"]'
    filterStatus = 'div[data-cy="filter-status"]'
    filterSizeMin = 'div[data-cy="filter-size-min"]'
    filterSizeMax = 'div[data-cy="filter-size-max"]'

    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'

    def getFiltersSearch(self) -> WebElement:
        return self.wait_for(self.filtersSearch)

    def getFiltersDocumentType(self) -> WebElement:
        return self.wait_for(self.filtersDocumentType)

    def getFiltersDocumentNumber(self) -> WebElement:
        return self.wait_for(self.filtersDocumentNumber)

    def getFiltersProgram(self) -> WebElement:
        return self.wait_for(self.filtersProgram)

    def getFiltersStatus(self) -> WebElement:
        return self.wait_for(self.filtersStatus)

    def getFiltersFsp(self) -> WebElement:
        return self.wait_for(self.filtersFsp)

    def getFiltersCategory(self) -> WebElement:
        return self.wait_for(self.filtersCategory)

    def getFiltersAdminLevel(self) -> WebElement:
        return self.wait_for(self.filtersAdminLevel)

    def getFiltersAssignee(self) -> WebElement:
        return self.wait_for(self.filtersAssignee)

    def getFiltersCreatedByAutocomplete(self) -> WebElement:
        return self.wait_for(self.filtersCreatedByAutocomplete)

    def getFiltersRegistrationDataImport(self) -> WebElement:
        return self.wait_for(self.filtersRegistrationDataImport)

    def getFiltersPreferredLanguage(self) -> WebElement:
        return self.wait_for(self.filtersPreferredLanguage)

    def getFiltersPriority(self) -> WebElement:
        return self.wait_for(self.filtersPriority)

    def getFiltersUrgency(self) -> WebElement:
        return self.wait_for(self.filtersUrgency)

    def getFiltersActiveTickets(self) -> WebElement:
        return self.wait_for(self.filtersActiveTickets)

    def getFiltersProgramState(self) -> WebElement:
        return self.wait_for(self.filtersProgramState)

    def getFiltersSector(self) -> WebElement:
        return self.wait_for(self.filtersSector)

    def getFiltersNumberOfHouseholdsMin(self) -> WebElement:
        return self.wait_for(self.filtersNumberOfHouseholdsMin)

    def getFiltersNumberOfHouseholdsMax(self) -> WebElement:
        return self.wait_for(self.filtersNumberOfHouseholdsMax)

    def getFiltersBudgetMin(self) -> WebElement:
        return self.wait_for(self.filtersBudgetMin)

    def getFiltersBudgetMax(self) -> WebElement:
        return self.wait_for(self.filtersBudgetMax)

    def getFiltersDataCollectingType(self) -> WebElement:
        return self.wait_for(self.filtersDataCollectingType)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getFiltersResidenceStatus(self) -> WebElement:
        return self.wait_for(self.filtersResidenceStatus)

    def getHhFiltersSearch(self) -> WebElement:
        return self.wait_for(self.hhFiltersSearch)

    def getHhFiltersResidenceStatus(self) -> WebElement:
        return self.wait_for(self.hhFiltersResidenceStatus)

    def getHhFiltersAdmin2(self) -> WebElement:
        return self.wait_for(self.hhFiltersAdmin2)

    def getHhFiltersHouseholdSizeFrom(self) -> WebElement:
        return self.wait_for(self.hhFiltersHouseholdSizeFrom)

    def getHhFiltersHouseholdSizeTo(self) -> WebElement:
        return self.wait_for(self.hhFiltersHouseholdSizeTo)

    def getHhFiltersOrderBy(self) -> WebElement:
        return self.wait_for(self.hhFiltersOrderBy)

    def getHhFiltersStatus(self) -> WebElement:
        return self.wait_for(self.hhFiltersStatus)

    def getMenuItemFiltersText(self) -> WebElement:
        return self.wait_for(self.menuItemFiltersText)

    def getFiltersTotalHouseholdsCountMin(self) -> WebElement:
        return self.wait_for(self.filtersTotalHouseholdsCountMin)

    def getFiltersTotalHouseholdsCountMax(self) -> WebElement:
        return self.wait_for(self.filtersTotalHouseholdsCountMax)

    def getGlobalProgramFilterContainer(self) -> WebElement:
        return self.wait_for(self.globalProgramFilterContainer)

    def getFilterSearch(self) -> WebElement:
        return self.wait_for(self.filterSearch)

    def getFilterStatus(self) -> WebElement:
        return self.wait_for(self.filterStatus)

    def getFilterSizeMin(self) -> WebElement:
        return self.wait_for(self.filterSizeMin)

    def getFilterSizeMax(self) -> WebElement:
        return self.wait_for(self.filterSizeMax)
