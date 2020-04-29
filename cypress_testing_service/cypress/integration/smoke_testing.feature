Feature: Smoke tests
    Runs a few scenarios to ensure system is in general functional and no obviouos
    issues or bugs exist

    Background:
        Given I login to AD as country_admin

    Scenario: Login and click around without any issues
        When I visit /
        Then I should see the Dashboard
        When I visit /registration-data-import in current business area
        Then I see "List of Imports" on the page
        When I click Population in navigation
        Then I get taken to /population/household in current business area
        When I visit /target-population in current business area
        Then I see "Target Populations" on the page

#    Scenario: Check backend API is up and running
#        When I make a request to GraphQL endpoint
#        Then I get a 200 response
