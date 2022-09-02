Feature: Program
Checks if the user can navigate to Individuals page and go to Individual details page

Background:
  Given I am authenticated


Scenario: Visit Programs page and creates a Program and activates
  When I visit the main dashboard
  Then I should see the side panel with Population option
  When I click on Population option
  Then I should see Individuals and Households options
  When I click the Individuals option
  Then I should see the Individuals Page
  When I click one of the table rows
