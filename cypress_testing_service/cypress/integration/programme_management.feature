@ProgrammeManagement
Feature: Programme Management

    This feature allows creating a new programme, approve it and then it syncs with
    CashAssist.

    A draft program can be removed, or activated. An active program can be Finished
    as well.

    Background:
        # Given I login to AD as country_admin
        Given I login with mocked cookies
        Then I see user profile menu

    Scenario: Create a New Programme
        When User starts creating New Programme
        Then the New Programme form is shown

        When the User completes all required fields on the form
            And the User submits the form
        Then the User is redirected to the new Programme details screen
            And status of this Programme is Draft

    Scenario: Remove Draft Programme
        Given the User is viewing existing Programme in Draft state
        When the User removes the Programme
        Then the Programme is soft deleted
            And the Programme is no longer accessible

    Scenario: Activating a Programme
        Given the User is viewing existing Programme in Draft state
        When the User activates the Programme
        Then status of this Programme is Active
            # TODO test as targeting.feature scenario
            # And the Programme can then be associated with a 'Closed' Programme Population in Targeting

    Scenario: Finish an Active Programme
        Given the User is viewing existing Programme in Active state
        When the User finishes the Programme
        Then status of this Programme is Finished
            # TODO test as targeting.feature scenario
            # And The Programme will no longer be available to associated with new 'Closed' Programme Population in Targeting
