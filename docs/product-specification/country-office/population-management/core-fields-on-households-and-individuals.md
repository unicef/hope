# Core fields on households & individuals

Below are the core fields that we will save on households and individuals as "core fields". This implies that these fields are to be saved for all countries HCT is deployed in. Some are required and some are not.

Flex fields can change over time and managed [differently](../../hq/uploading-and-managing-flex-fields.md).

### Household core fields

* Consent - signature/image \(**required**\)
* Residence status - select one
* Family nationality - select one
* Household size - integer \(**required**\)

### Individual core fields

* Head of household - yes/no \(**required**\)
* Marital status - select one
  * Status as head of household - select one
  * Address - text
  * admin level 1 - select one
  * admin level 2 - select one
  * phone number - integer
  * phone number \(alternative\) - integer
* Given name - text
* Middle name - text
* Last name - text
* Full name - calculated
* sex - select one \(**required**\)
* birthdate - date \(**required**\)
* age - calculated
* estimated birth date - select one
* work status - select one
* disability - select one

### Open issues

* **Technical:** Will the core fields 'flip' in terms of required or not required in the [XLS import](../../hq/uploading-and-managing-flex-fields.md) we do? Since if we do not see core fields we do error out. Or maybe we keep them all required=False and enforce at logical layer?



