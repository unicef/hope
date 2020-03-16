from storages.backends.azure_storage import AzureStorage


# TODO: configure azure blob storage
class AzureMediaStorage(AzureStorage):
    location = 'media'
    file_overwrite = False
