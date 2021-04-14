# Iteration 5

**Iteration 5: KoBo Helm Chart / Kubernetes Deliverables**

The goal of Iteration Five is to integrate KoBo Form / Projects and project data into HCT-MIS Registration module, along with push/pull of data from the CashAssist Datahub.

**Expected start/end date:** May 11th - July 3rd, 2020 \(8 weeks\)

## **Architectural design / Project Management Deliverables**

* Sign-off the functional/technical specifications and flows for Registration Data Import deduplication process to be implemented in later Iterations.
* Sign-off the functional/technical specifications & designs for Payment Verification and Grievances & Feedback Section to be implemented in later Iterations.
* Interface with core Kobo team on technical / testing details.
* Maintain Project Roadmap / Timeline.
* Participate in briefing and workshop remotely or in-person as required by UNICEF

## **Technical Deliverables**

* Complete development of any further Core Fields changes from Iteration 4 that were not fully finalized.
* Show flex fields that are in the system to the user aka Catalogue.
* Kobo setup within Azure:
  * Deliver a **helm chart** for Kobo that can be deployed on Azure environments of HCT \(dev/staging/uat/prod\).
  * Leverage the Kobo service setup via this helm package then, to interface with the HCT MIS system.
  * Nice to have \(out of scope if no time remaining\):
    * Work to make the helm chart be publicly available / maintained then by the open-source community or the Kobo team.
    * Helm chart tested and working in an AWS environment as well.
* Frontend and backend HCT MIS **integration with Kobo** to import data \(extension of XLS based registration data import\).
* Finalize and implement the CashAssist Datahub schema.
* Airflow based integration to **pull and push data from CashAssist Datahub**. This includes things like: programs, target population \(and included households/individuals as necessary\), cash plans, payment records etc.
  * Out of scope: 
    * Integrating CashAssist with the Datahub is not Tivix responsibility and will be done by the CashAssist team with help from UNICEF ICTD team.
* E2E testing / QA support to UNICEF QA team

## **UX / UI Design Deliverables**

* Design final clickable prototype of Registration Data Import Enhancements \(Deduplication\)
* Design final clickable prototype of Payment Verification and Grievances/Feedback Tab
* Continued refinement of mockups.
* Demo / webinar for peer review with country offices \(if feasible\).





