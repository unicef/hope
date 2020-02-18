# Excel Import

**Feature details:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50070](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50070)

## Motivation

Many times data for households and individuals is obtained via flat or CSV or excel files.

## **Functional Specifications**

### Import template

To ease the import process, we need to provide a template to users of how they should structure the data to get the data imported into HCT MIS. A HCT user should be able to download this template anytime they would like. This is **not a hardcoded file** being downloaded, but dynamically generated based on the set of core/flex fields as they exist in the system at that point.

Primarily this template will consist of two tabs: one called "**households**" and one called "**individuals**".

Within each tab there will be set of columns, one set for core fields and one for the active flex fields that HCT recognizes.

Additionally household tab will have a "**unique\_id**" as its first column. This will then be referenced in the individuals tab as a "household\_unique\_id" reference since individuals being imported have to belong to a \(valid\) household always.

\*\*\*\*

### **Import Process**

When selecting `Excel` as the file type for information to be imported from, an Upload File field will be made present, allowing a user to select a file from their local drive to be ingested into the HCT-MIS staging database.

Before being able to complete the import process, the following criteria must be met:

* File Data must comply with HCT-MIS data [import template](via-excel-import.md#import-template).
* Import batch must be named.

The following options are also available to the user during File Import:

* \(Optional\) Tags may be applied to the file for future referencing.
* \(Optional\) The ability to select an existing Programme within the HCT-MIS system for this this file should be associated with.

Once a file is selected to be imported, a load screen will be presented where the `Upload File` message once was.

During this time, the selected file will be analyzed for any potential issues and will display the following details for the user's convenience:

* **\[\#\] Households** Available to Import
* **\[\#\] Individuals** Available to Import
* **Registration Start Date** - Earliest Registered Date recorded
* **Registration End Date** - Last Registered Date recorded

Furthermore, for the user's convenience, and to ensure consistency in data is being met, the users will have the ability to download the approved data [import template](via-excel-import.md#import-template) by clicking a button on the bottom right of the modal.



### Acceptance Criteria / Validation

* [ ] 
