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

    @createProgramme
    Scenario: Create a New Programme
        When User starts creating New Programme
        Then the New Programme form is shown

        When the User completes all required fields on the form
            And the User clicks the Save button
        Then the User is redirected to the new Programme Details screen
            And status of this Progrmame is Draft

    @removeProgramme
    Scenario: Remove Draft Programme
        Given the User is viewing existing Programme in Draft state
        When the User takes action to remove Programme
        Then the Programme is soft deleted
            And the Programme is no longer accessible

# Scenario: Activating a Programme
#     Given The User is viewing the details page of a 'Draft' Programme
#     When The User clicks 'Activate' Button
#     Then A Confirmation Modal displays

#     Given The Confirmation Modal is present
#     When The User clicks the 'Activate' Button
#     Then The Confirmation Modal dissapears
#     And The Programme state changes from 'Draft' to 'Active'
#     And The Programme can then be associated with a 'Closed' Programme Population in Targeting

# Scenario: Finish/Terminate an Active Programme
#     Given The User is viewing an Active Programme Detail screen
#     When The User clikc the 'Finalize' Button
#     Then A Confirmation Modal displays

#     Given The Confirmation Modal is present
#     When the User clicks 'Finalize' Button
#     Then The Confirmation Modal dissapears
#     And The Programme changes state from 'Active' to 'Finalized'
#     And The Programme will no longer be available to associated with new 'Closed' Programme Population in Targeting
