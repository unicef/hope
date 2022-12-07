# Aurora (aka Flex Registration)

## Objects

### Registration

It's the page when data collections happens, it requires a Flex Form (which can be used in many registrations).

### Flex Form

* Type
* Enabled
* Required
* Advanced / Extras

### Flex Field

### Formset

## Advanced Functionalities

### Validators

Javascript code used to validate form, field or formset. It can also be used as script to be run.

### Ajax Field and OptionSet

AjaxField is a special field which allow to connect to custom objects defined as OptionSet.

In the advanced option of the AjaxField we can select the following attributes:

* datasource: name of the related OptionSet
* data-parent: name of the parent OptionSet used to filter the queryset  (optional)

#### Option set configuration

The primary key (PK) is the unique identfier of the options to be displayed

The label to be displayed in multiple languages

The PK of a specific option set is used when you want to reference another option set

The Separator is the char used to split the row in columns

A field can trigger js function on changes in the Advanced Section (smart > onchange)

smart.showHideDependant(this, '\[data-flex=field\_x], \[data-flex=field\_y], \[data-flex=field\_x], 'y');

### Custom Field Type (WIP)

Equivalent of meta class for fields.

## Data

### Record

Data collected from registrations.

* json
* binary

## Process

After the registration the data is stored in Record objects as json + binary. \
Then the data is transferred to Hope through Azure Data Factory.
