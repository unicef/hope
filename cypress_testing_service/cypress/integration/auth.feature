Feature: Authentication related functionality. Logging in, redirects
    to login etc. when user is not logged in and trying to access any urls.

    Also tests the logout functionality.

    TODO: Add functionality around the user profile itself one the feature works.

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
        Then I see my email address in the header

    Scenario: Logging out of HCT
        Given I login to AD as country_admin
        When I click Logout
        Then I should get redirected to login
