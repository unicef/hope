Feature: Create Payment Plan
    Checks the whole payment plan flow

    Background:
        Given I am authenticated
        Given There are individuals and households imported
        Given I have an active program
        Given I have target population in ready status
    # Given There are steficon rules provided # via admin panel
    # Given I am sure that my business area is payment plan applicable
    # query businessAreaData

    Scenario: Create Payment Plan
        When I visit the main dashboard
        Then I should see the side panel with Payment Module option
        When I click on Payment Module option
        Then I should see the Payment Module page
        When I click the New Payment Plan button
        Then I should see the New Payment Plan page
        When I fill out the form fields and save
        Then I should see the Payment Plan details page
        When I lock the Payment Plan
        Then I see the entitlements input
        When I choose the steficon rule
        And I apply the steficon rule
        # Then I see the entitlements calculated
        And I am able to set up FSPs
        Then I should see the Set up FSP page
        When I select only one Delivery Mechanism
        Then I should see the warning
        When I select more Delivery Mechanisms
        Then I should be able to assign FSPs





#TODO

# Then I see the volumes calculated
# When I lock the FSPs
# Then I should see the needed approvals etc
# When I approve, review, etc
# Then I am able to accept the Payment Plan
# And I am able to upload the reconciliation info
# When I download the zip archive
# And I unarchive it
# Then I should see that there are multiple xlsx files inside the archive
# When I fill the data in xlsx files with delivered quantities
# And I upload the xlsx files
# Then I should see that the delivered quantities are visible in the system
# And the Payment Plan is reconciled # TODO: show that on FE
