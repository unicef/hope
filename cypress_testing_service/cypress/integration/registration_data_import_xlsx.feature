Feature: Be able to download a template and upload households and individuals to
        be registered.

        Then be able to go through the workflow of approving and merging this to the
    golden record.

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

        # Given the User is prompted to select a file from the Import Excel screen
        #     And Import file selected is in XLSX format
        #     And File has no errors
        # When The User completes all required fields
        #     And Clicks 'Import'
        # Then The Import Modal dissapears
        #     And Information from file is added to Registration Datahub
        #     And A new Import Source is made in the Registration Datahub
        #     And The User is taken to the 'Import Preview' screen

# Scenario: Approving an import: Reviewed and ready to approve source of import data
#     Given The source of import data has been cleaned
#     And The User has Reviewed all import data content
#     When The User clicks 'Approve'
#     Then A Confirmation Modal screen displays to confirm the action or cancel process

#     Given Confirmation Modal to Approve Import Data is present
#     When The User clicks 'Approve'
#     Then The modal screen dissapears
#     And The Beneficiary data from the source in the 'Registration Datahub' is merged to the 'HCT MIS DB'

# Scenario: Unapprove an import: Approved Data is discovered to be faulty, and needs to be un-approved
#     Given The User is viewing an 'Approved' source of Import Data
#     When The User clicks the 'Unapprove' Button
#     Then A Confirmation Modal will display

#     Given The Confirmation Modal is present
#     When The User clicks the 'Unapprove' Button
#     Then The Confirmation Modal dissapears
#     And The source of Import Data is changes state from 'Approved' to 'In Review'
#     And 'Approve' Button is present on the Import Data Details screen.

# Scenario: Merging to golden record: Clean and Approved Import Data is merged to HCT Golden Records
#     Given The User has the appropriate role and permissions
#     And The source of Import Data is in the 'Approved' state
#     When The User clicks on 'Merge' Button
#     Then Import Source will be merged to HCT Datahub Golden Records

# # Scenario: Verify that the data uploaded is visible in the golden record (population tab)
