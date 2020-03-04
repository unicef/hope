# Targeting Criteria \[Create\]

**Feature details:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50086](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50086)

## Motivation

HCT users will need to generate accurate calculations based on specific target populations within the MIS system shared with Cash Assist. In order to do so, they must first select the specific criteria that best represents their cash plans. By selecting specific targeting criteria in the Target Population create new feature.

## Feature Specifications

In this section we will review the following features of the Target Population Tab in detail:

* **Creating A Target Population**
* **Editing A Target Population**

\*\*\*\*

### Create New Target Population

Located in the top-right corner of the [**Target Population List**](./) screen is the **`Create New`** button.

Clicking the button will take you to a new screen, allowing HCT-MIS users to set their **Targeting Criteria** and to name their target. 

In order to create a new Target, users will need to complete the following fields on the create screen.

* Name Target Population
* Adding Criteria



#### Name Target  Population

Positioned at the top of the screen, the first thing a user should fill out is the Target Population Name.

{% hint style="info" %}
Tip on how to use good naming conventions for your Target Populations.

**Example:** _Date\_Location\_PopulationSummary_
{% endhint %}



### Adding Criteria

Just below the Target Population Name Field, is a new card titled "**Targeting Criteria"**

A blue box with text that reads "+ Add Criteria" will be present, this is how you being your first set of rules for the target population.

#### 

#### Setting Ands & Ors

Users will have the flexibility to set criteria for Target Populations in two ways. 

When first clicking on the **Add Criteria** button, a user will start a new set of **AND** criteria.

A modal will pop up on the UI and allow for the user to choose from a dropdown menu which field type they would like to select criteria from.

To end their **AND** criteria, the user must click the **`Save`**.

Once clicking the **`Save`** button the modal will disappear, and the user will see a summary of their criteria within the blue box. 

Along side of the previously selected criteria, a new box with a "+" sign will be present. The two boxes will be separated by a divider line with the word "**OR**" inside, indicating that a new set of criteria will be added as **OR** criteria. 

Once criteria is added and saved to the Target Population, the system will return data to be seen in the [**Results**](view-copy-delete.md) card and the [**Target Population Entries**](view-copy-delete.md) list. This data will continue to update until the user clicks the **`Save`** button on the [**Target Populations Details**](view-copy-delete.md) screen to end the creation of the new Target Population.



### 

### Core Fields

| **Group** | Field Type |
| :--- | :--- |
| Sex | Select Many |
| Location | Select Many |
| Age | Range |
|  |  |
|  |  |
|  |  |
|  |  |

### **Flex Fields**

| **Group** | Field Type |
| :--- | :--- |
| ID Type | Select One |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

### \*\*\*\*

### **Individual Fields**

| **Group** | Field Type |
| :--- | :--- |
| Intake Group | Select Many |
| Tags | Select Many |
| Programmes | Select Many |

### \*\*\*\*

## Acceptance Criteria

* [ ] The criteria must include core/flex fields that are within of the HCT-MIS Database
* [ ] The Target Criteria must include the groups of fields to the users before presenting the related fields which are subject to that specific group.
* [ ] All criteria must generate data that is representative of the specific Business Area the logged in user is associated with.
* [ ] 
## User Permissions



