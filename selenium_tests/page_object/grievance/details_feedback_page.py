from page_object.base_components import BaseComponents


class FeedbackDetailsPage(BaseComponents):
    # Locators
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    titlePage = 'h5[data-cy="page-header-title"]'
    buttonEdit = 'a[data-cy="button-edit"]'
    labelCategory = 'div[data-cy="label-Category"]'
    labelIssueType = 'div[data-cy="label-Issue Type"]'
    labelHouseholdID = 'div[data-cy="label-Household ID"]'
    labelIndividualID = 'div[data-cy="label-Individual ID"]'
    labelCreatedBy = 'div[data-cy="label-Created By"]'
    labelDateCreated = 'div[data-cy="label-Date Created"]'
    labelLastModifiedDate = 'div[data-cy="label-Last Modified Date"]'
    labelAdministrativeLevel2 = 'div[data-cy="label-Administrative Level 2"]'
    labelAreaVillagePayPoint = 'div[data-cy="label-Area / Village / Pay point"]'
    labelLanguagesSpoken = 'div[data-cy="label-Languages Spoken"  ]'
    labelDescription = 'div[data-cy="label-Description"]'
    labelComments = 'div[data-cy="label-Comments"]'
    buttonCreateLinkedTicket = 'button[data-cy="button-create-linked-ticket"]'
    labelTicketId = 'div[data-cy="label-Ticket Id"]'

    # Texts
    textTitle = "Feedback ID: "
    textCategory = "Feedback"
    textIssueType = "Negative Feedback"
    textDescription = "Negative Feedback"

    # Elements
    def getPageHeaderContainer(self):
        return self.wait_for(self.pageHeaderContainer)

    def getTitlePage(self):
        return self.wait_for(self.titlePage)

    def getButtonEdit(self):
        return self.wait_for(self.buttonEdit)

    def getCategory(self):
        return self.wait_for(self.labelCategory)

    def getIssueType(self):
        return self.wait_for(self.labelIssueType)

    def getHouseholdID(self):
        return self.wait_for(self.labelHouseholdID)

    def getIndividualID(self):
        return self.wait_for(self.labelIndividualID)

    def getCreatedBy(self):
        return self.wait_for(self.labelCreatedBy)

    def getDateCreated(self):
        return self.wait_for(self.labelDateCreated)

    def getLastModifiedDate(self):
        return self.wait_for(self.labelLastModifiedDate)

    def getAdministrativeLevel2(self):
        return self.wait_for(self.labelAdministrativeLevel2)

    def getAreaVillagePayPoint(self):
        return self.wait_for(self.labelAreaVillagePayPoint)

    def getLanguagesSpoken(self):
        return self.wait_for(self.labelLanguagesSpoken)

    def getDescription(self):
        return self.wait_for(self.labelDescription)

    def getComments(self):
        return self.wait_for(self.labelComments)

    def getButtonCreateLinkedTicket(self):
        return self.wait_for(self.buttonCreateLinkedTicket)

    def getLabelTicketId(self):
        return self.wait_for(self.labelTicketId)
