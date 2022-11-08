Feature: Communication
    Checks, if creating a Communication message works.

    Background:
        Given I am authenticated


    Scenario: Visit Communication page and create a message
        When I visit the main dashboard
        Then I should see the side panel with Communication option
        When I click on Communication option
        Then I should see the Communication page
        When I click the New Message button
        Then I should see the New Message page
        When I fill in the form and save
        Then I should see the Message details page
