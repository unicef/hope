# Iteration 6

The goal of Iteration Six is to implement Payment Verification, Deduplication, and User Management.

**Expected start/end date:** July 6 - September 11, 2020 \(10 weeks\)

## **Architectural design / Project Management Deliverables**

* Sign-off the functional/technical specifications and flows for features to be implemented in later Iterations:
  * Registration Data Import deduplication process
  * Grievances & Feedback Section \(pending items\)
  * User Management Section
* Start discussion of Reports and Dashboard modules.
* Interface with core Kobo team on technical / testing details on any pending items like uploads being on blob storage.
* Maintain Project Roadmap / Timeline.
* Participate in briefing and workshop remotely or in-person as required by UNICEF
* RapidPro API conversations w/ UNICEF as necessary.

## **Technical Deliverables**

* Complete development of the **Payment Verification Module** according to the signed off requirements from Iteration 5:
  * Search & Filter a Table List view of Verifications for Cash Plans.
  * Cash Plan Payment Verification Details to display verification process details.
  * Verification Planning, allowing users to choose between verifying a full list vs a Random Sample and the following methods to collect verification:
    * RapridPro
    * XLSX export/import
    * Manual Entry
  * Verification Details screen showing the progress details of a Verification Plan.
  * Manual Verification entry form accessed through the individual Payment Record selected for verification.
  * Data model changes to accommodate the handling of Verification ID
  * Changes to Population &gt; Household &gt; Payment Record Details to show verification.
* Complete the development of the **User Management Module** according to the signed off spec from Iteration 5
  * * UI for adding/managing users
    * Not implementing Roles & Permissions
* Complete the development of the **Registration Data Import Module** to accommodate for **Deduplication** according to the signed off spec from Iteration 5
  * Within a batch/import \(RDI instance\)
  * Pre-merge duplication against the golden record
  * Creation of grievance tickets based on above \(no UI for the ticket in this iteration\).
* Complete the development of the **Sanctions List Check** functionality according to signed off spec from Iteration 5
  * Flagging of batch/import records against the sanctions list.
  * Flagging of Golden Records against the sanctions list.

## **UX / UI Design Deliverables**

* Design tweaks to some design deliverables from iteration 5 \(including new items like user management screens for iteration 6 development to happen or feedback & grievances for which some things like data change category are being still specified in detail\)
* Design final clickable prototype of Payment Verification and Grievances/Feedback Tab
* Continued general upkeep of mockups to represent what is decided/built.
* Demo for peer review with country offices \(as/if required\).

## **UNICEF Dependencies**

‌ Following are the dependencies Tivix team has on UNICEF teams in order to deliver on time.

* UNICEF team to provide working in-country RapidPro setup for all HCT MIS environments.
* UNICEF team to lead efforts to get Elasticsearch in all HCT MIS environments.

## \*\*\*\*

## **Out of Scope**

The following items are deemed out of scope:

* Implementation of roles and permission checks and logic in various modules \(to be done in a future iteration\)
* UI for grievance tickets or management \(future iteration\)
* Deduplication algorithms using biometrics or data hashing methods \(to be handled post-MVP\)
* Support for multiple verification methods for one cash plan \(to be handled post-MVP/not clear if ever needed\).
* Support for searching duplicates in neighboring business areas \(to be handled post-MVP\).











