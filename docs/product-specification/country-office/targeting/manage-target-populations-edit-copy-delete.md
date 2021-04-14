# Manage Target Populations \[Edit / Copy / Delete\]

**Feature Details**

* Edit: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50086](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50086)
* Copy/delete: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50085](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50085)

## Motivation

Many times, users will need to manage their Target Populations, therefore a need to copy or delete existing Target Populations is a feature detailed in the Specifications below. 

## Feature Specifications

In this section, we will review the details of a Target Population, including how to copy & delete saved Target Populations in the HCT-MIS System. 

### Editing Criteria

In order to edit a Programme or Target Population's criteria, a user must first visit the [**Details**](view-copy-delete.md) page of their selected Target Population and click the **`Edit`** button located on the top-right of the screen. 

This will enable the user to edit the Title of the Target Population as well as it's Targeting Criteria.

A user may **delete** a group of **AND** criteria by simply clicking on the _trash can symbol_ in the top-right corner of the selected criteria box. 

Alternatively, a user can **edit** the selected **AND** criteria by selecting the edit button, which will bring up the Add Criteria modal and all it's pre-set rules available to adjust/change.

The user may also add more **OR** criteria if desired.

**NOTE:** The UI will not change from what was previously seen on the [**Create New Target Population**](targeting-criteria.md#create-new-target-population) screens.

### 

### Copy Target Populations

In order to **Copy** a Target Population and it's criteria, a user must first visit the **Target Population Details** page of their selected Target Population and click the **`Copy`** button \(icon\) located on the top-right of the screen, next to a `delete` / `edit` / `close` buttons respectively. 

A modal screen will prompt the user to fill in a new name of the duplicate Target Population before moving forward. Once a user has added a new title they can proceed with the duplicate by selecting `Save`. This will generate a new Target Population with the same criteria selected as well as a snapshot of the data preserved in the duplicated Target Population. Once the criteria is changed, or any other manipulations to the data occur, the Target Population will begin to take in new results from the most recent data in the Population database. 

From here, all the steps are the same as seen in the [**Create New Target Population**](targeting-criteria.md#create-new-target-population) section.



### Delete Target Populations

In order to **Delete** a Target Population, a user must first visit the **Target Population Details** page of their selected Target Population and click the **`Delete`** icon located on the top-right of the screen, next to a `copy` / `edit` / `close` buttons respectively. 

This will remove the Target Population from the system.\* 

{% hint style="info" %}
\*This deletion is considered a soft delete.
{% endhint %}

## Acceptance Criteria

* [ ] Copying a Target Population is possible for both `In Progress` and `Finalized` status. 
* [ ] A user cannot delete a `Finalized` \(status\) Target Population from the HCT-MIS System.

