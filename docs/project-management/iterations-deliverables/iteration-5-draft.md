# Iteration 5 \(DRAFT\)

**Iteration 5: KoBo Helm Chart / Kubernetes Deliverables**

The goal of Iteration Five is to integrate KoBo Form / Projects and project data into HCT-MIS Registration Datahub along with push/pull of data from the CashAssist Datahub.

**Expected start/end date:** May 11th - July 3rd, 2020 \(8 weeks\)

## **Architectural design / Project Management Deliverables**

* Sign-off the functional specifications and flows for Registration Data Import deduplication process to be implemented in later Iterations.
* _Sign-off the functional specifications & designs for Payment Verification Section to be implemented in later Iterations._
* _Sign-off the functional specifications & designs for Grievances & Feedback Section to be implemented in later Iterations._
* Interface with core Kobo team on technical / testing details.
* Maintain Project Roadmap / Timeline.
* Participate in briefing and workshop remotely or in-person as required by UNICEF

## **Technical Deliverables**

* Complete development of any further Core Fields changes from Iteration 4 that were not fully finalized.
* CO users to be able to **view flex fields** somewhere in the interface.
* Kobo setup within Azure:
  * Deliver a **helm chart** for Kobo that can be deployed on Azure environments of HCT \(dev/staging/uat/prod\).
  * Work to make the helm chart be potentially public available / maintained then by the open-source community or the Kobo team.
  * Leverage the Kobo service setup via this helm package then, to interface with the HCT MIS system.
  * _Nice to have_ \(out of scope if no time remaining\): helm chart tested and working in AWS environment as well. AWS is something that the Kobo team leverages and might find useful long-term.
* Frontend and backend HCT MIS **integration with Kobo** to import data \(extension of XLS based registration data import\).
* Airflow based integration to **pull and push data from CashAssist Datahub**. This includes things like: programs, target population \(and included households/individuals as necessary\), cash plans, payment records etc. 
  * Out of scope: Integrating CashAssist with the Datahub is not Tivix responsibility and will be done by CashAssist team with help from UNICEF ICTD team.
* E2E testing / QA support to UNICEF QA team

## **UX / UI Design Deliverables**

* Design final clickable prototype of Registration Data Import Enhancements \(Deduplication\)
* Design final clickable prototype of Payment Verification Tab
* _Design final prototype of Grievances & Feedback Tab_
* Continued refinement of mockups.
* Demo / webinar for peer review with country offices \(if feasible\).

