from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from hct_mis_api.apps.core.utils import encode_id_base64
from tests.selenium.page_object.base_components import BaseComponents


class Targeting(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    searchFilter = 'div[data-cy="filters-search"]'
    statusFilter = 'div[data-cy="filters-status"]'
    programFilter = 'div[data-cy="filters-program"]'
    minNumberOfHouseholds = 'div[data-cy="filters-total-households-count-min"]'
    maxNumberOfHouseholds = 'div[data-cy="filters-total-households-count-max"]'
    buttonCreateNew = 'button[data-cy="button-new-tp"]'
    buttonCreateNewByFilters = 'li[data-cy="menu-item-filters"]'
    tabTitle = 'h6[data-cy="table-title"]'
    tabColumnLabel = 'span[data-cy="table-label"]'
    statusOptions = 'li[role="option"]'
    rows = 'tr[role="checkbox"]'
    createUserFilters = 'div[data-cy="menu-item-filters-text"]'
    createUseIDs = 'div[data-cy="menu-item-ids-text"]'
    buttonInactiveCreateNew = 'a[data-cy="button-target-population-create-new"]'
    tooltip = 'div[role="tooltip"]'
    statusContainer = 'div[data-cy="status-container"]'
    loadingRows = 'tr[data-cy="table-row"]'
    buttonTargetPopulation = 'button[data-cy="button-target-population-info"]'
    buttonApply = 'button[data-cy="button-filters-apply"]'
    buttonClear = 'button[data-cy="button-filters-clear"]'
    tabFieldList = 'button[data-cy="tab-field-list"]'
    tabTargetingDiagram = 'button[data-cy="tab-targeting-diagram"]'
    name = 'th[data-cy="name"]'
    status = 'th[data-cy="status"]'
    numOfHouseholds = 'th[data-cy="num-of-households"]'
    dateCreated = 'th[data-cy="date-created"]'
    lastEdited = 'th[data-cy="last-edited"]'
    createdBy = 'th[data-cy="created-by"]'

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

    def navigate_to_page(self, business_area_slug: str, program_id: str) -> None:
        self.driver.get(self.get_page_url(business_area_slug, program_id))
        self.driver.refresh()

    def get_page_url(self, business_area_slug: str, program_id: str) -> str:
        encoded_program_id = encode_id_base64(program_id, "Program")
        return f"{self.driver.live_server.url}/{business_area_slug}/programs/{encoded_program_id}/target-population"

    # Elements

    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def waitForTextTitlePage(self, text: str) -> bool:
        return self.wait_for_text(text, self.titlePage)

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

    def getButtonCreateNewByFilters(self) -> WebElement:
        return self.wait_for(self.buttonCreateNewByFilters)

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

    def countTargetPopulations(self, number: int) -> None:
        for _ in range(5):
            if len(self.getTargetPopulationsRows()) == number:
                break
        else:
            raise TimeoutError(f"{len(self.getTargetPopulationsRows())} target populations instead of {number}")

    def getCreateUseFilters(self) -> WebElement:
        return self.wait_for(self.createUserFilters)

    def getCreateUseIDs(self) -> WebElement:
        return self.wait_for(self.createUseIDs)

    def getButtonInactiveCreateNew(self) -> WebElement:
        return self.wait_for(self.buttonInactiveCreateNew)

    def geTooltip(self) -> WebElement:
        return self.wait_for(self.tooltip)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTabFieldList(self) -> WebElement:
        return self.wait_for(self.tabFieldList)

    def getTabTargetingDiagram(self) -> WebElement:
        return self.wait_for(self.tabTargetingDiagram)

    def getButtonTargetPopulation(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulation)

    def getLoadingRows(self) -> WebElement:
        return self.wait_for(self.loadingRows)

    def getColumnName(self) -> WebElement:
        return self.wait_for(self.name).find_element(By.CSS_SELECTOR, self.tabColumnLabel)

    def getColumnStatus(self) -> WebElement:
        return self.wait_for(self.status).find_element(By.CSS_SELECTOR, self.tabColumnLabel)

    def getColumnNumOfHouseholds(self) -> WebElement:
        return self.wait_for(self.numOfHouseholds).find_element(By.CSS_SELECTOR, self.tabColumnLabel)

    def getColumnDateCreated(self) -> WebElement:
        return self.wait_for(self.dateCreated).find_element(By.CSS_SELECTOR, self.tabColumnLabel)

    def getColumnLastEdited(self) -> WebElement:
        return self.wait_for(self.lastEdited).find_element(By.CSS_SELECTOR, self.tabColumnLabel)

    def getColumnCreatedBy(self) -> WebElement:
        return self.wait_for(self.createdBy).find_element(By.CSS_SELECTOR, self.tabColumnLabel)

    def disappearLoadingRows(self) -> WebElement:
        try:
            self.getLoadingRows()
        except BaseException:
            self.getStatusContainer()
        return self.wait_for_disappear(self.loadingRows)
