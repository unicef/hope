# Uploading and Managing Flex Fields

**Feature**: [https://unicef.visualstudio.com/ICTD-HCT-MIS/\_boards/board/t/Software%20Engineering/Features/?workitem=49446](https://unicef.visualstudio.com/ICTD-HCT-MIS/_boards/board/t/Software%20Engineering/Features/?workitem=49446)

**Technical specification**: [Kobo integration](../../technical-specification/kobo-integration/)

**Glossary**: [Kobo glossary](../../introduction/glossary-terminology/kobo-glossary.md)

### Motivation

HCT would like to maintain a global set of flex fields in the system that are needed. These fields are associated with a household or individual level data. The data for these will be imported via [Kobo](../external-integrations/kobo.md) or an excel file upload \(when data has been attained via pre-existing registration methods or a partner etc.\). See  [Registration Data Import](../country-office/registration-data-import/) for more details.

The way this "catalog" of fields is maintained in the system will be centralized and apply to all business areas in the same manner. This will allow a shared set of variables across business areas and permit unification of the registration and targeting process, but also allow reporting ease at a HQ level potentially if required.

For ease of generating this excel file \(to be used for importing in flex field metadata\), it will be generated via export of a form/project from Kobo.

### User Permissions

Only a certain user group will be permitted to do this functionality. Typically this will be a special **HQ admin** user. The user will not be able to delete any data or fields or choices etc. from the database.

### User Interface

Its recommended that instead of a user interface inside the core HCT application, we build on top of a pre-existing admin interface such as Django Admin, given how infrequently this feature will be used and by a very limited set of users.

### Field Types to be supported

The following field types will be supported:

* Integer
* Decimal
* DateTime Stamp
* Geo location/Point
* Select one
* Select many
* File field \(photo\)
* Text field

Any grouping of fields and choices associated with the select one/many fields will also be stored.

### Acceptance Criteria

Following are all the edge cases / acceptance criteria, associated with the upload of the fields spreadsheet by the HQ user.

* [ ] Any deletion of fields/choices/groups etc. should be a soft delete in the system, along with timestamps for when they were created and last modified.
* [ ] The user who created and edited the fields/choices last should be there as well.
* [ ] The upload should fail or succeed as an atomic transaction, making sure no harm to the db is done.
* [ ] If a core field that is required by the db is missing, then throw an error as well \(this is simply a sanity check since really we already know the name, label, type etc. of the core field since it will be a fixed column in our db\).
* [ ] Show error to user if the file format is not compatible with the system.
* [ ] Type, name and label are required in the excel file being uploaded. Show error to users.
* [ ] Name of the field needs to be unique.
* [ ] If a new excel file is uploaded, the following list of criteria needs to be checked:
  * [ ] if new fields being introduced then import them.
  * [ ] if the **type** of an existing field \(name\) is changed, we will throw an error.
  * [ ] if a choice has been added to an existing \(single and multiple select\)
  * [ ] if a choice is removed then de-activate it.
  * [ ] if a field is removed then mark it inactive.

### Future Enhancements

Future enhancements for this feature might include:

* Keeping a copy of any excel file that is uploaded/imported successfully in the system.



