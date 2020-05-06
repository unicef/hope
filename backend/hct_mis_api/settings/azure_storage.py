from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    location = "media"
    file_overwrite = False
