from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    expiration_secs = 30


class AzureStaticStorage(AzureStorage):
    expiration_secs = None
