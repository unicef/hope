Feature: Population Individuals
Checks if the user can navigate to Population Individuals page and go to Individual details page

Background:
  Given I am authenticated


Scenario: Visit Population Individuals page and Individual details page
  When I visit the main dashboard
  Then I should see the side panel with Population option
  When I click on Population option
  Then I should see Individuals and Households options
  When I click the Individuals option
  Then I should see the Individuals Page and the table
  When I click one of the table rows
  Then I should see the Individual details page
