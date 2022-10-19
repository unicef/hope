Feature: Feedback
    Checks, if creating and editing Feedback works.

    Background:
        Given I am authenticated

    Scenario: Visit Feedback page and create and edit Feedback
        When I visit the main dashboard
        Then I should see the side panel with Feedback option
        When I click on Feedback option
        Then I should see the Feedback page
        When I click the Submit New Feedback button
        Then I should see the New Feedback page
        When I fill in the form and save
        Then I should see the Feedback details page
        When I edit the Feedback and save
        Then I should see the updated Feedback
