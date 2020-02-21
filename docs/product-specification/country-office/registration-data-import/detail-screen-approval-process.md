# Import Management

**Feature:** [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=50069](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=50069)

## Motivation

HCT must be able to view on the system interface the information that is being ingested into the system in order to validate whether or not it is acceptable to be merged into the golden database. This is done by displaying the imported data on screen via the Details screen. Details on this screen will look similar in format and style to what is seen in the Populations Household/Individual details screen, however it will not be connected to the same database whatsoever. Lastly, once the information is reviewed on the interface, HCT users will have the option to [**approve**](approval-process.md) the data file being examined before allowing it to merge with the golden records.

## Functional Specification

### Import Management

Upon clicking the Registration Data Import navigation tab from the right drawer menu, the user will be taken to this default screen which will display a table list of previous imports, which a user can search and filter to narrow down their results.

\*\*\*\*

#### **Search & Filters**

HCT user will be able to use the **search field** to quickly pull up previously imported batches of beneficiaries that reflect the information that is entered in their search query. Users will be able to search batches on the following fields:

* **Title**

Users will also be able to filter their search query by using the following options:

* **Import Date**
* **Imported By**
* **Status**

The Table List below will have the following details displayed:

* **Header** = List of Imports \(\# of Results\)
* Table Columns:
  * **Title**
  * **Status** - In Review // Approved
  * **Import Date -** dd/mm/yyyy
  * **Number of Households -**  \#
  * **Imported By**
  * **Source of Data**

This table will display up to 10 rows upon default.



#### **Blank State**

When there is no data to be displayed, there will be a message on the card where the Table Data would typically be displayed, notifying the user with the following message:

{% hint style="info" %}
"No Results Found"
{% endhint %}



#### **Starting an Import**

On the top right hand side of this screen there is a button labeled `Import` 

When clicked, a modal will pop up, instructing the user to select a file to import.

The user will have the following choices to choose from to import data from:

* \*\*\*\*[**Excel**](via-excel-import.md)\*\*\*\*
* \*\*\*\*[**KoBo**](via-kobo-api.md)\*\*\*\*

## Acceptance Criteria

* [ ] Filtering
* [ ] Modal

## _Data Source_

_All the data shown will be from the Registration DataHub \(except maybe when de-duplication is involved?\)._





