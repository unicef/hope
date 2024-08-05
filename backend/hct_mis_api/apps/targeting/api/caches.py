from hct_mis_api.api.caches import BusinessAreaAndProgramKeyBit, KeyConstructorMixin


class TPListVersionsKeyBit(BusinessAreaAndProgramKeyBit):
    specific_view_cache_key = "target_population_list"


class TPKeyConstructor(KeyConstructorMixin):
    target_population_list_versions = TPListVersionsKeyBit()
