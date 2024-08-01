from typing import Any

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hct_mis_api.api.caches import KeyConstructorMixin, get_or_create_cache_key, \
    ProgramKeyBit
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleListVersionsKeyBit(KeyBitBase):
    def get_data(
            self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        program_id = decode_id_string(kwargs.get("program_id"))
        program_cycle_updated_at = ProgramCycle.all_objects.filter(program_id=program_id).latest("updated_at").updated_at

        version_key = f"{program_id}:{program_cycle_updated_at}"
        return str(version_key)


class ProgramCycleKeyConstructor(KeyConstructorMixin):
    program_id_version = ProgramKeyBit()
    program_cycle_list_versions = ProgramCycleListVersionsKeyBit()
