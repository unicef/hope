# Via Excel import

**Feature details:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50070](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50070)

### Motivation

Many times data for households and individuals is obtained via flat or CSV or excel files.

### Import template

To ease the import process, we need to provide a template to users of how they should structure the data to get the data imported into HCT MIS. A HCT user should be able to download this template anytime they would like. This is **not a hardcoded file** being downloaded, but dynamically generated based on the set of core/flex fields as they exist in the system at that point.

Primarily this template will consist of two tabs: one called "**households**" and one called "**individuals**".

Within each tab there will be set of columns, one set for core fields and one for the active flex fields that HCT recognizes.

Additionally household tab will have a "**unique\_id**" as its first column. This will then be referenced in the individuals tab as a "household\_unique\_id" reference since individuals being imported have to belong to a \(valid\) household always.

### Acceptance Criteria

* [ ] 
