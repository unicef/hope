"""
Environment configuration for the Inform API integration.

This fragment defines a handful of configuration variables that control how
HOPE interacts with the UNICEF Inform service.  Values are loaded from
environment variables using the project's SmartEnv wrapper.  If an
environment variable is missing the default value will be used instead.

Variables defined here:

* INFORM_API_BASE_URL: Base URL for the Inform API (e.g. https://data.inform.unicef.org).
* INFORM_API_TOKEN: API authentication token for requests to Inform.
* INFORM_API_AUTH_HEADER_PREFIX: Prefix for the Authorization header (defaults to "Token").
* INFORM_DATA_ENDPOINT_TEMPLATE: URL template for pulling data for a single form.
  Defaults to "/api/v1/data/{form_id}".
* INFORM_FORMS_ENDPOINT: Endpoint for listing all available forms.  Defaults to
  "/api/v1/forms".

To configure these variables set them in the environment (e.g. in your
.env file or secret manager).  For example:

    INFORM_API_BASE_URL=https://data.inform.unicef.org
    INFORM_API_TOKEN=my-super-secret-token

If any variable is unset the default will be used.
"""

from hope.config.env import env

INFORM_API_BASE_URL = env("INFORM_API_BASE_URL")
INFORM_API_TOKEN = env("INFORM_API_TOKEN")
INFORM_API_AUTH_HEADER_PREFIX = env("INFORM_API_AUTH_HEADER_PREFIX", default="Token")
INFORM_DATA_ENDPOINT_TEMPLATE = env(
    "INFORM_DATA_ENDPOINT_TEMPLATE", default="/api/v1/data/{form_id}"
)
INFORM_FORMS_ENDPOINT = env("INFORM_FORMS_ENDPOINT", default="/api/v1/forms")