# Kobo Integration

### How to get the API token for a user?

/token/?format=json - for example on the cloud hosted Kobo go to: [https://kobo.humanitarianresponse.info/token/?format=json](https://kobo.humanitarianresponse.info/token/?format=json)

To test it use this command:

```text
curl -X GET https://[kpi-url]/assets/?format=json -H "Authorization: Token [your_token_goes_her
```

See [http://support.kobotoolbox.org/en/articles/592398-api-and-rest-services](http://support.kobotoolbox.org/en/articles/592398-api-and-rest-services) for more information.

### How to get data from Kobo installation

Primarily 2 API calls will be made to Kobo to get data out. All API calls need to be made with the API token \(in the head: will give you the data back.\)

* URL **https://\[kpi-url\]/api/v2/assets/** - will return list of the projects \(forms / survey\). We will only need the entries that have **has\_deployment** and/or **deployment\_\_active** is set to **true**. 
* URL **https://\[kpi-url\]/api/v2/assets/\[asset\_hash\]/data/** - will return the data associated with this survey in JSON format. This will need to be paginated depending on the amount of data associated.  The data from these API calls will be saved in HCT database as a JSONField on individuals and household models. See the details of how these fields should be interpreted [here](../../product-specification/external-integrations/kobo.md#field-naming).



