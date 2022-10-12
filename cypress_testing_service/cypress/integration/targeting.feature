Feature: Targeting
    Checks, if creating Target Population and statuses flow work.

    Background:
        Given I am authenticated
        Given There are individuals and households imported
        Given I have an active program

    Scenario: Visit Targeting page and create Target Population
        When I visit the main dashboard
        Then I should see the side panel with Targeting option
        When I click on Targeting option
        Then I should see the Targeting page
        When I click the Create New button
        Then I should see the Create Target Population page
        When I fill out the form fields and save
        Then I should see the Households table
        When I save the Target Population
        Then I should see the Target Population details page and status Open
        When I Lock Target Population
        Then I should see the Target Population details page and status Locked
        When I Send Target Population to HOPE
        Then I should see the Target Population details page and status Ready
