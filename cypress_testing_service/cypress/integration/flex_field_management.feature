Feature: Upload KoBo export file in Django admin

    As an HQ Admin User
    I want to have the ability to upload a KoBo Registration File
    So that all HCT Users in various business areas can use a standardized set of
    flex fields

    Scenario: Upload a valid KoBo File through the Django admin
        Given I login to AD as hq_admin
        When the User navigates to Django Administration page
        Then the Site Administration page is shown

        When the User navigates to Flexible Attributes import section
            And the User imports a valid XLS file with flexible attributes
            And the XLS file is uploaded without errors

        Then the list of imported flexible attributes is shown

    Scenario: Upload an invalid KoBo File through the Django admin
        Given I login to AD as hq_admin
        When the User navigates to Django Administration page
        Then the Site Administration page is shown

        When the User navigates to Flexible Attributes import section
            And the User imports flexible attributes XLS file with empty label

        Then the XLS file is not uploaded
            And error messages about empty label is shown

# Remove Scenarios below (for now)

# Scenario: Upload a KoBo File through the Django Admin Tool
#     Given I login to AD as hq_admin
#     And The User is in the Django Admin Tool
#     When The User clicks ...
#     Then ... [Django Admin Confirms Upload Success]

#     When I click Logout in Django Admin
#     Then I should get redirected to login

# Scenario: Verify that the flexs fields uploaded are now available
#     Given I login to AD as country_admin

# Scenario: Update the flex fields via a new upload. This should add new flex fields,
#     disable some existing ones, add new options to existing ones etc.
#     Given I login to AD as hq_admin
#     And The User is in the Django Admin Tool
#     When The User clicks ...
#     Then ... [Django Admin Confirms Upload Success]

#     When I click Logout in Django Admin
#     Then I should get redirected to login

# Scenario: Verify that the flexs fields got updated appropriately
#     Given I login to AD as country_admin
