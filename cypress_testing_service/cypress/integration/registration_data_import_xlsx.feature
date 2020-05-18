Feature: Be able to download a template and upload households and individuals to be registered.

    Also be able to go through the workflow of approving and merging this to the golden record.

    Verify that the data uploaded is visible in the golden record (population tab)
    then via a deterministic search.

    Background:
        Given I login to AD as country_admin
        Then I see user profile menu

    Scenario: Download Template: User successfully downloads Registration Template
        Given the User is viewing the Registration Data Import screen
        When the User starts to import new data
            And the User selects Excel as their import source
            And the User downloads template

        Then the XLSX file stored in the system is downloaded
            And the downloaded XLSX file has the Households, Individuals and Choices sheets

    Scenario: User successfully imports Beneficiary Registration Data
        Given the User is viewing the Registration Data Import screen

        When the User starts to import new data
            And the User selects Excel as their import source
            And the User uploads file
            And the file has no errors
            And the User completes all required fields
            And the User confirms the import

        Then the User is taken to the Import details screen
            And the information from uploaded file is visible

    Scenario: Approving an import: Reviewed and ready to approve source of import data
        Given the User has an RDI import in review
            And the User has reviewed all import data content

        When the User approves the RDI import
        Then the RDI import becomes approved

    Scenario: Unapprove an import: Approved Data is discovered to be faulty, and needs to be un-approved
        Given the User has an RDI import in review
            And the User approves the RDI import

        When the User unapproves the RDI import
        Then the RDI import changes status to in review

# Scenario: Merging to golden record: Clean and Approved Import Data is merged to HCT Golden Records
#     Given The User has the appropriate role and permissions
#     And The source of Import Data is in the 'Approved' state
#     When The User clicks on 'Merge' Button
#     Then Import Source will be merged to HCT Datahub Golden Records

# Scenario: Verify that the data uploaded is visible in the golden record (population tab)
