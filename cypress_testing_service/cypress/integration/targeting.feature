@Targeting
Feature: Target Population

  Background:
    # Given I login to AD as country_admin
    Given I login with mocked cookies
    Then I see user profile menu


  # Create New Programme Population
  # As a User
  # I want to create a new Programme Population based on Targeting Criteria
  # So I can create useful Cash Plans

  Scenario: Target Beneficiaries from the 'HCT MIS DB'
    Given the User is viewing the Targeting List screen
    When the User starts creating new Target Population
      And the User gives new Target Population a name
      And the User selects at least one Target Criteria
      And the User completes creating new Target Population

    Then the User will be directed to the Programme Population details screen
      And the Status of the Programme Population will be set to Open

  # Close Programme Population
  # As a User
  # I want to lock in the Beneficiary Data selected from my criteria set
  # So I can use it in CashAssist

  Scenario: Preparing potential list of beneficiaries to be added to a Cash Plan of a particular Program
    Given the User is viewing the Targeting List screen
    When the User starts creating new Target Population
      And the User gives new Target Population a name
      And the User selects at least one Target Criteria
      And the User completes creating new Target Population

    Then the User will be directed to the Programme Population details screen
      And the Status of the Programme Population will be set to Open
# Given The User is in the Programme Population Details screen
# When The User clicks 'Close' Button
# Then A Confirmation Modal display

# Given The Confirmation Modal is present
# When The User Selects a Programme from the dropdown list
# And The User clicks 'Close' Button on the Confirmation Modal
# Then The Confirmation Modal dissapears
# And The Programme Population state becomes 'Closed'
# And The User can no longer select the 'Edit' Button from the Programme Population Details screen
# And The Programme Population Details are locked
# And A Target Population is created with the same details from the Programme Population


# @Targeting
# Feature: Send Target Population to CashAssist

#     As a User
#     I want to send the final Target Populationt to CashAssist
#     So that it can be used for Programme Cash Plans

#     Scenario: Finalizing list of Targeted Beneficiaries to send to CashAssist
#         Given A User is viewing a 'Closed' Target Population
#         When The User clicks on the 'Send to CashAssist' Button
#         Then A Confirmation Modal will display

#         Given the Confirmation Modal is present
#         And the correct total amount of Households are displayed in the description text
#         When The User clicks 'Send to CashAssist'
#         Then The Confirmation Modal screen dissapears
#         And The Details for the Target Population are sent to CashAssist


# @Targeting
# Feature: Duplicate Programme Population

#     As a User I want to Duplicate the Target Criteria of a particular Programme Population

#     Scenario: Refresh Eligible Beneficiaries with Current Population in the 'HCT MIS DB'
#         Given The User is viewing the details of a 'Open' 'Closed' or 'Sent' Programme Population
#         When The User clicks the duplicate symbol located at the top-right of body
#         Then A Confirmation Modal screen will display

#         Given The Confirmation Modal is present
#         When The User completes all the required form fields
#         And The User clicks the 'Save' Button
#         Then The Confirmation Modal dissapears
#         And A new Create New Programme Population is started with the Title prefilled
#         And The User is directed to the new Create New Programme Population screen
