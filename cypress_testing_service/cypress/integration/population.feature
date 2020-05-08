Feature: Search and Filter Households / Individuals in the Population tab.

    Primary function here to to search/filter/sort columns etc. of the households
    and individuals that are part of the golden record.

    Background:
        # Given I login to AD as country_admin
        Given I login with mocked cookies
        Then I see user profile menu

    Scenario: Search Households in 'HCT MIS DB'
        Given the User is viewing the Population Household details screen
        When the User enters alphanumeric string in search field
        Then a list of the Housholds that meet the text in search is shown

    # Scenario: Filter Households in 'HCT MIS DB'
    #     Given User is viewing the Population Household Details screen
    #     When A user makes at least one selection of filters available
    #     Then System will return a list of the Households that meet the criteria selected in the filters

    # # Scenario: Click on a household and verify that requisite information is present
    # #     When I click on a household
    # #     Then

    # Scenario: Search Individuals in 'HCT MIS DB'
    #     Given User is viewing the Population Individuals Details screen
    #     When A User enters alphanumeric string in Search Field
    #     Then System will return a list of the Individuals that meet the text in search

    # Scenario: Filter Individuals in 'HCT MIS DB'
    #     Given User is viewing the Population Individuals Details screen
    #     When A user makes at least one selection of filters available
    #     Then System will return a list of the Individuals that meet the criteria selected in the filters

# Scenario: Click on an individual and verify that requisite information is present
#     When I click on a individual
#     Then
