# Flexible Fields

Its required to have the capability to add fields \(attributes\) to household and beneficiary data models per country.

### JSON data type

To enable this we propose leveraging [JSON data type in PostgreSQL](https://www.postgresql.org/docs/current/datatype-json.html). This field type provides a NoSQL type capability inside a relational database. Since our needs are reasonably humble, we propose using it.

The actual field definitions at the country level, will act as the template for the field itself. These fields would then be attached to household or beneficiaries either at a global or per intervention levels.

Once set the actual data captured will be stored as JSONField's on the HouseHold and Beneficiary data models themselves, with the keys of those JSONField entries pointing to the ID's of the definitions themselves.

Django has excellent support for this as well via [JSONField](https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/#jsonfield).

