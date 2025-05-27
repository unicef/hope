from hct_mis_api.api.caches import (BusinessAreaAndProgramKeyBitMixin,
                                    KeyConstructorMixin)


class TPListVersionsKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "target_population_list"


class TPKeyConstructor(KeyConstructorMixin):
    target_population_list_version = TPListVersionsKeyBit()
