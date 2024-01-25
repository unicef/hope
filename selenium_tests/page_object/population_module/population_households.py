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
  # ToDo: Add data-cy
  filterAdminLevel2 = "brak"

  # Texts
  textTitle = "Households"
  # Elements
  getHouseholdTableRow(self):
        return self.wait_for(self.householdTableRow)
  getStatusContainer(self):
        return self.wait_for(self.statusContainer)
  getHouseholdId(self):
        return self.wait_for(self.householdId)
  getLabelStatus(self):
        return self.wait_for(self.labelStatus)
  getHouseholdHeadName(self):
        return self.wait_for(self.householdHeadName)
  getHouseholdSize(self):
        return self.wait_for(self.householdSize)
  getHouseholdLocation(self):
        return self.wait_for(self.householdLocation)
  getHouseholdResidenceStatus(self):
        return self.wait_for(self.householdResidenceStatus)
  getHouseholdTotalCashReceived(self):
        return self.wait_for(self.householdTotalCashReceived)
  getHouseholdRegistrationDate(self):
        return self.wait_for(self.householdRegistrationDate)
  getTableTitle(self):
        return self.wait_for(self.tableTitle)
  getButtonFiltersApply(self):
        return self.wait_for(self.buttonFiltersApply)
  getButtonFiltersClear(self):
        return self.wait_for(self.buttonFiltersClear)
  getHhFiltersStatus(self):
        return self.wait_for(self.hhFiltersStatus)
  getHhFiltersOrderBy(self):
        return self.wait_for(self.hhFiltersOrderBy)
  getHhFiltersHouseholdSizeTo(self):
        return self.wait_for(self.hhFiltersHouseholdSizeTo)
  getHhFiltersHouseholdSizeFrom(self):
        return self.wait_for(self.hhFiltersHouseholdSizeFrom)
  getHhFiltersResidenceStatus(self):
        return self.wait_for(self.hhFiltersResidenceStatus)
  getFilterSearchType(self):
        return self.wait_for(self.filterSearchType)
  getFilterSearchType1(self):
        return self.wait_for(self.filterSearchType1)
  getHhFiltersSearch(self):
        return self.wait_for(self.hhFiltersSearch)
  getPageHeaderTitle(self):
        return self.wait_for(self.pageHeaderTitle)

  checkElementsOnPage() {
    this.getHouseholdTableRow().should("be.visible")
    this.getStatusContainer().should("be.visible")
    this.getHouseholdId().should("be.visible")
    this.getLabelStatus().should("be.visible")
    this.getHouseholdHeadName().should("be.visible")
    this.getHouseholdSize().should("be.visible")
    this.getHouseholdLocation().should("be.visible")
    this.getHouseholdResidenceStatus().should("be.visible")
    this.getHouseholdTotalCashReceived().should("be.visible")
    this.getHouseholdRegistrationDate().should("be.visible")
    this.getTableTitle().should("be.visible")
    this.getButtonFiltersApply().should("be.visible")
    this.getButtonFiltersClear().should("be.visible")
    this.getHhFiltersStatus().should("be.visible")
    this.getHhFiltersOrderBy().should("be.visible")
    this.getHhFiltersHouseholdSizeTo().should("be.visible")
    this.getHhFiltersHouseholdSizeFrom().should("be.visible")
    this.getHhFiltersResidenceStatus().should("be.visible")
    this.getFilterSearchType().should("be.visible")
    this.getFilterSearchType1().should("be.visible")
    this.getHhFiltersSearch().should("be.visible")
    this.getPageHeaderTitle().should("be.visible")
  }
  clickNavHouseholds() {
    this.getMenuButtonProgrammePopulation().click()
    this.getMenuButtonHouseholds().should("be.visible")
    this.getMenuButtonHouseholds().click()
  }
}
