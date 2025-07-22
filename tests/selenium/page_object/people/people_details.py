from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PeopleDetails(BaseComponents):
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
    labelRole = 'div[data-cy="label-Role"]'
    labelPreferredLanguage = 'div[data-cy="label-Preferred language"]'
    labelResidenceStatus = 'div[data-cy="label-Residence Status"]'
    labelCountry = 'div[data-cy="label-Country"]'
    labelCountryOfOrigin = 'div[data-cy="label-Country of Origin"]'
    labelAddress = 'div[data-cy="label-Address"]'
    labelVilage = 'div[data-cy="label-Vilage"]'
    labelZipCode = 'div[data-cy="label-Zip Code"]'
    labelAdministrativeLevel1 = 'div[data-cy="label-Administrative Level 1"]'
    labelAdministrativeLevel2 = 'div[data-cy="label-Administrative Level 2"]'
    labelAdministrativeLevel3 = 'div[data-cy="label-Administrative Level 3"]'
    labelAdministrativeLevel4 = 'div[data-cy="label-Administrative Level 4"]'
    labelGeolocation = 'div[data-cy="label-Geolocation"]'
    labelDataCollectingType = 'div[data-cy="label-Data Collecting Type"]'
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
    labelBirthCertificate = 'div[data-cy="label-Birth Certificate"]'
    labelIssued = 'div[data-cy="label-issued"]'
    labelDriverLicense = 'div[data-cy = "label-DriverLicense"]'
    labelElectoralCard = 'div[data-cy="label-Electoral Card"]'
    labelNationalPassport = 'div[data-cy="label-National Passport"]'
    labelNationalId = 'div[data-cy="label-National ID"]'
    labelUnhcrId = 'div[data-cy="label-UNHCR ID"]'
    labelWfpId = 'div[data-cy="label-WFP ID"]'
    labelEmail = 'div[data-cy="label-Email"]'
    labelPhoneNumber = 'div[data-cy="label-Phone Number"]'
    labelAlternativePhoneNumber = 'div[data-cy="label-Alternative Phone Number"]'
    labelDateOfLastScreeningAgainstSanctionsList = 'div[data-cy="label-Date of last screening against sanctions list"]'
    labelLinkedGrievances = 'div[data-cy="label-Linked Grievances"]'
    labelWalletName = 'div[data-cy="label-Wallet Name"]'
    labelBlockchainName = 'div[data-cy="label-Blockchain Name"]'
    labelWalletAddress = 'div[data-cy="label-Wallet Address"]'
    labelCashReceived = 'div[data-cy="label-Cash received"]'
    labelTotalCashReceived = 'div[data-cy="label-Total Cash Received"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableLabel = 'span[data-cy="table-label"]'
    statusContainer = 'div[data-cy="status-container"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    labelSource = 'div[data-cy="label-Source"]'
    labelImportName = 'div[data-cy="label-Import name"]'
    labelRegistrationDate = 'div[data-cy="label-Registration Date"]'
    labelUserName = 'div[data-cy="label-User name"]'

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

    def getLabelRole(self) -> WebElement:
        return self.wait_for(self.labelRole)

    def getLabelPreferredLanguage(self) -> WebElement:
        return self.wait_for(self.labelPreferredLanguage)

    def getLabelResidenceStatus(self) -> WebElement:
        return self.wait_for(self.labelResidenceStatus)

    def getLabelCountry(self) -> WebElement:
        return self.wait_for(self.labelCountry)

    def getLabelCountryOfOrigin(self) -> WebElement:
        return self.wait_for(self.labelCountryOfOrigin)

    def getLabelAddress(self) -> WebElement:
        return self.wait_for(self.labelAddress)

    def getLabelVilage(self) -> WebElement:
        return self.wait_for(self.labelVilage)

    def getLabelZipCode(self) -> WebElement:
        return self.wait_for(self.labelZipCode)

    def getLabelAdministrativeLevel1(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel1)

    def getLabelAdministrativeLevel2(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel2)

    def getLabelAdministrativeLevel3(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel3)

    def getLabelAdministrativeLevel4(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel4)

    def getLabelGeolocation(self) -> WebElement:
        return self.wait_for(self.labelGeolocation)

    def getLabelDataCollectingType(self) -> WebElement:
        return self.wait_for(self.labelDataCollectingType)

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

    def getLabelBirthCertificate(self) -> WebElement:
        return self.wait_for(self.labelBirthCertificate)

    def getLabelIssued(self) -> WebElement:
        return self.wait_for(self.labelIssued)

    def getLabelDriverLicense(self) -> WebElement:
        return self.wait_for(self.labelDriverLicense)

    def getLabelElectoralCard(self) -> WebElement:
        return self.wait_for(self.labelElectoralCard)

    def getLabelNationalPassport(self) -> WebElement:
        return self.wait_for(self.labelNationalPassport)

    def getLabelNationalId(self) -> WebElement:
        return self.wait_for(self.labelNationalId)

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

    def getLabelWalletName(self) -> WebElement:
        return self.wait_for(self.labelWalletName)

    def getLabelBlockchainName(self) -> WebElement:
        return self.wait_for(self.labelBlockchainName)

    def getLabelWalletAddress(self) -> WebElement:
        return self.wait_for(self.labelWalletAddress)

    def getLabelCashReceived(self) -> WebElement:
        return self.wait_for(self.labelCashReceived)

    def getLabelTotalCashReceived(self) -> WebElement:
        return self.wait_for(self.labelTotalCashReceived)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getLabelSource(self) -> WebElement:
        return self.wait_for(self.labelSource)

    def getLabelImportName(self) -> WebElement:
        return self.wait_for(self.labelImportName)

    def getLabelRegistrationDate(self) -> WebElement:
        return self.wait_for(self.labelRegistrationDate)

    def getLabelUserName(self) -> WebElement:
        return self.wait_for(self.labelUserName)
