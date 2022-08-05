Feature: Registration Data Import
    Checks, if importing RDI populates the list of imports and if merging RDI works.

    Background:
        Given There are no RDI imports
        Given I am authenticated

    Scenario: Visit RDI page and import RDI data
        When I visit the main dashboard
        Then I should see the side panel with RDI option
        When I click on RDI option
        Then I should see the RDI page
        When I click the import button
        Then I should see the file import modal
        When I select the xlsx file
        Then I see it was chosen
        When I press import
        Then I should see a new import with status in review
        When I merge the import
        Then I see that the status is merging
        When I refresh the page
        Then I see that the status is merged
        When I visit the Households dashboard
        Then I see a newly imported household
        When I visit the Individuals dashboard
        Then I see the newly imported individuals