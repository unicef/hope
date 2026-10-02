from storages.backends.azure_storage import AzureStorage


# Looks unused, but deploys select it via FILE_STORAGE_MEDIA; removing it broke prod once (#6062, #6120).
class AzureMediaStorage(AzureStorage):
    expiration_secs = 30


# Looks unused, but deploys select it via FILE_STORAGE_STATIC; removing it broke prod once (#6062, #6120).
class AzureStaticStorage(AzureStorage):
    expiration_secs = None
