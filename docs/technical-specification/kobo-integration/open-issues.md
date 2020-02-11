# Open issues

### Setting/Accessing Kobo API token for business area

There are 2 options for making sure HCT can make API calls to Kobo successfully.

Having an API token manually set at the business area level.

The other option is to set only the username of the Kobo user \(the "main" account in Kobo\) for the country.  Based on that, on\_save we would read from the Kobo db directly what the API token is and save it in the HCT database.

### Helm Chart for Kobo

It would ease deployment of Kobo if it were available as a Helm chart.



