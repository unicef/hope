# Kobo

[Kobo](https://www.kobotoolbox.org/) is a powerful form builder and data collection platform. It will be used for data collection in the field via its mobile application \([KoBoCollect](https://play.google.com/store/apps/details?id=org.koboc.collect.android&hl=en_US)\) and PWA \([Enketo](https://enketo.org/) forms\) which is integrated into the Kobo platform, to support non-Android users or web users in general.

### Field naming

Fields in the kobo forms will be named henceforth so that HCT can understand it fully.

* field\_name\_h\_c - household core field
* field\_name\_h\_f - household flex field
* field\_name\_i\_c - individual core field
* field\_name\_i\_f - individual flex field

See [Uploading and Managing Flex Fields](../hq/uploading-and-managing-flex-fields.md) to see how this would be managed in HCT.

### Accounts per business area

Since Kobo has a user-centric model of permissions, we propose having a "main" user account per business area. This main account will be the one from which data will be extracted once data collection has been done.

The main account will give permissions to collect data or at whatever level they deem appropriate, to enumerators on the ground.

### Standardizing forms across country offices

A standard form will be shared as a collection with country offices, so that they can use a standard form and potentially capture additional data if they would like. This will ensure lower mistakes, not having countries having to worry about exact field naming etc. as well.

This same standard form \(template, not data\) is exported into Excel and [imported as "flex fields"](../hq/uploading-and-managing-flex-fields.md) into HCT. 



