# Import Data Details

**Feature details**: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50071](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50071)

## Motivation

HCT users have the need to ensure all information is being imported accurately from the field into the system. The Import File Details screen allows user to directly see what has been imported, with simple views that consolidate information into a summary and allow users to see rows of beneficiary household and individual data to be validated and [**approved**](approval-process.md). 

## Functional Specifications

A user can access the **Import Files Details** page by one of two ways:

* After successfully uploading an Import File to the Staging area.
* By Clicking a previously uploaded file from the [**Import Management Screen**](detail-screen-approval-process.md).

On this screen users will see the following elements on the User Interface:

* **Details Summary**
* **Import Preview**

### Details Summary

The details summary is a card located just below the header of the page. It retains the title: **"Import File Details"**.

Within this section, the system will generate a summary of the following details:

* **Status -** In Review / Approved
* **Source of Data**
* **Total Number of Households**
* **Total Number of Individuals**
* _% Correct - TBD_

\_\_

### Import Preview

The import Preview card is a table list view of all the data separated by two tabs:

* **Households**
* **Individuals**

#### 

#### Households

Within the **Household** tab, HCT users will be able to view the following details of the file that was imported:

* **Source ID**
* **Head of Household**
* **Household Size**
* **Location**
* **Date Collected**

\*\*\*\*

#### **Individuals**

Within the **Individuals** tab, HCT users will be able to view the following details of the file that was imported:

* **Source ID**
* **Name**
* **Age**
* **Sex**
* **Location**
* **Date Collected**

\*\*\*\*

To see how these files are cleaned and how duplicates are prevented, please see the page on [**de-duplicating data**](de-duplicating-data.md).

If everything looks good, and the user would like to proceed to merge this file into the HCT-MIS Golden Records they will follow the next steps outlined in the [**Approval Process**](approval-process.md).

## Acceptance Criteria

* [ ] Approve Button should only appear if the import is in review state.
* [ ] * [ ] 
## User Permissions



