Feature: Program
Checks if the user can create and activate a program

Background:
  Given I am authenticated


Scenario: Visit Programs page and creates a Program and activates
  When I visit the main dashboard
  Then I should see the side panel with Programme Management option
  When I click on Programme Management option
  Then I should see the Programs page
  When I click the New Programme button
  Then I should see the Set-up a new Programme modal
  When I fill out all the form fields
  And I click the save button
  Then I should see the Program details page
  When I click the activate button
  Then I should see the Activate Program Modal opened
  When I click the activate button in the modal
  Then I should see the Program is active
