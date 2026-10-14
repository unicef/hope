from hope.api.caches import BusinessAreaAndProgramKeyBitMixin, KeyConstructorMixin


class PDUTemplateListVersionsKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "periodic_data_update_template_list"


class PDUUploadListVersionsKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "periodic_data_update_upload_list"


class PeriodicFieldListVersionsKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "periodic_field_list"


# Looks unused, but it is the key for the parked PDU template list cache (decorators commented out in api/views.py).
class PDUTemplateKeyConstructor(KeyConstructorMixin):
    periodic_data_update_template_list_version = PDUTemplateListVersionsKeyBit()


# Looks unused, but it is the key for the parked PDU upload list cache (decorators commented out in api/views.py).
class PDUUpdateKeyConstructor(KeyConstructorMixin):
    periodic_data_update_upload_list_version = PDUUploadListVersionsKeyBit()


class PeriodicFieldKeyConstructor(KeyConstructorMixin):
    periodic_field_list_version = PeriodicFieldListVersionsKeyBit()
