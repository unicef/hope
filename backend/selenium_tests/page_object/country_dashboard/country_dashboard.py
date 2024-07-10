from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class CountryDashboard(BaseComponents):
    navResourcesReleaseNote = 'a[data-cy="nav-resources-Release Note"]'
    mainContent = 'div[data-cy="main-content"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonEdPlan = 'button[data-cy="button-ed-plan"]'
    filtersProgram = 'div[data-cy="filters-program"]'
    programmeInput = 'div[data-cy="Programme-input"]'
    filterAdministrativeArea = 'div[data-cy="filter-administrative-area"]'
    adminLevel2Input = 'div[data-cy="Admin Level 2-input"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableLabel = 'span[data-cy="table-label"]'
    totalNumberOfHouseholdsReached = 'div[data-cy="total-number-of-households-reached"]'
    totalNumberOfIndividualsReached = 'div[data-cy="total-number-of-individuals-reached"]'
    totalNumberOfPeopleReached = 'div[data-cy="total-number-of-people-reached"]'
    totalNumberOfChildrenReached = 'div[data-cy="total-number-of-children-reached"]'
    totalNumberOfGrievances = 'span[data-cy="total-number-of-grievances"]'
    totalNumberOfFeedback = 'span[data-cy="total-number-of-feedback"]'
    totalAmountTransferred = 'div[data-cy="total-amount-transferred"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonEdPlan(self) -> WebElement:
        return self.wait_for(self.buttonEdPlan)

    def getFiltersProgram(self) -> WebElement:
        return self.wait_for(self.filtersProgram)

    def getProgrammeInput(self) -> WebElement:
        return self.wait_for(self.programmeInput)

    def getFilterAdministrativeArea(self) -> WebElement:
        return self.wait_for(self.filterAdministrativeArea)

    def getAdminLevel2Input(self) -> WebElement:
        return self.wait_for(self.adminLevel2Input)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getTableLabel(self) -> [WebElement]:
        return self.get_elements(self.tableLabel)

    def getTotalNumberOfHouseholdsReached(self) -> WebElement:
        return self.wait_for(self.totalNumberOfHouseholdsReached)

    def getTotalNumberOfIndividualsReached(self) -> WebElement:
        return self.wait_for(self.totalNumberOfIndividualsReached)

    def getTotalNumberOfPeopleReached(self) -> WebElement:
        return self.wait_for(self.totalNumberOfPeopleReached)

    def getTotalNumberOfChildrenReached(self) -> WebElement:
        return self.wait_for(self.totalNumberOfChildrenReached)

    def getTotalNumberOfGrievances(self) -> WebElement:
        return self.wait_for(self.totalNumberOfGrievances)

    def getTotalNumberOfFeedback(self) -> WebElement:
        return self.wait_for(self.totalNumberOfFeedback)

    def getTotalAmountTransferred(self) -> WebElement:
        return self.wait_for(self.totalAmountTransferred)
