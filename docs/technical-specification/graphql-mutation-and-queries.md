---
description: These mutations and queries support the core functionality within HCT MIS.
---

# GraphQL mutations and queries

## Mutations

### Registration Data Import

* Validate import XLS file \(is this a query?!\)
* Create import \(via XLS or Kobo project\)
  * Will have to trigger, probably via REST an async job.
* Change Import State \(pending -&gt; approved\)
  * importing -&gt; pending and merging -&gt; merged are async backend import state transitions. approved -&gt; merging is done in a separate mutation \(below\)?
* Import to population \(async\)
  * approved -&gt; merging state transition

### Population

* none!

### Target Population

* Create
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
* Validate import XLS file
  * is this a mutation? Its just a validation check as part of import creation process.
* Import details \(nested households, individuals\)

### Population

* List of Households
* Household details
* List of Individuals
* Individual details \(by id\)

### Target Population

* List of target populations \(paginated, filtered, sortable\)
* Target population targeting criterias \(filters\)
* Target population results \(by target population ID \(for saved ones\) or by filter payload \(for new/editing purposes\)\)
* Target population households \(by target population ID \(for saved ones\) or by filter payload \(for new/editing purposes\)\)

{% hint style="info" %}
Proposing to do as separate queries rather than one query called "target population details" since in edit mode the frontend will send to backend a payload of filters and expect fresh \(not from db or stored in db\) results / households sent back. So this would be better design.

The code for determining the households to associate with a target population and these queries ideally is shared code since this is how we "target the households / filter them".
{% endhint %}

### Programme Management

* List of Programme
* Programme details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
* List of households \(paginated, filtered, searchable, sortable\)
* Household details \(by id, nested individuals, payments\)
* List of individuals \(paginated, filtered, searchable, sortable\)
* Individuals details \(by id\)



