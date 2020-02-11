# De-duplicating data

**Feature details**: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50072](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50072)



{% hint style="info" %}
The current plans for deduplication within HCT-MIS can be found in this document, [**here**](https://unicef.sharepoint.com/:w:/r/teams/EMOPS-HCT-MIS/DocumentLibrary2/Modules%20-%20Components/Registration/Deduplication%20scenarios_ge.docx?d=w34184c05b28243ee81a9819410909daf&csf=1&e=x4R8n0)**.**
{% endhint %}



The goal of de-duplicating data is not to have duplicate households and individuals in the HCT MIS database.

### What is a duplicate?

It could be either:

* duplicates between the same import
* duplicate of some household already in the population \(HCT-MIS' golden DB\).

### Algorithm for finding duplicates

Attributes we care about:

* National ID
* Unicef ID
* Names
* DOB
* Number of people in household.
* Geographical location of individuals in the household.

### Handling duplicates

### Preservation of Data

As required by the Data Agreements, the system is required to keep records of the following information:

* x
* y
* z





### Issues

* How to handle N-way duplicate management?



