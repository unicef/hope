Feature: Grievance
    Checks, if creating and editing Grievance Ticket works.

    Background:
        Given I am authenticated


    Scenario: Visit Grievance page and create and edit Grievance (Referral)
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

      Scenario: Visit Grievance page and create an anonymous Grievance (Referral)
        When I visit the main dashboard
        Then I should see the side panel with Grievance option
        When I click on Grievance Tickets option
        Then I should see the Grievance page
        When I click the New Ticket button
        Then I should see the New Ticket page
        When I fill in the form without individual and household and save
        Then I should see the Grievance details page


    Scenario: Visit Grievance page and create a Grievance, approve and close the ticket (Individual Data Update)
        When I visit the main dashboard
        Then I should see the side panel with Grievance option
        When I click on Grievance Tickets option
        When I click the New Ticket button
        Then I should see the New Ticket page
        When I fill in the form individual data change and save
        Then I should see the Requested Data Change component with correct values
        When I change states and approve data
        Then I should see the ticket is closed
