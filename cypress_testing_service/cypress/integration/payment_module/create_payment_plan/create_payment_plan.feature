Feature: Create Payment Plan
    Checks, if creating a payment plan is possible

    Background:
        Given I am on the New Payment Plan
        And I can see the form correctly displayed

    Scenario: Create Payment Plan
        When I fill in the form
        And I save it
        Then I should be redirected to /payment-plans/{id}
