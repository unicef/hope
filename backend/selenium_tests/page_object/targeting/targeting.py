from time import sleep

from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class Targeting(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    searchFilter = 'div[data-cy="filters-search"]'
    statusFilter = 'div[data-cy="filters-status"]'
    programFilter = 'div[data-cy="filters-program"]'
    minNumberOfHouseholds = 'div[data-cy="filters-total-households-count-min"]'
    maxNumberOfHouseholds = 'div[data-cy="filters-total-households-count-max"]'
    buttonCreateNew = 'button[data-cy="button-new-tp"]'
    tabTitle = 'h6[data-cy="table-title"]'
    tabColumnLabel = 'span[data-cy="table-label"]'
    statusOptions = 'li[role="option"]'
    rows = 'tr[role="checkbox"]'
    createUserFilters = 'div[data-cy="menu-item-filters-text"]'
    createUseIDs = 'div[data-cy="menu-item-ids-text"]'

    # Texts

    textTitlePage = "Targeting"
    textCreateNew = "Create new"
    textTabTitle = "Target Populations"
    textTabName = "Name"
    textTabStatus = "Status"
    textTabProgramme = "Programme"
    textTabNOHouseholds = "Num. of Households"
    textTabDateCreated = "Date Created"
    textTabLastEdited = "Last Edited"
    textTabCreatedBy = "Created by"
    buttonApply = 'button[data-cy="button-filters-apply"]'
    buttonClear = 'button[data-cy="button-filters-clear"]'

    # Elements

    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getSearchFilter(self) -> WebElement:
        return self.wait_for(self.searchFilter)

    def getStatusFilter(self) -> WebElement:
        return self.wait_for(self.statusFilter)

    def getProgramFilter(self) -> WebElement:
        return self.wait_for(self.programFilter)

    def getMinNumberOfHouseholdsFilter(self) -> WebElement:
        return self.wait_for(self.minNumberOfHouseholds)

    def getMaxNumberOfHouseholdsFilter(self) -> WebElement:
        return self.wait_for(self.maxNumberOfHouseholds)

    def getButtonCreateNew(self) -> WebElement:
        return self.wait_for(self.buttonCreateNew)

    def getTabTitle(self) -> WebElement:
        return self.wait_for(self.tabTitle)

    def getTabColumnLabel(self) -> list[WebElement]:
        return self.get_elements(self.tabColumnLabel)

    def getStatusOption(self) -> WebElement:
        return self.wait_for(self.statusOptions)

    def getApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)

    def getClear(self) -> WebElement:
        return self.wait_for(self.buttonClear)

    def getTargetPopulationsRows(self) -> list[WebElement]:
        return self.get_elements(self.rows)

    def chooseTargetPopulations(self, number: int) -> WebElement:
        try:
            self.wait_for(self.rows)
            return self.get_elements(self.rows)[number]
        except IndexError:
            sleep(1)
            return self.get_elements(self.rows)[number]

    def getCreateUseFilters(self) -> WebElement:
        return self.wait_for(self.createUserFilters)

    def getCreateUseIDs(self) -> WebElement:
        return self.wait_for(self.createUseIDs)
