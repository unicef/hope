from page_object.base_components import BaseComponents

class ProgrammeDetails(BaseComponents):

    headerTitle = 'h5[data-cy="page-header-title"]'
    programStatus = 'div[data-cy="status-container"]'
    labelStartDate = 'div[data-cy="label-START DATE"]'
    labelEndDate = 'div[data-cy="label-END DATE"]'
    labelSelector = 'div[data-cy="label-Sector"]'
    labelDataCollectingType = 'div[data-cy="label-Data Collecting Type"]'
    labelFreqOfPayment = 'div[data-cy="label-Frequency of Payment"]'
    labelAdministrativeAreas = 'div[data-cy="label-Administrative Areas of implementation"]'
    labelCashPlus = 'div[data-cy="label-CASH+"]'
    labelTotalNumberOfHouseholds = 'div[data-cy="label-Total Number of Households"]'
    labelDescription = 'div[data-cy="label-Description"]'
    labelAreaAccess = 'div[data-cy="label-Area Access"]'
    labelPartnerName = 'h6[data-cy="label-partner-name"]'

    def getLabelPartnerName(self):
        return self.wait_for(self.labelPartnerName)

    def getLabelAreaAccess(self):
        return self.wait_for(self.labelAreaAccess)

    def getProgramStatus(self):
        return self.wait_for(self.programStatus)

    def getHeaderTitle(self):
        return self.wait_for(self.headerTitle)

    def getLabelStartDate(self):
        return self.wait_for(self.labelStartDate)

    def getLabelEndDate(self):
        return self.wait_for(self.labelEndDate)

    def getLabelSelector(self):
        return self.wait_for(self.labelSelector)

    def getLabelDataCollectingType(self):
        return self.wait_for(self.labelDataCollectingType)

    def getLabelFreqOfPayment(self):
        return self.wait_for(self.labelFreqOfPayment)

    def getLabelAdministrativeAreas(self):
        return self.wait_for(self.labelAdministrativeAreas)

    def getLabelCashPlus(self):
        return self.wait_for(self.labelCashPlus)

    def getLabelTotalNumberOfHouseholds(self):
        return self.wait_for(self.labelTotalNumberOfHouseholds)
