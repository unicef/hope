from time import sleep

from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Filters(BaseComponents):
    filtersSearch = 'div[data-cy="filters-search"]'
    searchTextField = 'div[data-cy="search-text-field"]'
    indFiltersSearch = 'div[data-cy="ind-filters-search"]'
    indFiltersGender = 'div[data-cy="ind-filters-gender"]'
    indFiltersAgeFrom = 'div[data-cy="ind-filters-age-from"]'
    indFiltersAgeTo = 'div[data-cy="ind-filters-age-to"]'
    indFiltersFlags = 'div[data-cy="ind-filters-flags"]'
    indFiltersOrderBy = 'div[data-cy="ind-filters-order-by"]'
    indFiltersStatus = 'div[data-cy="ind-filters-status"]'
    indFiltersRegDateFrom = 'div[data-cy="ind-filters-reg-date-from"]'
    indFiltersRegDateTo = 'div[data-cy="ind-filters-reg-date-to"]'
    datePickerFilterFrom = 'div[data-cy="date-picker-filter-From"]'
    datePickerFilterTo = 'div[data-cy="date-picker-filter-To"]'
    filterFsp = 'div[data-cy="filter-fsp"]'
    filterModality = 'div[data-cy="filter-Modality"]'
    filtersStatus = 'div[data-cy="filters-status"]'
    filtersSector = 'div[data-cy="filters-sector"]'
    dataPickerFilter = 'div[data-cy="date-picker-filter"]'
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
    filtersAdminLevel = 'div[data-cy="filters-admin-level-2"]'
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
    globalProgramFilter = 'button[data-cy="global-program-filter"]'
    reportTypeFilter = 'div[data-cy="report-type-filter"]'
    reportCreatedFromFilter = 'div[data-cy="report-created-from-filter"]'
    reportCreatedToFilter = 'div[data-cy="report-created-to-filter"]'
    reportStatusFilter = 'div[data-cy="report-status-filter"]'
    reportOnlyMyFilter = 'span[data-cy="report-only-my-filter"]'
    programmeInput = 'div[data-cy="Programme-input"]'
    filtersCreationDateFrom = 'div[data-cy="filters-creation-date-from"]'
    filtersCreationDateTo = 'div[data-cy="filters-creation-date-to"]'
    userInput = 'div[data-cy="User-input"]'
    selectFilter = 'div[data-cy="select-filter"]'
    filtersEndDate = 'div[data-cy="filters-end-date"]'
    filtersStartDate = 'div[data-cy="filters-start-date"]'
    filterEndDate = 'div[data-cy="filter-end-date"]'
    filterStartDate = 'div[data-cy="filter-start-date"]'
    assignedToInput = 'div[data-cy="Assigned To-input"]'
    filtersIssueType = 'div[data-cy="filters-issue-type"]'
    filterImportDateRangeMin = 'div[data-cy="filter-import-date-range-min"]'
    filterImportDateRangeMax = 'div[data-cy="filter-import-date-range-max"]'
    filtersTargetPopulationAutocomplete = 'div[data-cy="filters-target-population-autocomplete"]'
    targetPopulationInput = 'div[data-cy="Target Population-input"]'
    createdByInput = 'div[data-cy="Created by-input"]'
    filtersTotalEntitledQuantityFrom = 'div[data-cy="date-picker-filter-From"]'
    filtersTotalEntitledQuantityTo = 'div[data-cy="date-picker-filter-To"]'

    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    importedByInput = 'div[data-cy="Imported By-input"]'

    def getFiltersSearch(self) -> WebElement:
        return self.wait_for(self.filtersSearch).find_element(By.XPATH, "./div/input")

    def getFiltersDocumentType(self) -> WebElement:
        return self.wait_for(self.filtersDocumentType)

    def getFiltersDocumentNumber(self) -> WebElement:
        return self.wait_for(self.filtersDocumentNumber)

    def getFiltersProgram(self) -> WebElement:
        return self.wait_for(self.filtersProgram)

    def getFiltersStatus(self) -> WebElement:
        return self.wait_for(self.filtersStatus)

    def selectFiltersSatus(self, status: str) -> None:
        self.getFiltersStatus().click()
        self.wait_for(f'li[data-value="{status.upper()}"]').click()
        for _ in range(10):
            sleep(1)
            if status.capitalize() in self.getFiltersStatus().text:
                self.getButtonFiltersApply().click()
                break
        else:
            raise Exception(f"Status: {status.capitalize()} does not occur.")

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
        return self.wait_for(self.filtersNumberOfHouseholdsMin).find_element(By.XPATH, "./div/input")

    def getFiltersNumberOfHouseholdsMax(self) -> WebElement:
        return self.wait_for(self.filtersNumberOfHouseholdsMax).find_element(By.XPATH, "./div/input")

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
        return self.wait_for(self.filtersTotalHouseholdsCountMin).find_element(By.XPATH, "./div/input")

    def getFiltersTotalHouseholdsCountMax(self) -> WebElement:
        return self.wait_for(self.filtersTotalHouseholdsCountMax).find_element(By.XPATH, "./div/input")

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

    def getGlobalProgramFilter(self) -> WebElement:
        return self.wait_for(self.globalProgramFilter)

    def getReportTypeFilter(self) -> WebElement:
        return self.wait_for(self.reportTypeFilter)

    def getReportCreatedFromFilter(self) -> WebElement:
        return self.wait_for(self.reportCreatedFromFilter)

    def getReportCreatedToFilter(self) -> WebElement:
        return self.wait_for(self.reportCreatedToFilter)

    def getReportStatusFilter(self) -> WebElement:
        return self.wait_for(self.reportStatusFilter)

    def getReportOnlyMyFilter(self) -> WebElement:
        return self.wait_for(self.reportOnlyMyFilter)

    def getFilterByLocator(self, value: str, locator_type: str = "data-cy") -> WebElement:
        return self.driver.find_elements(By.CSS_SELECTOR, f"[{locator_type}='{value}']")[0].find_elements(
            By.TAG_NAME, "input"
        )[0]
