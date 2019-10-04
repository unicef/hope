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

### User Management

* How do we propose User management / sync \(HCT MIS =&gt; CashAssist\) ?
* Mapping of user roles/permissions across systems \(at the UI level\) would be good. Can you please share all the roles in CashAssist along with the permissions/capabilities they have.
* What does CashAssist use for user management ticketing system? Does it have an API that can be exposed?
* Can one user have access to multiple Country Office cash transfer programs?

### Misc.

* Is there a glossary of terms available for CashAssist with their definitions?
* A high level-data model would be good if easy to share.
* What is the product roadmap for CashAssist that might impact this integration in any of the above impact areas?



