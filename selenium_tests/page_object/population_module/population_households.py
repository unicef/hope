from page_object.base_components import BaseComponents


class PopulationHouseholds(BaseComponents):
    # Locators
    householdTableRow = 'tr[data-cy="household-table-row"]'
    statusContainer = 'div[data-cy="status-container"]'
    householdId = 'th[data-cy="household-id"]'
    labelStatus = 'th[data-cy="status"]'
    householdHeadName = 'th[data-cy="household-head-name"]'
    householdSize = 'th[data-cy="household-size"]'
    householdLocation = 'th[data-cy="household-location"]'
    householdResidenceStatus = 'th[data-cy="household-residence-status"]'
    householdTotalCashReceived = 'th[data-cy="household-total-cash-received"]'
    householdRegistrationDate = 'th[data-cy="household-registration-date"]'
    tableTitle = 'h6[data-cy="table-title"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    hhFiltersStatus = 'div[data-cy="hh-filters-status"]'
    hhFiltersOrderBy = 'div[data-cy="hh-filters-order-by"]'
    hhFiltersHouseholdSizeTo = 'div[data-cy="hh-filters-household-size-to"]'
    hhFiltersHouseholdSizeFrom = 'div[data-cy="hh-filters-household-size-from"]'
    hhFiltersResidenceStatus = 'div[data-cy="hh-filters-residence-status"]'
    filterSearchType = 'div[data-cy="filter-search-type"]'
    filterSearchType1 = 'div[data-cy="filter-search-type"]'
    hhFiltersSearch = 'div[data-cy="hh-filters-search"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'

    # Texts
    textTitle = "Households"

    # Elements

    def getHouseholdTableRow(self):
        return self.wait_for(self.householdTableRow)

    def getStatusContainer(self):
        return self.wait_for(self.statusContainer)

    def getHouseholdId(self):
        return self.wait_for(self.householdId)

    def getLabelStatus(self):
        return self.wait_for(self.labelStatus)

    def getHouseholdHeadName(self):
        return self.wait_for(self.householdHeadName)

    def getHouseholdSize(self):
        return self.wait_for(self.householdSize)

    def getHouseholdLocation(self):
        return self.wait_for(self.householdLocation)

    def getHouseholdResidenceStatus(self):
        return self.wait_for(self.householdResidenceStatus)

    def getHouseholdTotalCashReceived(self):
        return self.wait_for(self.householdTotalCashReceived)

    def getHouseholdRegistrationDate(self):
        return self.wait_for(self.householdRegistrationDate)

    def getTableTitle(self):
        return self.wait_for(self.tableTitle)

    def getButtonFiltersApply(self):
        return self.wait_for(self.buttonFiltersApply)

    def getButtonFiltersClear(self):
        return self.wait_for(self.buttonFiltersClear)

    def getHhFiltersStatus(self):
        return self.wait_for(self.hhFiltersStatus)

    def getHhFiltersOrderBy(self):
        return self.wait_for(self.hhFiltersOrderBy)

    def getHhFiltersHouseholdSizeTo(self):
        return self.wait_for(self.hhFiltersHouseholdSizeTo)

    def getHhFiltersHouseholdSizeFrom(self):
        return self.wait_for(self.hhFiltersHouseholdSizeFrom)

    def getHhFiltersResidenceStatus(self):
        return self.wait_for(self.hhFiltersResidenceStatus)

    def getFilterSearchType(self):
        return self.wait_for(self.filterSearchType)

    def getFilterSearchType1(self):
        return self.wait_for(self.filterSearchType1)

    def getHhFiltersSearch(self):
        return self.wait_for(self.hhFiltersSearch)

    def getPageHeaderTitle(self):
        return self.wait_for(self.pageHeaderTitle)

    def checkElementsOnPage(self):
        self.getHouseholdTableRow().should("be.visible")
        self.getStatusContainer().should("be.visible")
        self.getHouseholdId().should("be.visible")
        self.getLabelStatus().should("be.visible")
        self.getHouseholdHeadName().should("be.visible")
        self.getHouseholdSize().should("be.visible")
        self.getHouseholdLocation().should("be.visible")
        self.getHouseholdResidenceStatus().should("be.visible")
        self.getHouseholdTotalCashReceived().should("be.visible")
        self.getHouseholdRegistrationDate().should("be.visible")
        self.getTableTitle().should("be.visible")
        self.getButtonFiltersApply().should("be.visible")
        self.getButtonFiltersClear().should("be.visible")
        self.getHhFiltersStatus().should("be.visible")
        self.getHhFiltersOrderBy().should("be.visible")
        self.getHhFiltersHouseholdSizeTo().should("be.visible")
        self.getHhFiltersHouseholdSizeFrom().should("be.visible")
        self.getHhFiltersResidenceStatus().should("be.visible")
        self.getFilterSearchType().should("be.visible")
        self.getFilterSearchType1().should("be.visible")
        self.getHhFiltersSearch().should("be.visible")
        self.getPageHeaderTitle().should("be.visible")

    def clickNavHouseholds(self):
        self.getMenuButtonProgrammePopulation().click()
        self.getMenuButtonHouseholds().should("be.visible")
        self.getMenuButtonHouseholds().click()
