from e2e.page_object.base_components import BaseComponents
from e2e.webdriver.remote.webelement import WebElement


class AccountabilitySurveys(BaseComponents):
    # Locators
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonNewSurvey = 'button[data-cy="button-new-survey"]'
    filtersSearch = 'div[data-cy="filters-search"]'
    filtersTargetPopulationAutocomplete = 'div[data-cy="filters-target-population-autocomplete"]'
    targetPopulationInput = 'div[data-cy="Target Population-input"]'
    filtersCreatedByAutocomplete = 'div[data-cy="filters-created-by-autocomplete"]'
    createdByInput = 'div[data-cy="Created by-input"]'
    filtersCreationDateFrom = 'div[data-cy="filters-creation-date-from"]'
    filtersCreationDateTo = 'div[data-cy="filters-creation-date-to"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableLabel = 'span[data-cy="table-label"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    menuItemRapidPro = 'li[data-cy="menu-item-rapid-pro"]'
    menuItemRapidProText = 'div[data-cy="menu-item-rapid-pro-text"]'
    menuItemSmsText = 'li[data-cy="menu-item-sms-text"]'
    menuItemManual = 'li[data-cy="menu-item-manual"]'
    menuItemManualText = 'div[data-cy="menu-item-manual-text"]'
    rows = 'tr[role="checkbox"]'

    # Texts
    textTitlePage = "Surveys"
    textNewSurvey = "New Survey"
    textTargetPopulationFilter = "Target Population"
    textTabCreatedBy = "Created by"

    # Elements
    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonNewSurvey(self) -> WebElement:
        return self.wait_for(self.buttonNewSurvey)

    def getFiltersSearch(self) -> WebElement:
        return self.wait_for(self.filtersSearch)

    def getFiltersTargetPopulationAutocomplete(self) -> WebElement:
        return self.wait_for(self.filtersTargetPopulationAutocomplete)

    def getTargetPopulationInput(self) -> WebElement:
        return self.wait_for(self.targetPopulationInput)

    def getFiltersCreatedByAutocomplete(self) -> WebElement:
        return self.wait_for(self.filtersCreatedByAutocomplete)

    def getCreatedByInput(self) -> WebElement:
        return self.wait_for(self.createdByInput)

    def getFiltersCreationDateFrom(self) -> WebElement:
        return self.wait_for(self.filtersCreationDateFrom)

    def getFiltersCreationDateTo(self) -> WebElement:
        return self.wait_for(self.filtersCreationDateTo)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getTableLabel(self) -> [WebElement]:
        self.wait_for(self.tableLabel)
        return self.get_elements(self.tableLabel)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getMenuItemRapidPro(self) -> WebElement:
        return self.wait_for(self.menuItemRapidPro)

    def getMenuItemRapidProText(self) -> WebElement:
        return self.wait_for(self.menuItemRapidProText)

    def getMenuItemSmsText(self) -> WebElement:
        return self.wait_for(self.menuItemSmsText)

    def getMenuItemManual(self) -> WebElement:
        return self.wait_for(self.menuItemManual)

    def getMenuItemManualText(self) -> WebElement:
        return self.wait_for(self.menuItemManualText)

    def getRows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)
