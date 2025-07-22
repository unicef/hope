from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class AccountabilityCommunication(BaseComponents):
    # Locators
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonCommunicationCreateNew = 'a[data-cy="button-communication-create-new"]'
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
    rows = 'tr[role="checkbox"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonCommunicationCreateNew(self) -> WebElement:
        return self.wait_for(self.buttonCommunicationCreateNew)

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
        return self.get_elements(self.tableLabel)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getRows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)
