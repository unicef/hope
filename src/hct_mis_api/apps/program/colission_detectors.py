from collections import defaultdict

from strategy_field.registry import Registry

from hct_mis_api.apps.household.models import Household


class AbstractCollisionDetector:
    def __init__(self, context: "Program"):
        self.program = context
        if not self.program.collision_detection_enabled:
            raise ValueError("Collision detection is not enabled for this program")

    def detect_collision(self, identifiaction_key: str):
        raise NotImplementedError("Subclasses should implement this method")

class IdentificationKeyCollisionDetector(AbstractCollisionDetector):

    def __init__(self, context: "Program"):
        super().__init__(context)
        self.unique_identification_keys_dict = None

    def initialize(self):
        if self.unique_identification_keys_dict is not None:
            return
        ids_with_uniquekey_list = list(
            Household.objects.filter(program=self.program).values_list("id", "unique_identification_key").distinct(
                "id"))
        for (hh_id, key) in ids_with_uniquekey_list:
            self.unique_identification_keys_dict[key] =str(hh_id)
    def detect_collision(self, identifiaction_key: str):
        self.initialize()
        return self.unique_identification_keys_dict.get(identifiaction_key, None)


collision_detectors_registry = Registry()
collision_detectors_registry.append(IdentificationKeyCollisionDetector)