Feature: Surveys
    Checks, if creating a Survey works.

    Background:
        Given I am authenticated
        Given I have a Target Population
        Given I have a Program

    Scenario: Visit Surveys page and create one
        When I visit the main dashboard
        Then I should see the side panel with Surveys option
        When I click on Surveys option
        Then I should see the Surveys page
        When I click the New Survey button
        Then I should see the New Survey page
        When I fill in the form and save
        Then I should see the Survey details page
