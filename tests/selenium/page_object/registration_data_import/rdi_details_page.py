from time import sleep

from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class RDIDetailsPage(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    labelStatus = 'div[data-cy="label-status"]'
    statusContainer = 'div[data-cy="status-container"]'
    labelSourceOfData = 'div[data-cy="label-Source of Data"]'
    labelImportDate = 'div[data-cy="label-Import Date"]'
    labelImportedBy = 'div[data-cy="label-Imported by"]'
    labelizedFieldContainerHouseholds = 'div[data-cy="labelized-field-container-households"]'
    labelTotalNumberOfHouseholds = 'div[data-cy="label-Total Number of Items Groups"]'
    labelizedFieldContainerIndividuals = 'div[data-cy="labelized-field-container-individuals"]'
    labelTotalNumberOfIndividuals = 'div[data-cy="label-Total Number of Items"]'
    tableLabel = 'span[data-cy="table-label"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    importedIndividualsTable = 'div[data-cy="imported-individuals-table"]'
    tableRow = 'tr[data-cy="table-row"]'
    buttonRefuseRdi = 'button[data-cy="button-refuse-rdi"]'
    buttonMergeRdi = 'button[data-cy="button-merge-rdi"]'
    buttonMerge = 'button[data-cy="button-merge"]'
    buttonViewTickets = 'a[data-cy="button-view-tickets"]'
    buttonHouseholds = 'button[data-cy="tab-Households"]'
    buttonIndividuals = 'button[data-cy="tab-Individuals"]'
    importedHouseholdsRow = './/tr[@data-cy="imported-households-row"]'

    # Texts
    buttonRefuseRdiText = "REFUSE IMPORT"
    buttonMergeRdiText = "MERGE"

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getLabelStatus(self) -> WebElement:
        return self.wait_for(self.labelStatus)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getLabelSourceOfData(self) -> WebElement:
        return self.wait_for(self.labelSourceOfData)

    def getLabelImportDate(self) -> WebElement:
        return self.wait_for(self.labelImportDate)

    def getLabelImportedBy(self) -> WebElement:
        return self.wait_for(self.labelImportedBy)

    def getLabelizedFieldContainerHouseholds(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerHouseholds)

    def getLabelTotalNumberOfHouseholds(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfHouseholds)

    def getLabelizedFieldContainerIndividuals(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerIndividuals)

    def getLabelTotalNumberOfIndividuals(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfIndividuals)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def getButtonRefuseRdi(self) -> WebElement:
        return self.wait_for(self.buttonRefuseRdi)

    def getTablePagination(self) -> WebElement:
        return self.get(self.tablePagination)

    def getButtonMergeRdi(self) -> WebElement:
        return self.wait_for(self.buttonMergeRdi)

    def getButtonMerge(self) -> WebElement:
        return self.wait_for(self.buttonMerge)

    def getButtonViewTickets(self) -> WebElement:
        return self.wait_for(self.buttonViewTickets)

    def getButtonHouseholds(self) -> WebElement:
        return self.wait_for(self.buttonHouseholds)

    def getButtonIndividuals(self) -> WebElement:
        return self.wait_for(self.buttonIndividuals)

    def getImportedIndividualsTable(self) -> WebElement:
        return self.wait_for(self.importedIndividualsTable)

    def getImportedHouseholdsRow(self, number: int) -> WebElement:
        self.wait_for(self.importedHouseholdsRow, By.XPATH)
        return self.get_elements(self.importedHouseholdsRow, By.XPATH)[number]

    def waitForStatus(self, status: str, timeout: int = 60) -> None:
        for _ in range(timeout):
            sleep(1)
            if self.getStatusContainer().text == status:
                break
            self.driver.refresh()

    def waitForNumberOfRows(self, string: str, timeout: int = 60) -> bool:
        for _ in range(timeout):
            sleep(1)
            if string in self.get('//*[@data-cy="table-pagination"]/div/p[2]', By.XPATH).text:
                return True
        print(self.get('//*[@data-cy="table-pagination"]/div/p[2]', By.XPATH).text)
        return False
