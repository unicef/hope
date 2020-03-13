---
description: These mutations and queries support the core functionality within HCT MIS.
---

# GraphQL mutations and queries

## Mutations

### Registration Data Import

* Validate and Create only with XLSX file attached
* Create import \(via XLSX or Kobo project\)
  * Will have to trigger, probably via REST an async job.
* Approve Registration Import \(pending -&gt; approved\)
  * importing -&gt; pending and merging -&gt; merged are async backend import state transitions. approved -&gt; merging is done in a separate mutation \(below\)?
* Import to population \(async\)
  * approved -&gt; merging state transition

### Population

* none!

### Target Population

* Create
  * Requires a name and a valid set of filters payload to be sent
  * Will then freeze results and the households associated \(after calculating/filtering them\) with this newly created target population.
* Change Target population state \(in progress -&gt; finalized\)
* Edit
  * Very similar to create, all the same validations, save actions etc.
* Duplicate
* Delete

### Programme Management

* Create Programme
* Edit Programme
* Remove Programme
* Change Programme State \(activate finish etc.\)

## Queries

### Registration Data Import

* List of Imports \(paginated, filtered, sortable\)
* Import details \(nested households, individuals\)

### Population

* List of Households
* Household details
* List of Individuals
* Individual details \(by id\)

### Target Population

* List of target populations \(paginated, filtered, sortable\)
* [Targeting filters supported](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Stories/?workitem=52076)
  * This will return a list of possible filters that can be applied while creating a new targeting population. This will basically be a **combination of some of the core fields and all the flex fields** in the db that are active.
  * Each should have a key, readable name, type \(int, string etc.\), choices, operations supported \(between, equals etc.\)
  * This will enable the frontend to build the ui with appropriate functionality and also appropriately build a filter payload to send in below queries but also in the save/edit mutations.
* Target population details \(by ID\)
  * send back any metadata like name, who created, when it was created, its current state
  * needs to send back the filters
* Target population results and households - by target population ID \(for saved ones\) 
  * Simple db lookup of the data
* Target population results and households - by filter payload \(for new/editing purposes\)\)
  * Calculation / filtering of data on the golden record households/individuals at the time of query.

{% hint style="info" %}
Proposing to do filters, results+households \(split into two, response for which for frontend is identical from a format perspective\) as separate queries above, rather than one query called "target population details", since in edit mode the frontend will send to backend a **payload of filters** and expect **fresh** \(not from db or stored in db\) results / households sent back. So this would be better design.

The code for determining the households to associate with a target population and these queries ideally is **shared code** since this is how we "target the households / filter them".
{% endhint %}

### Programme Management

* List of Programme
* Programme details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
* List of households \(paginated, filtered, searchable, sortable\)
* Household details \(by id, nested individuals, payments\)
* List of individuals \(paginated, filtered, searchable, sortable\)
* Individuals details \(by id\)



