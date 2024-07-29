from hct_mis_api.api.caches import BusinessAreaAndProgramKeyBit, KeyConstructorMixin


class ProgramCycleListVersionsKeyBit(BusinessAreaAndProgramKeyBit):
    specific_view_cache_key = "program_cycle_list"


class ProgramCycleKeyConstructor(KeyConstructorMixin):
    program_cycle_list_versions = ProgramCycleListVersionsKeyBit()
