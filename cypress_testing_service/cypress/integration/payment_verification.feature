Feature: Payment Verification
Checks if the user can navigate to Payment Verification page and go to Cash Plan details page

Background:
  Given I am authenticated


Scenario: Visit Payment Verification page and Cash Plan details page
  When I visit the main dashboard
  Then I should see the side panel with Payment Verification option
  When I click on Payment Verification option
  Then I should see the List of Cash Plans
  When I click one of the table rows
  Then I should see the Cash Plan Details Page
