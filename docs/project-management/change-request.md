---
description: Change request for Iteration 4 Deliverables
---

# Change Requests

## Iteration 7



### **Targeting - Details View - Columns**

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75647" %}

**------------------------------------------------**

### Change of copy in the Targeting

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75651" %}

**------------------------------------------------**

### Activity log - change copy

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75639" %}

**------------------------------------------------**

### **Chages to PV list view**

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/73205" %}

**------------------------------------------------**

### Add fields to household details

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/73178" %}

**------------------------------------------------**

### Ability to archive/remove a Target Population

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/60538" %}

**------------------------------------------------**

### Move “Programme\(s\) Enrolled” and “Total Cash Received”

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/73176" %}

**------------------------------------------------**

### Data related to Location should be grouped together

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/73177" %}

**------------------------------------------------**

### **Household composition**

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/73180" %}

**------------------------------------------------**

### **Copy change**

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75461" %}

**------------------------------------------------**

### **Change location to Administrative level 2**

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75460" %}

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75305" %}

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75303" %}

**------------------------------------------------**

### Allow local users to login

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75616" %}

**------------------------------------------------**

### ERP schema updates

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75526" %}

{% embed url="https://unicef.visualstudio.com/ICTD-HCT-MIS/\_workitems/edit/75653/" %}

**------------------------------------------------**

### ERP schema - **DP** table changes **-** [link](https://unicef.visualstudio.com/ICTD-HCT-MIS/_workitems/edit/74080)

#### October 13th 2020

1. remove: 
   * session\_id
   * exchange\_rate
2. change: 
   * document\_type to only **char\(2\)**
   * total\_down\_payment\_amount\_local to **decimal\(15.2\)**
   * total\_down\_payment\_amount\_usd to **decimal\(15.2\)** 
3. add:

   | id | integer\(\) autoinc |
   | :--- | :--- |
   | rec\_serial\_number | char\(10\) |
   | doc\_year | integer |
   | doc\_number | char\(10\) |
   | doc\_item\_number | char\(03\) |
   | doc\_reversed | CHAR\(01\) |
   | create\_date | datetime |
   | created\_by | char\(12\) |
   | update\_date | datetime |
   | updated\_by | char\(12\) |
   | mis\_sync\_flag | bool |
   | mis\_sync\_date | datetime |
   | ca\_sync\_flag | bool |
   | ca\_sync\_date | datetime |

See full details: [Integration data sets - July 26 updated.xlsx](https://unicef.sharepoint.com/:x:/r/teams/EMOPS-HCT-MIS/DocumentLibrary2/Modules%20-%20Components/CashAssist/Integration%20data%20sets%20-%20July%2026%20updated.xlsx?d=w8f70a71e4b074025b585d3a6190f7b8e&csf=1&web=1&e=gfhRuW)

**------------------------------------------------**

### ERP schema - FC table changes **-** [link](https://unicef.visualstudio.com/ICTD-HCT-MIS/_workitems/edit/74079)

#### October 13th 2020

1. remove:
   * session\_id
   * exchange\_rate
2. change: 
   * g\_l\_account to **gl\_account**  and to **char\(10\)**
   * document\_type to only **char\(2\)**
   * currency\_code to **char\(5\)**
   * commitment\_amount\_local to **decimal\(15.2\)**
   * **commitment\_amount\_usd to decimal\(15.2\)**
   * total\_open\_amount\_local to **decimal\(15.2\)**
   * total\_open\_amount\_usd to **decimal\(15.2\)**
3. add:

   > | id | integer\(\) autoinc |
   > | :--- | :--- |
   > | rec\_serial\_number | varchar\(10\) |
   > | document\_reference | char\(16\) |
   > | fc\_status | char\(01\) |
   > | create\_date | datetime |
   > | created \_by | char\(12\) |
   > | update\_date | datetime |
   > | updated\_by | char\(12\) |
   > | mis\_sync\_flag | bool |
   > | mis\_sync\_date | datetime |
   > | ca\_sync\_flag | bool |
   > | ca\_sync\_date | datetime |

See full details: [Integration data sets - July 26 updated.xlsx](https://unicef.sharepoint.com/:x:/r/teams/EMOPS-HCT-MIS/DocumentLibrary2/Modules%20-%20Components/CashAssist/Integration%20data%20sets%20-%20July%2026%20updated.xlsx?d=w8f70a71e4b074025b585d3a6190f7b8e&csf=1&web=1&e=gfhRuW)

**------------------------------------------------**

### **RDI Changes in Kobo form**

**September 30th 2020**

* Grouping of questions have been modified and new groups are created, please reflect on the catalog on Targeting. \(as part of previous change requests we had asked to show core fields too, it can be part of that work\)  
* `consent_h_c`  is now a **boolean** field 
* `child_marital_status_i_f` is **removed** 
* `free_union` from `marital_status_i_c` is **removed**
* Column name modifications highlighted in **yellow** in the XLSForm:
  * `sex_i_c` is changed to `gender_i_c`
  * `fchild_hoh_i_c`  changed to `child_hoh_h_c`  \(Female child headed household\)
  * `child_hoh_i_c`  changed to `child_hoh_h_c`   \(Child headed household\) 
  * Disability field changes: `observed_disability_i_fis` changed to `observed_disability_i_c` , `seeing_disability_i_f` is changed to `seeing_disability_i_c` and others 
  * `latrine_h_f` changed to `shared_latrine_h_f` 
  * `water_source_h_f` changed to `drinking_water_source_h_f` 
* New fields have been added highlighted in **orange** 
* There are some changes in choices, highlighted in **orange**

{% file src="../.gitbook/assets/detailed-registration-9.29.xlsx" caption="\(Change Request\) Detailed Registration 9.29.xlsx" %}



## Iteration 6

**------------------------------------------------**

### BusinessArea info

**August 17th 2020**

\*\*\*\*[**link to ticket**](https://unicef.visualstudio.com/ICTD-HCT-MIS/_workitems/edit/68702)\*\*\*\*

Add BusinessArea info to the ****Session model**.**

We need to add a `mis_datahub.business_area` field to the Session model equal to the `mis_datahub.Program..business_area` field.

**------------------------------------------------**

### **Target Population Updates**

\*\*\*\*[**See Related Document**](https://docs.google.com/document/d/1WBLRN_DPK29KqWDrZ0eHuJUpiby3VW4EE6uipENlFmQ/edit?usp=sharing)\*\*\*\*

#### **Overview / Motivation**

* Many times there is no reliable individual level data available for households in certain programs.
* Hence UNICEF needs the ability to restrict visibility in data where it is not necessary in Cash Assist and communicate what level of data is available for a program so entitlements etc. can be best calculated in CA.

#### **Solution**

1. **Add a flag to the staging \(High Priority\)**
   * Add field \(Boolean, send\_individual\) for Household / Individual flag when creating a Programme.
   * Send flag from HOPE Programme / TP to Cash Assist.
2. **UI changes \(Low Priority\)**
   * When closing a Target Population, and a user selects a Programme with an individual flag, warn the user when send\_individual == False and they are targeting based on individual params anywhere in the TP 
   * send collectors plus targeted individual details to Cash Assist

#### **Expected Delivery Date**

Staging Model + light UI changes \(50%\) to be done within 4 weeks.

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

