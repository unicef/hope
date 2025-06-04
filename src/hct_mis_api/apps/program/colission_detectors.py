from typing import TYPE_CHECKING, Optional

from strategy_field.registry import Registry

from hct_mis_api.apps.household.models import Household

# only for typing purposes
if TYPE_CHECKING:
    from hct_mis_api.apps.program.models import Program


class AbstractCollisionDetector:
    def __init__(self, context: "Program"):
        self.program = context
        if not self.program.collision_detection_enabled:
            raise ValueError("Collision detection is not enabled for this program")

    def detect_collision(self, household: Household) -> Optional[str]:
        raise NotImplementedError("Subclasses should implement this method")


class IdentificationKeyCollisionDetector(AbstractCollisionDetector):
    def __init__(self, context: "Program"):
        super().__init__(context)
        self.unique_identification_keys_dict: Optional[dict[str, str]] = None

    def initialize(self) -> None:
        if self.unique_identification_keys_dict is not None:
            return
        self.unique_identification_keys_dict = dict()
        ids_with_uniquekey_list = list(
            Household.all_objects.filter(program=self.program, identification_key__isnull=False)
            .values_list("id", "identification_key")
            .distinct("id")
        )
        for hh_id, key in ids_with_uniquekey_list:
            self.unique_identification_keys_dict[key] = str(hh_id)

    def detect_collision(self, household: Household) -> Optional[str]:
        self.initialize()
        return self.unique_identification_keys_dict.get(household.identification_key, None)


collision_detectors_registry = Registry(AbstractCollisionDetector)
collision_detectors_registry.append(IdentificationKeyCollisionDetector)
