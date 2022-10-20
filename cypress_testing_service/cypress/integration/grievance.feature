Feature: Grievance
    Checks, if creating and editing Grievance Ticket works.

    Background:
        Given I am authenticated

    Scenario: Visit Grievance page and create and edit Grievance
        When I visit the main dashboard
        Then I should see the side panel with Grievance option
        When I click on Grievance Tickets option
        Then I should see the Grievance page
        When I click the New Ticket button
        Then I should see the New Ticket page
        When I fill in the form and save
        Then I should see the Grievance details page
        When I edit the Grievance and save
        Then I should see the updated Grievance
