from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class IndividualsDetails(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    labelFullName = 'div[data-cy="label-Full Name"]'
    labelGivenName = 'div[data-cy="label-Given Name"]'
    labelMiddleName = 'div[data-cy="label-Middle Name"]'
    labelFamilyName = 'div[data-cy="label-Family Name"]'
    labelGender = 'div[data-cy="label-Gender"]'
    labelAge = 'div[data-cy="label-Age"]'
    labelDateOfBirth = 'div[data-cy="label-Date of Birth"]'
    labelEstimatedDateOfBirth = 'div[data-cy="label-Estimated Date of Birth"]'
    labelMaritalStatus = 'div[data-cy="label-Marital Status"]'
    labelWorkStatus = 'div[data-cy="label-Work Status"]'
    labelPregnant = 'div[data-cy="label-Pregnant"]'
    labelHouseholdId = 'div[data-cy="label-Items Group ID"]'
    labelRole = 'div[data-cy="label-Role"]'
    labelRelationshipToHoh = 'div[data-cy="label-Relationship to Head Of Items Group"]'
    labelPreferredLanguage = 'div[data-cy="label-Preferred language"]'
    labelLinkedHouseholds = 'div[data-cy="label-Linked Items Groups"]'
    labelObservedDisabilities = 'div[data-cy="label-Observed disabilities"]'
    labelSeeingDisabilitySeverity = 'div[data-cy="label-Seeing disability severity"]'
    labelHearingDisabilitySeverity = 'div[data-cy="label-Hearing disability severity"]'
    labelPhysicalDisabilitySeverity = 'div[data-cy="label-Physical disability severity"]'
    labelRememberingOrConcentratingDisabilitySeverity = (
        'div[data-cy="label-Remembering or concentrating disability severity"]'
    )
    labelSelfCareDisabilitySeverity = 'div[data-cy="label-Self-care disability severity"]'
    labelCommunicatingDisabilitySeverity = 'div[data-cy="label-Communicating disability severity"]'
    labelDisability = 'div[data-cy="label-Disability"]'
    labelBirth_certificate = 'div[data-cy="label-BIRTH_CERTIFICATE"]'
    labelIssued = 'div[data-cy="label-issued"]'
    labelDrivers_license = 'div[data-cy="label-DRIVERS_LICENSE"]'
    labelElectoral_card = 'div[data-cy="label-ELECTORAL_CARD"]'
    labelNational_passport = 'div[data-cy="label-NATIONAL_PASSPORT"]'
    labelNational_id = 'div[data-cy="label-NATIONAL_ID"]'
    labelUnhcrId = 'div[data-cy="label-UNHCR ID"]'
    labelWfpId = 'div[data-cy="label-WFP ID"]'
    labelEmail = 'div[data-cy="label-Email"]'
    labelPhoneNumber = 'div[data-cy="label-Phone Number"]'
    labelAlternativePhoneNumber = 'div[data-cy="label-Alternative Phone Number"]'
    labelDateOfLastScreeningAgainstSanctionsList = 'div[data-cy="label-Date of last screening against sanctions list"]'
    labelLinkedGrievances = 'div[data-cy="label-Linked Grievances"]'
    labelSchoolEnrolled = 'div[data-cy="label-school enrolled"]'
    labelSchoolEnrolledBefore = 'div[data-cy="label-school enrolled before"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getLabelFullName(self) -> WebElement:
        return self.wait_for(self.labelFullName)

    def getLabelGivenName(self) -> WebElement:
        return self.wait_for(self.labelGivenName)

    def getLabelMiddleName(self) -> WebElement:
        return self.wait_for(self.labelMiddleName)

    def getLabelFamilyName(self) -> WebElement:
        return self.wait_for(self.labelFamilyName)

    def getLabelGender(self) -> WebElement:
        return self.wait_for(self.labelGender)

    def getLabelAge(self) -> WebElement:
        return self.wait_for(self.labelAge)

    def getLabelDateOfBirth(self) -> WebElement:
        return self.wait_for(self.labelDateOfBirth)

    def getLabelEstimatedDateOfBirth(self) -> WebElement:
        return self.wait_for(self.labelEstimatedDateOfBirth)

    def getLabelMaritalStatus(self) -> WebElement:
        return self.wait_for(self.labelMaritalStatus)

    def getLabelWorkStatus(self) -> WebElement:
        return self.wait_for(self.labelWorkStatus)

    def getLabelPregnant(self) -> WebElement:
        return self.wait_for(self.labelPregnant)

    def getLabelHouseholdId(self) -> WebElement:
        return self.wait_for(self.labelHouseholdId)

    def getLabelRole(self) -> WebElement:
        return self.wait_for(self.labelRole)

    def getLabelRelationshipToHoh(self) -> WebElement:
        return self.wait_for(self.labelRelationshipToHoh)

    def getLabelPreferredLanguage(self) -> WebElement:
        return self.wait_for(self.labelPreferredLanguage)

    def getLabelLinkedHouseholds(self) -> WebElement:
        return self.wait_for(self.labelLinkedHouseholds)

    def getLabelObservedDisabilities(self) -> WebElement:
        return self.wait_for(self.labelObservedDisabilities)

    def getLabelSeeingDisabilitySeverity(self) -> WebElement:
        return self.wait_for(self.labelSeeingDisabilitySeverity)

    def getLabelHearingDisabilitySeverity(self) -> WebElement:
        return self.wait_for(self.labelHearingDisabilitySeverity)

    def getLabelPhysicalDisabilitySeverity(self) -> WebElement:
        return self.wait_for(self.labelPhysicalDisabilitySeverity)

    def getLabelRememberingOrConcentratingDisabilitySeverity(self) -> WebElement:
        return self.wait_for(self.labelRememberingOrConcentratingDisabilitySeverity)

    def getLabelSelfCareDisabilitySeverity(self) -> WebElement:
        return self.wait_for(self.labelSelfCareDisabilitySeverity)

    def getLabelCommunicatingDisabilitySeverity(self) -> WebElement:
        return self.wait_for(self.labelCommunicatingDisabilitySeverity)

    def getLabelDisability(self) -> WebElement:
        return self.wait_for(self.labelDisability)

    def getLabelBirth_certificate(self) -> WebElement:
        return self.wait_for(self.labelBirth_certificate)

    def getLabelIssued(self) -> WebElement:
        return self.wait_for(self.labelIssued)

    def getLabelDrivers_license(self) -> WebElement:
        return self.wait_for(self.labelDrivers_license)

    def getLabelElectoral_card(self) -> WebElement:
        return self.wait_for(self.labelElectoral_card)

    def getLabelNational_passport(self) -> WebElement:
        return self.wait_for(self.labelNational_passport)

    def getLabelNational_id(self) -> WebElement:
        return self.wait_for(self.labelNational_id)

    def getLabelUnhcrId(self) -> WebElement:
        return self.wait_for(self.labelUnhcrId)

    def getLabelWfpId(self) -> WebElement:
        return self.wait_for(self.labelWfpId)

    def getLabelEmail(self) -> WebElement:
        return self.wait_for(self.labelEmail)

    def getLabelPhoneNumber(self) -> WebElement:
        return self.wait_for(self.labelPhoneNumber)

    def getLabelAlternativePhoneNumber(self) -> WebElement:
        return self.wait_for(self.labelAlternativePhoneNumber)

    def getLabelDateOfLastScreeningAgainstSanctionsList(self) -> WebElement:
        return self.wait_for(self.labelDateOfLastScreeningAgainstSanctionsList)

    def getLabelLinkedGrievances(self) -> WebElement:
        return self.wait_for(self.labelLinkedGrievances)

    def getLabelSchoolEnrolled(self) -> WebElement:
        return self.wait_for(self.labelSchoolEnrolled)

    def getLabelSchoolEnrolledBefore(self) -> WebElement:
        return self.wait_for(self.labelSchoolEnrolledBefore)
