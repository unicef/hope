from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    account_name = settings.MEDIA_STORAGE_AZURE_ACCOUNT_NAME
    account_key = settings.MEDIA_STORAGE_AZURE_ACCOUNT_KEY
    azure_container = settings.MEDIA_LOCATION
    expiration_secs = 30


class AzureStaticStorage(AzureStorage):
    account_name = settings.STATIC_STORAGE_AZURE_ACCOUNT_NAME
    account_key = settings.STATIC_STORAGE_AZURE_ACCOUNT_KEY
    azure_container = settings.STATIC_LOCATION
    expiration_secs = None
