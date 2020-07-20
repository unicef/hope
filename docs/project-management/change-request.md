---
description: Change request for Iteration 4 Deliverables
---

# Change Requests

## Iteration 6

### **Target Population Updates**

**July 8th, 2020**

Stefano said that this is their decision from today**'**s night. So here some bullets:

* TP have to have a type field \(individual/household\)
* TP type has to be sent to DataHub
* If TP type is individual, we remove households without individuals from results
* TP type is not editable, after the initial set
* When TP type is set to individual all individual are send to Datahub
* We show individual based filters \(Age, Sex\) only when TP type is set to individual

**Expected Delivery Date:**

TBD

**Notes:**

**------------------------------------------------**

### **UNHCR Data Sharing Agreement**

**July 8th 2020**

\*\*\*\*[**link to ticket**](https://unicef.visualstudio.com/ICTD-HCT-MIS/_sprints/backlog/Software%20Engineering/ICTD-HCT-MIS/Iteration%206/Sprint%201%20%28i.6%29?workitem=64344)\*\*\*\*

> In order to push the necessary data to appropriate fields into the datahub depends on if the business area has data sharing agreement with UNHCR or not. Some rules below have been set, the logic is described in length below.

**------------------------------------------------**

### Primary Collector \(Many2Many\) 

**July 2nd 2020**

**Data Model Change**

* Change Data model to allow for Many to Many Individuals to Households
* If we find a duplicate that belongs to two households - because we have the many 2 many - but based on their ROLE - we can allow for the duplicate.
* Three factors:
  * Membership
  * Role
  * Collector Type

  
representatives = m2m\(through=individuals\)

Make household nullable to allow for Collector object.

## Iteration 5

### Sanctions List

* Upload Sanctions List Document check screen w/ authentication and validation.

**------------------------------------------------**

### Cypress / UAT / QA

* 200+ hours of development/engineering/training/spec of Cypress User Testing that were decided in final \(2\) weeks of Iteration. 

**------------------------------------------------**

### Cash Assist Changes to DataHub

* Continued throughout Iteration 5 and into Iteration 6



## Iteration 4

### 

### Target Population Updates

**Date: ....**

### Overview:

#### Change Details:

Unicef has made the request to include in the development of the Target Population for Iteration 4; the ability to have HCT system interact with the Corticon RuleEngine in order to produce a Vulnerability Score, along with a few other scores \(_amount not yet determined_\).

#### Change Reason

Upon recent discussion and thought, it was decided to include additional criteria that can only be established by the Corticon RuleEngine, at this time. These additional criteria, including Vulnerability Score is considered to be a fundamental business requirement . It's previous consideration was overlooked until now. 

#### Impact of Change

Overall the Impact this change brings is relatively small. See below for the list of impacts this change brings:

* Slight Adjustments to the backend that have already been created since the start of Iteration 4 \(roughly 4.5 weeks\).
* Significant Design Adjustments to the affected flow of the Target Population process from which it was originally prepared for.
* Slight refactoring of the Front End, including updated styles, components, new components and more.
* General Impact for overall timeline project or iteration timeline is **small**.
* Some deliverables identified for Iteration 4 will need to be placed on hold or moved to be developed at a later time.

#### Proposed Action

The agreed action is to move forward with placing the following two features from the Iteration 4 SOW on hold:

1. CO users to be able to view flex fields somewhere in the interface.
2. POC of Kobo DevOps and documentation refinements, API usage needed etc. Technical support from Kobo on DevOps, database structure, API related help may be required.

