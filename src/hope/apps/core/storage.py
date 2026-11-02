from storages.backends.azure_storage import AzureStorage


# Looks unused, but deploys select it via FILE_STORAGE_MEDIA; #6062 removed it and #6120 had to restore it.
class AzureMediaStorage(AzureStorage):
    expiration_secs = 30


# Looks unused, but deploys select it via FILE_STORAGE_STATIC; #6062 removed it and #6120 had to restore it.
class AzureStaticStorage(AzureStorage):
    expiration_secs = None
