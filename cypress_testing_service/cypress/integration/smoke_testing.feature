Feature: Smoke tests
    Checks, if the main page returns something

    Scenario: Login and click around without any issues
        When I visit /
        Then I should see the AD login page


# When I visit /registration-data-import in current business area
# Then I see "List of Imports" on the page
# When I click Population in navigation
# Then I get taken to /population/household in current business area
# When I visit /target-population in current business area
# Then I see "Target Populations" on the page
