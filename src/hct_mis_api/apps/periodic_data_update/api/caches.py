from hct_mis_api.api.caches import BusinessAreaAndProgramKeyBit, KeyConstructorMixin


class PDUTemplateListVersionsKeyBit(BusinessAreaAndProgramKeyBit):
    specific_view_cache_key = "periodic_data_update_template_list"


class PDUUploadListVersionsKeyBit(BusinessAreaAndProgramKeyBit):
    specific_view_cache_key = "periodic_data_update_upload_list"


class PeriodicFieldListVersionsKeyBit(BusinessAreaAndProgramKeyBit):
    specific_view_cache_key = "periodic_field_list"


class PDUTemplateKeyConstructor(KeyConstructorMixin):
    periodic_data_update_template_list_versions = PDUTemplateListVersionsKeyBit()


class PDUUpdateKeyConstructor(KeyConstructorMixin):
    periodic_data_update_upload_list_versions = PDUUploadListVersionsKeyBit()


class PeriodicFieldKeyConstructor(KeyConstructorMixin):
    periodic_field_list_versions = PeriodicFieldListVersionsKeyBit()
