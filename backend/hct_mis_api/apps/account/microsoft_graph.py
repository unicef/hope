import logging

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

AZURE_GRAPH_API_TOKEN_CACHE_KEY = "azure_graph_api_token_cache_key"
AZURE_GRAPH_DELTA_LINK_KEY = "azure_graph_delta_link_key"

logger = logging.getLogger(__name__)

DJANGO_USER_MAP = {
    "_pk": ["username"],
    "username": "userPrincipalName",
    "email": "mail",
    "azure_id": "id",
    "job_title": "jobTitle",
    "display_name": "displayName",
    "first_name": "givenName",
    "last_name": "surname",
}

ADMIN_EMAILS = [i[1] for i in settings.ADMINS]

NotSet = object()


class MicrosoftGraphAPI:
    def __init__(self):
        self.azure_client_id = settings.AZURE_CLIENT_ID
        self.secret = settings.AZURE_CLIENT_SECRET
        self.user_model = get_user_model()
        self.field_map = DJANGO_USER_MAP
        self.user_pk_fields = self.field_map.pop("_pk")
        self._baseurl = "{}/{}/users".format(settings.AZURE_GRAPH_API_BASE_URL, settings.AZURE_GRAPH_API_VERSION)
        self.startUrl = "%s/delta" % self._baseurl
        self.access_token = self.get_token()
        self.next_link = None
        self.delta_link = ""

    def get_token(self):
        if not self.azure_client_id or self.secret:
            raise ValueError("Configure AZURE_CLIENT_ID and/or AZURE_CLIENT_SECRET")

        post_dict = {
            "grant_type": "client_credentials",
            "client_id": self.azure_client_id,
            "client_secret": self.secret,
            "resource": settings.AZURE_GRAPH_API_BASE_URL,
        }
        response = requests.post(settings.AZURE_TOKEN_URL, post_dict)

        if response.status_code != 200:
            logger.error(f"Unable to fetch token from Azure. {response.status_code} {response.content}")
            raise Exception(f"Error during token retrieval: {response.status_code} {response.content}")

        json_response = response.json()
        token = json_response["access_token"]
        return token

    def get_results(self, url):
        headers = {"Authorization": "Bearer {}".format(self.get_token())}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        self.next_link = json_response.get("@odata.nextLink")
        self.delta_link = json_response.get("@odata.deltaLink")

        return json_response

    def get_page_values(self, url):
        return self.get_results(url).get("value", [])

    def __iter__(self):
        values = self.get_page_values(self.startUrl)
        while len(values) > 0:
            yield values.pop()
            if len(values) == 0 and self.next_link:
                values = self.get_page_values(self.startUrl)

    def get_record(self, user_info):
        data = {field_name: user_info.get(mapped_name, "") for field_name, mapped_name in self.field_map.items()}
        pk = {field_name: data.pop(field_name) for field_name in self.user_pk_fields}
        return pk, data

    def fetch_users(self, user_filter, callback=None):
        self.startUrl = "%s?$filter=%s" % (self._baseurl, user_filter)
        return self.synchronize(callback=callback)

    def search_users(self, record):
        url = "%s?$filter=" % self._baseurl
        filters = []
        if record.email:
            filters.append("mail eq '%s'" % record.email)
        if record.last_name:
            filters.append("surname eq '%s'" % record.last_name)
        if record.first_name:
            filters.append("givenName eq '%s'" % record.first_name)

        page = self.get_results(url + " or ".join(filters))
        return page["value"]

    def filter_users_by_email(self, email):
        """https://graph.microsoft.com/v1.0/users?$filter=mail eq 'sapostolico@unicef.org'"""
        url = "%s?$filter=mail eq '%s'" % (self._baseurl, email)
        page = self.get_results(url)
        return page["value"]

    def get_user(self, username):
        url = "%s/%s" % (self._baseurl, username)
        user_info = self.get_results(url)
        return user_info

    def sync_user(self, user, azure_id=None):
        if not (azure_id or user.azure_id):
            raise ValueError("Cannot sync user without azure_id")
        url = "%s/%s" % (self._baseurl, azure_id or user.azure_id)
        user_info = self.get_results(url)
        pk, values = self.get_record(user_info)
        user, __ = self.user_model.objects.update_or_create(**pk, defaults=values)
        return user

    def resume(self, *, delta_link=None, max_records=None):
        if delta_link:
            self.startUrl = delta_link
        return self.synchronize(max_records)

    def synchronize(self, max_records=None, callback=None):
        for i, user_info in enumerate(iter(self)):
            pk, values = self.get_record(user_info)
            if user_info.get(values):
                user, created = self.user_model.objects.update_or_create(**pk, defaults=values)
                if callback:
                    callback(user=user, is_new=created)
            if max_records and i > max_records:
                break
