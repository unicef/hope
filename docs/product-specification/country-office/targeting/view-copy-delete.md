# Target Population Details

## Future Details: 

* View/finalization: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50084](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50084)

## Motivation

The purpose of this section is to allow HCT users to review their target population results with realistic data. To insure their target population generates the important results they are looking for, the Target Populations details screen offers many features which you can see detailed in the specifications below. 

## Feature Specifications

In this section, we will review the details of a Target Population.

### Target Population Entries \(Household\) List

The information contained within this section should all be included within a single card on the UI.

**Card** **Header** = Target Population Entries  \(\[\#\] Households\)

Below the card header will display two tabs:

* Candidate List
* Final List

#### **Candidate List**

The candidate list will have the following details displayed:

* Table Columns:
  * **Household ID**
  * **Head of Household -** First Name + Last Name
  * **Household Size - \#**
  * **Admin Level**
  * **Location**
  * **Last Inspection**
  * **Programme**

This table will display up to 10 rows upon default.

#### Candidate List States

The candidate list will have two states:

* Draft
* Frozen

A candidate list will remain in the **Draft** State once the Target Population is first created until the user decides to freeze the list of results the chosen criteria has generated for the Target Population.

Once the Target Population Candidate List is Frozen, it will remain in the **`Candidate List`** state until **`Finalized`** . **More on this here.**

#### Final List

The final list will have the following details displayed:

* Table Columns:
  * **Household ID**
  * **Head of Household -** First Name + Last Name
  * **Household Size - \#**
  * **Admin Level**
  * **Location**
  * **Last Inspection**
  * **Programme**

The Final List tab will not display any data until the Target Population has run against Corticon Rule Engine.

The Final List information will come from the same data table as the Candidate List, however, it will display unique information and include new details sent from Corticon.



### Results

Based on the criteria that was either entered upon [**creation**](targeting-criteria.md) ****or [**other means**](manage-target-populations-edit-copy-delete.md) ****the details displayed in this section will change. 

{% hint style="warning" %}
This information will represent a snapshot until [**edited**](manage-target-populations-edit-copy-delete.md#editing-criteria).
{% endhint %}

The following details will be displayed on the Results Card:

* **Female Children \(\#\)**
* **Male Children \(\#\)**
* **Female Adults \(\#\)**
* **Male Adults \(\#\)**
* **Total Number of Households \(\#\)**
* **Targeted Individuals \(\#\)**

### Showing New Results

With time, the results of a Target Population can change, when new data is entered into the system. Since the results of a target population are a snapshot of when the criteria was first set, a new indicator will show on the Target Population List titled: **New Results Available**

Clicking on this indicator, will enable the Target Population to be [**edited**](manage-target-populations-edit-copy-delete.md#editing-criteria).

{% hint style="danger" %}
Information in the **Results** card sections will change according to which tab is selected at the top of the screen \(**Candidate List** vs. **Final List**\). These details are still TBD.
{% endhint %}



### Freeze Candidate List

On the top-right corner of the Target Population Details screen there will be a button titled: **`Freeze`**. When a user clicks this button, a modal will appear, warning the user if they wish to proceed.

If the user decides to proceed, they will be able to select from a dropdown menu, any **`Active`**Programmes they wish to associate to this Target Population.

Selecting the **`Freeze`** option from the modal to continue will send the Target Population into the **`Candidate List`** \(state from the previous **`Draft`** state\). This will lock in the criteria for this target population and prevent any further changes being made with the selection of beneficiaries \(households\) identified in this target population. 

Furthermore, the "Candidate List" tab will change from the **`Draft`** state to the **`Freeze`** state, therefore the text "Draft" will be removed from the label on the UI \(_This is in regards to the label in the tab adjacent to the Final List Tab.\)_

Once the Target Population is in the **`Candidate List`** state, the user will now be able to run the target population in Corticon to generate additional details such as Vulnerability Scores, and more. 

{% hint style="danger" %}
**NOTE:** How Corticon will connect with HCT-MIS system and what details it will provide are still to be determined. 
{% endhint %}

Lastly, the button on the top-right, will change from **`Freeze`** to **`Finalize`** . See the next section for details regarding the Finalize process.

### Finalize

When the user is ready to complete the Target Population and send the results to Cash Assist, they will need to first Finalize the Target Population. To do so, the user will need to click on the button `Finalize` on the top-right of the UI and confirm their intentions through a modal popup.

#### Finalize Modal

The finalize Modal that pops up will list the total number of households being pushed to Cash Assist. The user will have the option to `Finalize` or `Cancel` . 

The **`Finalize`** button will lock in the criteria for this target population and push the resulting Households to CashAssist.

This is the last step in the process for creating and sharing a Target Population with Cash Assist. 

### 

### Open In CashAssist

Users will now have the ability to quickly navigate to the Target Population in CashAssist by simply clicking on the **`Open in CashAssist`** button on a Finalized Target Population details screen. This button will be located in the same position the **`Freeze`** and **`Finalize`** button were previously; the top-right of the screen. 

Further details regarding the  **`Finalized`** Target Population can be viewed in **CashAssist**. Clicking on the **`Open in CashAssist`** button will open the Target Population in Cash Assist in a new browser tab. 

## User Permissions



