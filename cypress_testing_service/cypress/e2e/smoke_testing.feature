Feature: Smoke tests
    Checks, if the main page returns something

    Scenario: Visit main page
        When I visit /
        Then I should see the AD login page

    Scenario: Login via admin panel
        When I visit admin panel
        And I fill in the login form
        Then I should see the admin panel contents
