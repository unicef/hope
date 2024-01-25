from page_object.base_components import BaseComponents


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

  getTitlePage(self):
        return self.wait_for(self.titlePage)
  getSearchFilter(self):
        return self.wait_for(self.searchFilter)
  getStatusFilter(self):
        return self.wait_for(self.statusFilter)
  getProgramFilter(self):
        return self.wait_for(self.programFilter)
  getMinNumberOfHouseholdsFilter(self):
        return self.wait_for(self.minNumberOfHouseholds)
  getMaxNumberOfHouseholdsFilter(self):
        return self.wait_for(self.maxNumberOfHouseholds)
  getButtonCreateNew(self):
        return self.wait_for(self.buttonCreateNew)
  getTabTitle(self):
        return self.wait_for(self.tabTitle)
  getTabColumnName(self):
        return self.wait_for(self.tabColumnLabel).eq(0)
  getTabColumnStatus(self):
        return self.wait_for(self.tabColumnLabel).eq(1)
  getTabColumnNOHouseholds(self):
        return self.wait_for(self.tabColumnLabel).eq(2)
  getTabColumnDateCreated(self):
        return self.wait_for(self.tabColumnLabel).eq(3)
  getTabColumnLastEdited(self):
        return self.wait_for(self.tabColumnLabel).eq(4)
  getTabColumnCreatedBy(self):
        return self.wait_for(self.tabColumnLabel).eq(5)
  getStatusOption(self):
        return self.wait_for(self.statusOptions)
  getApply(self):
        return self.wait_for(self.buttonApply)
  getClear(self):
        return self.wait_for(self.buttonClear)

  getTargetPopulationsRows(self):
        return self.wait_for(self.rows)

  checkElementsOnPage() {
    this.getTitlePage().should("be.visible").contains(this.textTitlePage)
    # this.getButtonFiltersExpand().click()
    this.getSearchFilter().should("be.visible")
    this.getStatusFilter().should("be.visible")
    this.getMinNumberOfHouseholdsFilter().should("be.visible")
    this.getMaxNumberOfHouseholdsFilter().should("be.visible")
    this.getButtonCreateNew().should("be.visible").contains(this.textCreateNew)
    this.getTabTitle().should("be.visible").contains(this.textTabTitle)
    this.getTabColumnName().should("be.visible").contains(this.textTabName)
    this.getTabColumnStatus().should("be.visible").contains(this.textTabStatus)
    this.getTabColumnNOHouseholds()
      .should("be.visible")
      .contains(this.textTabNOHouseholds)
    this.getTabColumnDateCreated()
      .scrollIntoView()
      .should("be.visible")
      .contains(this.textTabDateCreated)
    this.getTabColumnLastEdited()
      .scrollIntoView()
      .should("be.visible")
      .contains(this.textTabLastEdited)
    this.getTabColumnCreatedBy()
      .scrollIntoView()
      .should("be.visible")
      .contains(this.textTabCreatedBy)
  }

  selectStatus(status) {
    this.getStatusFilter().click()
    this.getStatusOption().contains(status).click()
    this.pressEscapeFromElement(this.getStatusOption().contains(status))
    this.getApply().click()
  }

  chooseTargetPopulationRow(row) {
    return this.getTargetPopulationsRows().eq(row)
  }
}
