# Population

## Description

The Population tab is an essential are within the HCT-MIS system, which allows users to search, filter, and view valuable information regarding Beneficiaries. Users can come to this section not only to learn more about specific household vulnerabilities information, but find out how each beneficiary is associated to Programmes, Cash Plans, and Payment Records as well. 

## Feature Specification

In this section we will review the many features of the Population Tab in detail.

### Households

\*\*\*\*[**See Glossary**](../../../introduction/glossary-terminology/)\*\*\*\*

Households are comprised of individual beneficiaries or groups of beneficiaries under a single location / address. In this section of the HCT-MIS, users can sort/filter and view detailed information regarding the households registered in the system.

#### Household Search

> **Features:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=49434](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=49434)

This interface/functionality is a way to search and view all the households and individuals in HCT MIS.

HCT user will be able to use the search field to quickly pull up households that reflect the information that is entered in their search query. Users will be able to search households on the following fields:

* Household ID
* Head of Household

Users will be able to filter their search query by using the following options:

* Programme
* Household Size
* Location
* Status

The Table List below will have the following details displayed:

* **Header** = Households \(\# of Results\)
* Table Columns:
  * **Household ID**
  * **Head of Household -** First Name + Last Name
  * **Household Size - \#**
  * **Location**
  * **Residence Status**
  * **Total Cash Received** - Amount + Currency Type _\(ie: 990.47 USD\)_
  * **Registration Date -** dd/mm/yyyy

This table will display up to 10 rows upon default.



#### Household Details

> **Features:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=49435](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=49435)

This interface / functionality is a way to view all the household details that are kept in the HCT-MIS system for a particular household.

Users on this screen will be able to navigate through lists of data, separated into the following categories:

* Individuals in Household
* Entitlement Card
* Payment Records
* Vulnerabilities
* Registration Details

#### Individuals In Household - Details

In the **Individuals In Household** card a user will be presented with a table list of the following details:

* **Individual IDs**
* **Individual** - includes first and last name of individual associated with the household.
* **Status** - Active / Inactive
* **Role -** Head of Household / Secondary / Representative
* **Sex -** Male / Female
* **Date of Birth -** dd/mm/yyyy
* **Employment/Education -** Employed / Unemployed / Education In Progress

This table will display up to 10 rows upon default.



#### Entitlement Card - **Details**

In the **Entitlement Card** card a user will be presented with the following details within a table list:

* **Card Number**
* **Status -** Active / Erroneous / Closed
* **Issue Date -** dd/mm/yyyy
* **Card Type**
* **Current Card Size - ?**
* **Card Custodian -** First Name + Last Name
* **Service Provider -** Providers name _\(ie: AIB or Afghanistan International Bank\)_

This table will display up to 10 rows upon default.



#### Payment Records - Details

In the **Payment Records** card a user will be presented with a table list of the following details:

* **Payment ID**
* **Status -** Pending / Success / Error
* **Programme -** Programme Name
* **Date of Payment -** dd/mm/yyyy
* **Cash Amount -** Amount + Currency Type _\(ie: 990.47 USD\)_
* **Distribution Modality**

This table will display up to 10 rows upon default.



#### Vulnerabilities - Details

In the **Vulnerabilities** card a user will be presented with a table list of the following details:

* **Living Situation**
* **Construction Material**
* **Shelter Quality**
* **Number of Rooms**
* **Total Dweller**
* **Dwellers in One Room**
* **Total Households**
* **Source of Water**

This table will display up to 10 rows upon default.



#### Registration Details

In the **Registration Details** card a user will be presented with a list with two sections of the following details:

* **Source**
* **Intake Group Name**
* **Registered Date -** dd/mm/yyyy
* ------------- - A separation in the card details
* Data Collection:
  * **Start Time -** dd/mm/yyyy
  * **End Time -** dd/mm/yyyy
  * **Device ID**
  * **User Name -** First Name + Last Name

This table will display up to 10 rows upon default.



### Individuals

\*\*\*\*[**See Glossary**](../../../introduction/glossary-terminology/)\*\*\*\*

Individuals are individual beneficiaries registered in the HCT-MIS Database. In this section of the HCT-MIS, users can sort/filter and view detailed information regarding individuals registered in the system.

#### Individual Search

> **Features:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=49437](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=49437)

HCT user will be able to use the search field to quickly pull up Individuals that reflect the information that is entered in their search query. Users will be able to search Individuals based on the following fields:

* Individual ID
* First Name
* Last Name
* Household ID

Users will be able to filter their search query by using the following options:

* Age \(Span\)
* Sex
* Location

The Table List below will have the following details displayed:

* **Header** = Individuals \(\# of Results\)
* Table Columns:
  * **Individual ID**
  * **Individual -** First Name + Last Name
  * **Household ID**
  * **Age**
  * **Sex -** Male / Female
  * **Location**

This table will display up to 10 rows upon default.



#### Individual Details

> **Features:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=49436](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=49436)

This interface / functionality is a way to view all the individual beneficiaries' details that are kept in the HCT-MIS system for a particular Individual.

Users on this screen will be able to navigate through lists of data, separated into the following categories:

* Bio Data
* Contact Details
* Vulnerabilities
* Cash+

#### Bio Data - Details

In the **Bio Data** card a user will be presented with a list of the following details:

* **Full Name**
* **Given Name**
* **Middle Name**
* **Family Name**
* **Sex**
* **Age**
* **Date of Birth**
* **Estimated Date of Birth**
* **ID Type**
* **ID Number**

\*\*\*\*

#### **Contact** Details

In the **Contact Details** card a user will be presented with a list of the following details:

* **Phone Number**
* **Alternate Phone Number**
* **Address**
* **Location Level**
* **Location Name**

\*\*\*\*

#### **Vulnerabilities**

In the **Vulnerabilities** card a user will be presented with a list of flex fields associated with that particular individual. See below list as an example with the following details:

* **Disability**
* **Working**
* **Serious Illness**
* **Marital Status**
* **Age First Married**
* **Enrolled In School**
* **School Attendance**
* **School Type**
* **Years In School**
* **Minutes to School**

\*\*\*\*

#### **Cash+**

{% hint style="warning" %}
NOTE: This section is still to be defined and scoped out.
{% endhint %}

In the **Cash+** card a user will be presented with a list Cash+ specific details tbd.

* **Enrolled in Nutrition Programme**
* **Administration of RUTF**

## Acceptance Criteria

The navigation should include the following:

The global navigation for this product must include the following:

* [ ] Number of Individuals Filter for Household Search feature should set a limit between 1 and 20.
* [ ] 
## User Permissions

\*\*\*\*[**Roles & Permissions**](../user-management/user-roles-and-permissions.md)\*\*\*\*

The following users should be able to interact with the following Populations features and functionalities.

* &lt;User type 1&gt;
* &lt;User type 2&gt;

#### &lt;User Type 1&gt;

This user has the ability to view only Household / Individual Information

#### &lt;User Type 2&gt;

This user has the ability to address Grievances & Feedback specific to a particular Beneficiary.

## Technical Notes

* ~~Searches handled by searching throughout the JSON fields so that Elastic search is not necessary to build for this feature.~~ 

## Future Features to Consider

* TBD





