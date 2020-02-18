---
description: >-
  Once the information is reviewed on the interface, HCT users will have the
  option to approve the data file being examined before allowing it to merge
  with the golden records.
---

# Approval Process

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

~~If the entire file is not approved, the following message will appear.~~ 

~~_**\[\#\] Households have not been validated, move to new import?**_~~

~~In order to proceed, the user must first name the new import file that will be added to the~~ [~~**Import Management**~~](detail-screen-approval-process.md) ~~****screen to repeat the process.~~

~~Once all is reviewed and confirmed, the user will be able to click either the `Cancel` button or `Approve` button.~~



### Un-Approval

### Merge to population

### Notifications

A snackbar message will then appear for approx. 5 seconds confirming whether or not the import was successful or not. 

_\*\*\*\*_

#### 

## Acceptance Criteria

* [ ] 
## ~~User Permissions~~

~~~~[~~**Roles & Permissions**~~](../user-management/user-roles-and-permissions.md)~~\*\*\*\*~~

~~The following users should be able to interact with the following Populations features and functionalities.~~

* ~~&lt;User type 1&gt;~~
* ~~&lt;User type 2&gt;~~

#### ~~&lt;User Type 1&gt;~~

~~This user has the ability to import registered beneficiary data into the HCT-MIS Staging Environment~~ 

#### ~~&lt;User Type 2&gt;~~

~~This user has the ability to review and approve all import batches of Registered beneficiary data from the Staging environment to the Golden Records.~~





