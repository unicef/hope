# Iteration 8

## Iteration 8 Deliverables

The goal of Iteration 8 is to implement the remaining critical features for the MVP of the HOPE product as well as ensure areas that are developed are functioning securely through system hardening.

**Expected start/end date: December 7, 2020 - March 5, 2021 \(13 weeks\)**

##  Architecture / Project Management Deliverables

* Pilot Plan / Rollout Strategy
* \(i.9\) Planning.
* Maintenance & Support Planning \(i.10\)
* Maintain Project Roadmap / Timeline.
* Participate in briefing and workshop remotely or in-person as required by UNICEF

##  Technical Deliverables

### MVP:

* **Account for scaling with additional Clusters or new Node pool w/ Domain spaces, etc.**
  * Test and Document the full investigation of:
    * Upgrade docker - what prevents existing docker to be switched off when ready to switch to new request.
    * Investigate and Prepare for Downgrade of docker.
    * Scale on consumed resources \(ie: CPU, etc\) \(serial mode vs parallel\)...

      * Ex: Deduplication scaling.
* **Complete development of the Grievance & Feedback module according to the signed-off requirements from Iteration 7:**
  * Create Grievance Tickets:
    * Automated  
* **System hardening for integration testing & critical bug fixes and testing of all previously developed Modules \(no new work\):**
  * Integration w/ external applications:

    * KoBo 
    * CashAssist
    * RapidPro
    * Vision

  * **Bug fixes:**

    * Registration Data Import
    * Population
    * Targeting
    * Payment Verification
    * Programs
    * Grievances & Feedback
    * User Management
* **Implementation of Roles & Permissions**
  * 60+ Permission for following roles:

    * Basic User
    * Reader
    * Advanced Registration Reader
    * Planner
    * Approver
    * Authorizer
    * Releaser
    * Grievance Collector
    * Ticket Creator
    * Ticket Owner
    * Grievance Approver
    * Senior Manager
    * Adjudicator
    * Country Admin
    * HQ / System Admin
* **Development of Light Version of Audit Log**

  * Table List
  * ~~Filter List \(TBD?\)~~

* **Anonymization of Data on Lists**

  * Obscure PII Data on the Front End for most lists in the system.
  * Automatic Logout - Inactive User Session Timeout
  * Make anonymization as permission for all users \(Part of R&P\)

* **System Refactoring and General DevOps changes.**
  * _**Nice to have depending on time and budget remaining in iteration:**_
    * _Concurrency \(Backend Only for MVP\)_
    * _Python Package Path_
  * **Required changes:**
    * Sentry for Front End
    * Implement Code Versioning
    * "Automatic Docker activities" 
    * Move from .PIP to Poetry

### Change Requests:

* Registration Data Import \(MVP\)
  * Implementation of new KoBo Registration Workflow
* Targeting Changes \(Lower priority\)
  * Make changes to Targeting properties for Cloning Target Populations with Steficon.

### **Lower priority, but required items:**

* **System Reporting**
  * UI for displaying Report Templates
  * 8 Unique Report Templates
  * Account for missing report parameters.
* **Dashboard**
  * Add "Global" Country \(BA\).
  * Country Filter for Global Dashboard
  * Ability to export each chart.
  * 10+ Unique Dashboard Charts w/ Hover State details.

## UX / UI Design Deliverables

* Design final clickable prototype of Audit Logs
* Design final clickable prototype of Reports Tab
* Design Final clickable prototype for Targeting Change Requests.
* Design final clickable prototype of Dashboard Tab
* Design Review of Developed Screens in Staging Environment vs Mockups.
* Demo for peer review with country offices \(as/if required\).

