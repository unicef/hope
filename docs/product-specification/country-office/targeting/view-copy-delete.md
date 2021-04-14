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

* **Programme Population** \(Suggested: Programme Population \)
* **Target Population** \(Final List\)

#### **Programme Population**

The Programme Population will have the following details displayed:

* Table Columns:
  * **Household ID**
  * **Head of Household -** First Name + Last Name
  * **Household Size - \#**
  * **Admin Level**
  * **Location**
  * **Last Inspection**
  * **Programme**

This table will display up to 10 rows upon default.

#### Programme Population States

The Programme Population will have two states:

* Open
* Closed

A Programme Population will remain in the **Open** State once the Target Population is first created until the user decides to **Close** the list of results the chosen criteria has generated for the Target Population.

Once the Target Population Programme Population is Closed, it will remain in the **`Closed`** state until **`Sent`** . **More on this here.**

#### Target Population \(Final List\)

The Target Population \(final list\) will have the following details displayed:

* Table Columns:
  * **Household ID**
  * **Head of Household -** First Name + Last Name
  * **Household Size - \#**
  * **Admin Level**
  * **Location**
  * **Last Inspection**
  * **Programme**

The Target Population \(Final List\) tab will display the same data as the Programme Population until the Target Population has run against Corticon Rule Engine or additional Target Criteria are added to the Target Population.

The Target Population \(Final List\) information will come from the same data table as the Programme Population, minus any households that meet the new criteria added in the tab. The table will also display unique information and include new details sent from Corticon, including vulnerability score and the rules that were applied from the system. 



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
Information in the **Results** card sections will change according to which tab is selected at the top of the screen \(**Programme Population** vs. **Target Population\(Final List\)**\). These details are still TBD.
{% endhint %}



### Close Programme Population

On the top-right corner of the Target Population Details screen there will be a button titled: **`Close`**. When a user clicks this button, a modal will appear, warning the user if they wish to proceed.

If the user decides to proceed, they will be able to select from a dropdown menu, any **`Active`**Programmes they wish to associate to this Target Population.

Selecting the **`Close`** option from the modal to continue will send the Target Population into the **`Programme Population`** \(state from the previous **`Open`** state\). This will lock in the criteria for this Programme population and prevent any further changes being made with the selection of beneficiaries \(households\) identified in this target population. 

Furthermore, the "Programme Population" tab will change from the **`Open`** state to the **`Closed`** state.

Once the Programme Population is in the **`Closed`** state, the user will now be able to run the Target Population in Corticon to generate additional details such as Vulnerability Scores, and more. 

{% hint style="danger" %}
**NOTE:** How Corticon will connect with HCT-MIS system and what details it will provide are still to be determined. 
{% endhint %}

Lastly, the button on the top-right, will change from **`Close`** to **`Send to CashAssist`** . See the next section for details regarding the Send to CashAssist process.

### Send to Cash Assist

When the user is ready to complete the Target Population and send the results to Cash Assist, they will need to first Close the Programme Population. When all the criteria are set, and the user is completed adding their criteria to the Target Population, they can send the final results to Cash Assist. To do so, the user will need to click on the button `Send to CashAssist` on the top-right of the UI and confirm their intentions through a modal popup.

#### Send to CashAssist Modal

The Send to CashAssist Modal that pops up will list the total number of households being pushed to Cash Assist. The user will have the option to **`Send`** or `Cancel` . 

The **`Send`** button will lock in the criteria for this target population and push the resulting Households to CashAssist.

This is the last step in the process for creating and sharing a Target Population with Cash Assist. 

### 

### Open In CashAssist

Users will now have the ability to quickly navigate to the Target Population in CashAssist by simply clicking on the **`Open in CashAssist`** button on a `Sent` Target Population details screen. This button will be located in the same position the `Close` and `Send to CashAssist` button were previously; the top-right of the screen. 

Further details regarding the  `Sent` Target Populations can be viewed in **CashAssist**. Clicking on the **`Open in CashAssist`** button will open the Target Population in Cash Assist in a new browser tab. 

## User Permissions



