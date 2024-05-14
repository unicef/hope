from time import sleep

from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement

from hct_mis_api.apps.core.utils import encode_id_base64


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

    def navigate_to_page(self, business_area_slug: str, program_id: str) -> None:
        self.driver.get(self.get_page_url(business_area_slug, program_id))

    def get_page_url(self, business_area_slug: str, program_id: str) -> str:
        encoded_program_id = encode_id_base64(program_id, "Program")
        return f"{self.driver.live_server.url}/{business_area_slug}/programs/{encoded_program_id}/target-population"

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

    def getCreateUseFilters(self) -> WebElement:
        return self.wait_for(self.createUserFilters)

    def getCreateUseIDs(self) -> WebElement:
        return self.wait_for(self.createUseIDs)
