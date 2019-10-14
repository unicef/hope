# Open Issues

### UX

* How do we enable as seamless an experience with HCR.
* How to enable SSO with CA for users that have been on-boarded already?

### UNICEF HCT MIS data/flows in CashAssist

* Is HCT implementation going to be per country an app or workspace within dynamics? Is this the same way CashAssist supports its own different country offices?
* Is it the same codebase as HCR CashAssist or a fork of the codebase specific to UNICEF?
* Is each CO data be kept isolated and accessed that way by HCT MIS?

### Data Interchange

* What is the accepted/expected data format? REST / GraphQL ? JSON / XML ?
* Direct native Dynamics API access or through a CashAssist layer?
* Data lake integration: Does CashAssist have a data lake in place? What are its implementation details?
* What would be the best way to get household / beneficiary data from HCT MIS to CashAssist? Are we aiming for universal identity of households/beneficiary cross-agency as part of this effort?
* How large are typical datasets? For cash plans etc.
* Can we not push / update beneficiary / household data via Dynamics API's?

### Rule Engine

* How many users using it?
* Is it really cloud hosted [https://www.progress.com/corticon](https://www.progress.com/corticon) ?
* Where does data output get into CashAssist?
* What is the data input into Rule Engine? Does it come from CashAssist directly at all? Can it?

### User Management

* How do we propose User management / sync \(HCT MIS =&gt; CashAssist\) ?
* Mapping of user roles/permissions across systems \(at the UI level\) would be good. Can you please share all the roles in CashAssist along with the permissions/capabilities they have.
* What does CashAssist use for user management ticketing system? Does it have an API that can be exposed?
* Can one user have access to multiple Country Office cash transfer programs?
* Are CashAssist users all UNHCR users only?

#### From Sebastian

* CashAssist is Microsoft Dynamics 365 based,  which reduces the technical options to Azure AD as the IDP.
  * Yes, was confirmed by Sonam from UNHCR.
* In order to fulfill the requirement of using UNICEFs own corporate accounts to interact with CashAssist, the Azure B2B collaboration feature of the UNHCR Azure AD, by means of which users from another Azure AD tenant can be invited, and through a process of redeeming that invite access the resources on the original tenant \(UNHCR in this case\).
  * Confirmed as well.
* In order to use Dynamics 365, these UNICEF B2B collaboration users will have to be licensed on the UNHCR tenant.
  * Confirmed as well.
* The process of inviting and licensing UNICEF users into UNHCRs IDP can be:
  * Manual: Similar to the current agreement on role assignment, solved by raising a ticket through UNHCRs service management system.
  * Automated: Via the Azure AD B2B guest invite APIs \(this needs discussion with UNHCR in terms of how to layout a solution that will imply accessing these IDPs  APIs\)/UN
    * UNHCR is handling via access portal. So we may not need any API integration since a UNICEF user will be able to invite and add users on their own.
    * a UNICEF requestor and approver will be in the access portal. 

We need to validate with them all these technical assumptions and probe them on their availability to wok on the last API automation point.

### Misc.

* Is there a glossary of terms available for CashAssist with their definitions?
* A high level-data model would be good if easy to share.
* What is the product roadmap for CashAssist that might impact this integration in any of the above impact areas?
* Where are the SSIS packages executed?



