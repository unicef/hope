# Excel Import

**Feature details:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50070](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50070)

## Motivation

Many times data for households and individuals is obtained via flat or CSV or excel files. These files may have been obtained by their own independent registration efforts using some other systems. These files could also have been shared by other agencies with UNICEF as a way of sharing data.

The goal is to leverage this data to seed the golden record / population data within HCT MIS, so that programmes can be run for the households by targeting the population based on certain criteria.

## **Functional Specifications**

### Import template

To ease the import process, we need to provide a template to users of how they should structure the data to get the data imported into HCT MIS. A HCT user should be able to download this template anytime they would like. This is **not a hardcoded file** being downloaded, but dynamically generated based on the set of core/flex fields as they exist in the system at that point.

Primarily this template will consist of two tabs: one called "**households**" and one called "**individuals**".

Within each tab there will be set of columns, one set for core fields and one for the active flex fields that HCT recognizes. 

* The first row should not be modified by the user since this helps us programmatically identify what data is being uploaded.
* The second row has human readable version of it, along with the "data type" and any other helpful hints of what data is permissible to upload.

Additionally household tab will have a "**unique\_id**" as its first column. This will then be referenced in the individuals tab as a "household\_unique\_id" reference since individuals being imported have to belong to a \(valid\) household always.

{% hint style="info" %}
**See sample &lt;&lt;** [**Registration Data Import XLS Template**](https://docs.google.com/spreadsheets/d/1uNXQmOJd7eZC8Q-4IJ0iYGpvOjvfjRIe43eIN6dkFDg/edit?usp=sharing) **&gt;&gt;**
{% endhint %}

### **Import Process**

When selecting `Excel` as the file type for information to be imported from, an Upload File field will be made present, allowing a user to select a file from their local drive to be ingested into the HCT-MIS staging database.

Before being able to complete the import process, the following criteria must be met:

* File Data must comply with HCT-MIS data import template.
* Import batch must be named.

The following options are also available to the user during File Import:

* \(Optional\) Tags may be applied to the file for future referencing.
* ~~\(Optional\) The ability to select an existing Programme within the HCT-MIS system for this this file should be associated with.~~

Once a file is selected to be imported, a load screen will be presented where the `Upload File` message once was.

During this time, the selected file will be analyzed for any potential issues and will display the following details for the user's convenience:

* **\[\#\] Households** Available to Import
* **\[\#\] Individuals** Available to Import
* **Registration Start Date** - Earliest Registered Date recorded
* **Registration End Date** - Last Registered Date recorded

Furthermore, for the user's convenience, and to ensure consistency in data is being met, the users will have the ability to download the approved data [import template](via-excel-import.md#import-template) by clicking a button on the bottom right of the modal.

## Edge Cases / Validation Steps

* [ ] File import data must match the format of the approved Import Template.
* [ ] The system should only support XLSx file type
* [ ] If an import template is used, user removes multiple not required columns, has data in the rest and imports, the import should be successful.
* [ ] The user gets an import template, but modifies row 1 for any of the columns to something invalid, the import should fail.
* [ ] If any required fields are missing in the excel file being imported, the import should error out.

## Open issues

* It may be beneficial in the import template that is given to user, to have some sample data in it? Especially helpful where there are "select one" type fields, where choices could be not easy to guess/figure out?

## Future Enhancements / Out of scope

* Implementation of a wizard that read the excel column first and ask the user to map the columns in the next step.
* Further improvements can store common mapping for reuse, this will allow to not "freeze" the mapping today and grant the ability to be "open for changes" in case external systems change or new ones come.



