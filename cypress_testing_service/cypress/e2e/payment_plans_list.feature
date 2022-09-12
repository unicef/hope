Feature: Create Payment Plan
    Checks, if Payment Plans list renders

    Background:
        Given I am authenticated

    Scenario: See Payment Plans list
        When I visit the main dashboard
        Then I should see the side panel with Payment Module option
        When I click on Payment Module option
        Then I should see the Payment Module page
        And I should see Payment Plans list
