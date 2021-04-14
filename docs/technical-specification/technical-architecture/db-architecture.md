# DB Architecture

### Separate or unified schema?

Given that HCT MIS will be centrally hosted in the cloud there are 2 big ways in which the DB can be architected. Postgres has good support for [schemas](https://www.postgresql.org/docs/9.1/ddl-schemas.html) which enables us to consider these alternatives.

* Assume one DB schema per business area, with a shared schema \(if useful per requirements\).
  * Pros:
    * Data isolation, ensuring no data from business areas gets mixed even if there is a code level vulnerability.
    * Can still have a shared schema if needed for things that cut across business areas
    * The [HQ dashboard](../../product-specification/hq/dashboard.md) would just be a different schema \(literally with a different set of tables\)
  * Cons:
    * More moving parts to manage.
    * Running data migrations would require running it on many schemas
    * Makes HQ dashboard potentially a bit more involved since data has to be ETL'd from all the other schemas into it on a regular cadence. 
* One shared schema for all business areas.
  * Pros:
    * Easier from an implementation perspective. All the data points to a "business area" model that then tells the application code how to enforce permissions.
    * Less moving parts and migrations run faster/consistently \(easier to test in staging\)
    * Could get away with implementing queries on the raw data itself for HQ Dashboard purposes.
  * Cons:
    * Could lead to security issues since the data for each business area resides with mixed id's in the same schema/db tables.
    * Not easy to export all business area data if required.

### Implementation Choices

This [link](https://github.com/tomturner/django-tenants#why-schemas) \(from **django-tenants**\) gives a nice overview of choices as well. This library enables us to leverage Postgres Schemas efficiently without having to write a lot of custom code ourselves.



