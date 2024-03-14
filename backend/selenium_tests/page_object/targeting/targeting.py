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
    buttonCreateNew = 'a[data-cy="button-target-population-create-new"]'
    tabTitle = 'h6[data-cy="table-title"]'
    tabColumnLabel = 'span[data-cy="table-label"]'
    statusOptions = 'li[role="option"]'
    rows = 'tr[role="checkbox"]'

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

    def getTabColumnName(self) -> WebElement:
        return self.wait_for(self.tabColumnLabel).eq(0)

    def getTabColumnStatus(self) -> WebElement:
        return self.wait_for(self.tabColumnLabel).eq(1)

    def getTabColumnNOHouseholds(self) -> WebElement:
        return self.wait_for(self.tabColumnLabel).eq(2)

    def getTabColumnDateCreated(self) -> WebElement:
        return self.wait_for(self.tabColumnLabel).eq(3)

    def getTabColumnLastEdited(self) -> WebElement:
        return self.wait_for(self.tabColumnLabel).eq(4)

    def getTabColumnCreatedBy(self) -> WebElement:
        return self.wait_for(self.tabColumnLabel).eq(5)

    def getStatusOption(self) -> WebElement:
        return self.wait_for(self.statusOptions)

    def getApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)

    def getClear(self) -> WebElement:
        return self.wait_for(self.buttonClear)

    def getTargetPopulationsRows(self) -> WebElement:
        return self.wait_for(self.rows)

    def checkElementsOnPage(self) -> None:
        self.getTitlePage().should("be.visible").contains(self.textTitlePage)
        # self.getButtonFiltersExpand().click()
        self.getSearchFilter().should("be.visible")
        self.getStatusFilter().should("be.visible")
        self.getMinNumberOfHouseholdsFilter().should("be.visible")
        self.getMaxNumberOfHouseholdsFilter().should("be.visible")
        self.getButtonCreateNew().should("be.visible").contains(self.textCreateNew)
        self.getTabTitle().should("be.visible").contains(self.textTabTitle)
        self.getTabColumnName().should("be.visible").contains(self.textTabName)
        self.getTabColumnStatus().should("be.visible").contains(self.textTabStatus)
        self.getTabColumnNOHouseholds()
        self.getTabColumnDateCreated()
        self.getTabColumnLastEdited()
        self.getTabColumnCreatedBy()

    def selectStatus(self, status: str) -> None:
        self.getStatusFilter().click()
        self.getStatusOption().contains(status).click()
        self.pressEscapeFromElement(self.getStatusOption().contains(status))
        self.getApply().click()

    def chooseTargetPopulationRow(self, row: int) -> WebElement:
        return self.getTargetPopulationsRows().eq(row)
