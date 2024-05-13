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
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'

    def getFiltersSearch(self) -> WebElement:
        return self.wait_for(self.filtersSearch)

    def getFiltersStatus(self) -> WebElement:
        return self.wait_for(self.filtersStatus)

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
