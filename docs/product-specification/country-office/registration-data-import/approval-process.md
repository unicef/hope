---
description: >-
  Once the information is reviewed on the interface, HCT users will have the
  option to approve the data file being examined before allowing it to merge
  with the golden records.
---

# Approval Process

**Feature details**: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50071](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50071)

## Motivation

HCT must be able to restrict the information that is being ingested into the system in order to validate whether or not it is acceptable to be merged into the golden database. To do this, HCT-MIS only allows certain users privilege to merge imported data to the golden records from the staging environment. To further ensure this process is done with intention, the privileged users will have to interact with the various interface prompts described below

## Functional Specifications

Starting from any given [**Import File Details**](import-file-details.md) screen, a user will be able to see a button located at the top-right of the page, titled "Approve".

Clicking on this button will prompt a modal with the following details.

### Approve Modal Details

#### Card Title

The title of this modal will be:

* **Approve Import File**



#### Body Content

Within the body of this card, users will have a final chance to review a summarized details of the file they are attempting to merge with the Golden Records.

Security check 1:

A message will display asking the user the following question:

_"Are you sure you want to approve this data import?"_

Below this question, the system will have the following summary:

_**\[\#\] Households and \[\#\] Individuals will be approved. Do you want to Proceed?**_ 

{% hint style="info" %}
~~**Struckout**~~  section below is TBD
{% endhint %}

~~If the entire file is not approved, the following message will appear.~~ 

~~_**\[\#\] Households have not been validated, move to new import?**_~~

~~In order to proceed, the user must first name the new import file that will be added to the~~ [~~**Import Management**~~](detail-screen-approval-process.md) ~~****screen to repeat the process.~~



Once all is reviewed and confirmed, the user will be able to click either the **`Cancel`** button or **`Approve`** button.



### Un-Approval

Once a batch of imported Registered Data is approved, an action to undo or more specifically `Un-Approve` will become available to users when viewing the Import Data Details screen set to this state.



### Merge to population

Finally, users will have the ability to sync approved data to the Golden Records by clicking the **`Merge to Population`** button on the top-right of the page.

### Notifications

A snackbar message will then appear for approx. 5 seconds confirming whether or not the import was successful or not. 

For further details on notifications please see [**documentation here**](../../snackbar-notifications.md#registration-data-import).

_\*\*\*\*_

## Acceptance Criteria

* [ ] **Approve** button cannot appear for Imported Data with set status of `Approved` 
* [ ] The ability to **Un-Approve** a batch of Registered Data can only be available when that data's status is set to `Approved` 
* [ ] The ability to **Merge to Population** a batch of Registered Data can only be available when that data's status is set to `Approved` 
* [ ] Once the population has been merged, there are no further actions that can be taken on this data import.

## ~~User Permissions~~

~~~~[~~**Roles & Permissions**~~](../user-management/user-roles-and-permissions.md)~~\*\*\*\*~~

~~The following users should be able to interact with the following Populations features and functionalities.~~

* ~~&lt;User type 1&gt;~~
* ~~&lt;User type 2&gt;~~

#### ~~&lt;User Type 1&gt;~~

~~This user has the ability to import registered beneficiary data into the HCT-MIS Staging Environment~~ 

#### ~~&lt;User Type 2&gt;~~

~~This user has the ability to review and approve all import batches of Registered beneficiary data from the Staging environment to the Golden Records.~~





