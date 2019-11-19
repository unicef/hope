# Kobo Integration

#### How to get the API token for a user?

/token/?format=json - for example on the cloud hosted Kobo go to: [https://kobo.humanitarianresponse.info/token/?format=json](https://kobo.humanitarianresponse.info/token/?format=json)

To test it use this command:

```text
curl -X GET https://[kpi-url]/assets/?format=json -H "Authorization: Token [your_token_goes_her
```

See [http://support.kobotoolbox.org/en/articles/592398-api-and-rest-services](http://support.kobotoolbox.org/en/articles/592398-api-and-rest-services) for more information.



#### How to get data out of Kobo installation?

URL [https://kobo.humanitarianresponse.info/api/v2/assets/\[asset\_hash\]/data/](https://kobo.humanitarianresponse.info/api/v2/assets/[asset_hash]/data/) with the API token \(in the head:  will give you the data back.





