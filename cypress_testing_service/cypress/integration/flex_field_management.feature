Feature: Upload KoBo export file in Django admin

    As an HQ Admin User
    I want to have the ability to upload a KoBo Registration File
    So that all HCT Users in various business areas can use a standardized set of
    flex fields

    Background:
        Given I login once to AD as hqAdmin
        When the User navigates to Django Administration page
        Then the Site Administration page is shown

    Scenario: Upload a valid KoBo File through the Django admin
        When the User navigates to Flexible Attributes import section
            And the User imports a valid XLS file with flexible attributes
            And the XLS file is uploaded without errors

        Then the list of imported flexible attributes is shown

    Scenario: Upload a modified KoBo File through the Django admin
        When the User navigates to Flexible Attributes import section
        When the User imports a valid XLS file with default dairy_h_f attribute
            And the XLS file is uploaded without errors
        Then the dairy_h_f attribute has default value

        When the User navigates to Flexible Attributes import section
            And the User imports a valid XLS file with modified dairy_h_f attribute
            And the XLS file is uploaded without errors
        Then the dairy_h_f attribute has modified value

    Scenario: Upload an invalid KoBo File (with empty labels) through the Django admin
        When the User navigates to Flexible Attributes import section
            And the User imports flexible attributes XLS file with empty label

        Then the XLS file is not uploaded
            And error message about empty label is shown

    Scenario: Upload an invalid KoBo File (with choices without name) through the Django admin
        When the User navigates to Flexible Attributes import section
            And the User imports flexible attributes XLS file containing choices without name

        Then the XLS file is not uploaded
            And error message about required name is shown
