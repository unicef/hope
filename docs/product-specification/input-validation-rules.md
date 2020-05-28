# Input Validation Rules

## **E-mail**

The **local-part** of the email address may use any of these ASCII characters:

* uppercase and lowercase Latin letters A to Z and a to z;
* digits 0 to 9;
* printable characters !\#$%&'\*+-/=?^\_\`{\|}~
* dot ., provided that it is not the first or last character unless quoted, and provided also that it does not appear consecutively unless quoted
* the maximum total length of the local-part of an email address is 64 octets

The **domain name** part of an email address has to conform to strict guidelines: it must match the requirements for a hostname, a list of dot-separated DNS labels, each label being limited to a length of 63 characters and consisting of:

* uppercase and lowercase Latin letters A to Z and a to z;
* digits 0 to 9, provided that top-level domain names are not all-numeric;
* hyphen -, provided that it is not the first or last character;
* the domain may have a maximum of 255 octets.

## **Password**

* ASCII printable characters only
* Between 8 and 128 characters long 
* Has to include:
  * Uppercase letter
  * Lowercase letter
  * Digit
  * Special character

## Currency

* \[symbol\] \#\#.\#\# \[Currency Type\]
  * **example:** $100.00 USD
* A currency amount should not exceed two decimal place.

## Dates

* DD/MM/YYYY format
* Dates must be real
* A year value cannot be greater than 2099
* A year value cannot be less than 2019
* Digits only

## Program Management

### Text Fields:

* Name
* Description
* Administrative Areas of Implementation
* Population goal

#### Validation Rules:

* Unicode characters
* A minimum length of 3 
* A maximum length of 30

### Amount Fields:

* Budget

#### Validation Rules:

* Positive numbers only
* A dot or comma as a decimal point
* A maximum of 2 numbers after decimal point
* A maximum length of 11 digits before decimal point



