Feature: Create Payment Plan
    Checks, if creating a payment plan is possible

    Background:
        Given I am authenticated
        Given I have an active program
        Given I have target population in ready status
    # Given I am sure that my business area is payment plan applicable
    # query businessAreaData

    Scenario: Create Payment Plan
        When I visit the main dashboard
        Then I should see the side panel with Payment Module option
        When I click on Payment Module option
        Then I should see the Payment Module page
        When I click the New Payment Plan button
        Then I should see the New Payment Plan page
        When I fill out the form fields and save
        Then I should see the Payment Plan details page
