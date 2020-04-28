Feature: Authentication
    Scenario: Redirect to login screen if not logged in
        Given I visit /
        Then I should get redirected to login
    
    Scenario: Redirects to login screen if accessing internal url
        Given I visit /afghanistan/
        Then I should get redirected to login

    Scenario: Login user via AD and see dashboard
        Given I login to AD as country_admin
        When I visit /
        Then I should see the Dashboard

        When I visit /
        Then I should see the Dashboard
