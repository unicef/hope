Feature: Population Households
Checks if the user can navigate to Population Households page and go to Household details page

Background:
  Given I am authenticated


Scenario: Visit Population Households page and Household details page
  When I visit the main dashboard
  Then I should see the side panel with Population option
  When I click on Population option
  Then I should see Individuals and Households options
  When I click the Households option
  Then I should see the Households Page and the table
  When I click one of the table rows
  Then I should see the Household details page
