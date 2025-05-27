from hct_mis_api.api.caches import (BusinessAreaAndProgramKeyBitMixin,
                                    KeyConstructorMixin)


class RDIListVersionsKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "registration_data_import_list"


class RDIKeyConstructor(KeyConstructorMixin):
    registration_data_import_list_version = RDIListVersionsKeyBit()
