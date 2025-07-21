from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.extras.test_utils.factories.core import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import DataCollectingType
from tests.extras.test_utils.factories.household import create_household
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.validators import TargetingCriteriaInputValidator


class TestTargetingCriteriaInputValidator(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.program_standard = ProgramFactory(
            data_collecting_type=DataCollectingTypeFactory(
                type=DataCollectingType.Type.STANDARD,
                individual_filters_available=True,
                household_filters_available=True,
            )
        )
        cls.program_standard_hh_only = ProgramFactory(
            data_collecting_type=DataCollectingTypeFactory(
                type=DataCollectingType.Type.STANDARD,
                individual_filters_available=False,
                household_filters_available=True,
            )
        )
        cls.program_standard_ind_only = ProgramFactory(
            data_collecting_type=DataCollectingTypeFactory(
                type=DataCollectingType.Type.STANDARD,
                individual_filters_available=True,
                household_filters_available=False,
            )
        )
        cls.program_social = ProgramFactory(
            data_collecting_type=DataCollectingTypeFactory(
                type=DataCollectingType.Type.SOCIAL,
                individual_filters_available=True,
                household_filters_available=False,
            )
        )

    def test_TargetingCriteriaInputValidator(self) -> None:
        validator = TargetingCriteriaInputValidator
        create_household({"unicef_id": "HH-1", "size": 1}, {"unicef_id": "IND-12"})
        self._update_program(self.program_standard)
        validator.validate(
            {"rules": [{"Rule1": {"test": "123"}, "household_ids": "HH-1", "individual_ids": "IND-12"}]},
            self.program_standard,
        )

        with self.assertRaisesMessage(ValidationError, "Target criteria can only have individual ids"):
            self._update_program(self.program_standard_ind_only)
            validator.validate(
                {"rules": [{"household_ids": "HH-1", "individual_ids": "IND-12"}]}, self.program_standard_ind_only
            )

        with self.assertRaisesMessage(ValidationError, "There should be at least 1 rule in target criteria"):
            self._update_program(self.program_standard_hh_only)
            validator.validate({"rules": [], "household_ids": "", "individual_ids": ""}, self.program_standard_hh_only)

        with self.assertRaisesMessage(ValidationError, "The given households do not exist in the current program"):
            self._update_program(self.program_standard)
            validator.validate({"rules": [{"household_ids": "HH-666", "individual_ids": ""}]}, self.program_standard)

        with self.assertRaisesMessage(ValidationError, "The given individuals do not exist in the current program"):
            self._update_program(self.program_standard)
            validator.validate({"rules": [{"household_ids": "", "individual_ids": "IND-666"}]}, self.program_standard)

    def _update_program(self, program: Program) -> None:
        Household.objects.all().update(program=program)
        Individual.objects.all().update(program=program)
