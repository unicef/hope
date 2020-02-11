# Registration Data Import

## Overview

The Registration Data Import module is the gateway for importing new data to the HCT-MIS database, shared with other applications.

Users will have the ability to import registered data from external tools and applications \(like Kobo\) or a raw import \(via an excel file that follows a specific template\), deduplicate and clean the information in a staging environment before having the ability to accept new data into HCT-MIS database.

## Import

The user can import data in two ways:

* Excel upload \(based on a template provided\)
* Import from 3rd party \(Kobo only for now\).

This import goes into a 'staging area' and not usable for targeting right away.

The states of an import:

* Pending
* In Review
* Approved

## Data Export

The system will allow the user to download a CSV file of a particular import, minus any PII.

## Cleaning

Cleaning data is basically editing the data imported.

From a system perspective cleaning is comparing, reporting, and accepting new data to data that is stored in both the staging and golden record of the HCT-MIS System.

The system will potentially highlight any issues with the data such as \(_these are ideas_\):

* Blank fields such as name or address.
* Deviation in numerical values from standard deviation in an import. Not a high priority.

## Flagging

The user will also be able to mark an imported household as being non-compliant. Hence it would not be synced with HCT MIS core population dataset.



