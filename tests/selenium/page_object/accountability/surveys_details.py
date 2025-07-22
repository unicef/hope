from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class AccountabilitySurveysDetails(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    labelCategory = 'div[data-cy="label-Category"]'
    labelSurveyTitle = 'div[data-cy="label-Survey Title"]'
    labelCreatedBy = 'div[data-cy="label-Created By"]'
    labelDateCreated = 'div[data-cy="label-Date Created"]'
    labelTargetPopulation = 'div[data-cy="label-Target Population"]'
    labelProgramme = 'div[data-cy="label-Programme"]'
    tableTitle = 'h6[data-cy="table-title"]'
    householdId = 'th[data-cy="household-id"]'
    tableLabel = 'span[data-cy="table-label"]'
    status = 'th[data-cy="status"]'
    householdHeadName = 'th[data-cy="household-head-name"]'
    householdSize = 'th[data-cy="household-size"]'
    householdLocation = 'th[data-cy="household-location"]'
    householdResidenceStatus = 'th[data-cy="household-residence-status"]'
    householdRegistrationDate = 'th[data-cy="household-registration-date"]'
    tableRow = 'tr[data-cy="table-row"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    rows = 'tr[role="checkbox"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getLabelCategory(self) -> WebElement:
        return self.wait_for(self.labelCategory)

    def getLabelSurveyTitle(self) -> WebElement:
        return self.wait_for(self.labelSurveyTitle)

    def getLabelCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelCreatedBy)

    def getLabelDateCreated(self) -> WebElement:
        return self.wait_for(self.labelDateCreated)

    def getLabelTargetPopulation(self) -> WebElement:
        return self.wait_for(self.labelTargetPopulation)

    def getLabelProgramme(self) -> WebElement:
        return self.wait_for(self.labelProgramme)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getHouseholdId(self) -> WebElement:
        return self.wait_for(self.householdId)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getStatus(self) -> WebElement:
        return self.wait_for(self.status)

    def getHouseholdHeadName(self) -> WebElement:
        return self.wait_for(self.householdHeadName)

    def getHouseholdSize(self) -> WebElement:
        return self.wait_for(self.householdSize)

    def getHouseholdLocation(self) -> WebElement:
        return self.wait_for(self.householdLocation)

    def getHouseholdResidenceStatus(self) -> WebElement:
        return self.wait_for(self.householdResidenceStatus)

    def getHouseholdRegistrationDate(self) -> WebElement:
        return self.wait_for(self.householdRegistrationDate)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getRows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)
