Feature: Create Payment Plan
    Checks, if creating a payment plan is possible

    Background:
        Given I am authenticated
        Given I have an active program
        Given I have target population in ready status

    Scenario: Create Payment Plan
        When I fill in the form
        And I save it
        Then I should be redirected to /payment-plans/{id}
