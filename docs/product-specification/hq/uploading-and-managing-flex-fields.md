# Uploading and Managing Flex Fields

**Feature**: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=49446](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=49446)

### Motivation

HCT would like to maintain a global set of flex fields in the system that are needed. These fields are associated with a household or individual level data. The data for these will be imported via [Kobo](../external-integrations/kobo.md) or an excel file upload.

### User Permissions

Only a certain user group will be permitted to do this functionality. Typically this will be a special **HQ admin** user. The user will not be able to delete any data or fields or choices etc. from the database.

### Acceptance Criteria

Following are all the edge cases / acceptance criteria, associated with the upload of the fields spreadsheet by the HQ user.

* [ ] The upload should fail or succeed as an atomic transaction, making sure no harm to the db is done.
* [ ] If a core field that is required by the db is missing, then throw an error as well \(this is simply a sanity check since really we already know the name, label, type etc. of the core field since it will be a fixed column in our db\).
* [ ] Show error to user if the file format is not compatible with the system.
* [ ] Type, name and label are required in the excel file being uploaded. Show error to users.
* [ ] Name of the field needs to be unique.
* [ ] If a new excel file is uploaded following things need to be checked:
  * [ ] if new fields being introduced then import them.
  * [ ] if the **type** of an existing field \(name\) is changed, we will throw an error.
  * [ ] if a choice has been added to an existing \(single and multiple select\)
  * [ ] if a choice is removed then de-activate it.
  * [ ] if a field is removed then de-activate it.



