from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class TargetingDetails(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    status = 'div[data-cy="target-population-status"]'
    criteria_container = 'div[data-cy="criteria-container"]'
    lock_button = 'button[data-cy="button-target-population-lock"]'
    household_table_cell = "table tr:nth-of-type({}) td:nth-of-type({})"
    people_table_rows = '[data-cy="target-population-people-row"]'
    household_table_rows = '[data-cy="target-population-household-row"]'

    # Texts
    # Elements

    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getStatus(self) -> WebElement:
        return self.wait_for(self.status)

    def getCriteriaContainer(self) -> WebElement:
        return self.wait_for(self.criteria_container)

    def getLockButton(self) -> WebElement:
        return self.wait_for(self.lock_button)

    def getHouseholdTableCell(self, row: int, column: int) -> WebElement:
        return self.wait_for(self.household_table_cell.format(row, column))

    def getPeopleTableRows(self) -> list[WebElement]:
        return self.get_elements(self.people_table_rows)

    def getHouseholdTableRows(self) -> list[WebElement]:
        return self.get_elements(self.household_table_rows)
