from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.targeting.validators import TargetingCriteriaInputValidator


class TestTargetingCriteriaInputValidator(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.dct_standard = DataCollectingTypeFactory(
            type=DataCollectingType.Type.STANDARD,
            individual_filters_available=True,
            household_filters_available=True,
        )
        cls.dct_standard_hh_only = DataCollectingTypeFactory(
            type=DataCollectingType.Type.STANDARD,
            individual_filters_available=False,
            household_filters_available=True,
        )
        cls.dct_standard_ind_only = DataCollectingTypeFactory(
            type=DataCollectingType.Type.STANDARD,
            individual_filters_available=True,
            household_filters_available=False,
        )
        cls.dct_social = DataCollectingTypeFactory(
            type=DataCollectingType.Type.SOCIAL,
            individual_filters_available=True,
            household_filters_available=False,
        )

    def test_TargetingCriteriaInputValidator(self) -> None:
        validator = TargetingCriteriaInputValidator
        with self.assertRaisesMessage(
            ValidationError, "Target criteria can has only filters or ids, not possible to has both"
        ):
            validator.validate(
                {"rules": ["Rule1"], "household_ids": "HH-1", "individual_ids": "IND-1"}, self.dct_standard
            )

        with self.assertRaisesMessage(ValidationError, "Target criteria can has only individual ids"):
            validator.validate({"rules": [], "household_ids": "HH-1", "individual_ids": "IND-1"}, self.dct_social)
            validator.validate(
                {"rules": [], "household_ids": "HH-1", "individual_ids": "IND-1"}, self.dct_standard_ind_only
            )

        with self.assertRaisesMessage(ValidationError, "Target criteria can has only household ids"):
            validator.validate(
                {"rules": [], "household_ids": "HH-1", "individual_ids": "IND-1"}, self.dct_standard_hh_only
            )

        with self.assertRaisesMessage(ValidationError, "There should be at least 1 rule in target criteria"):
            validator.validate({"rules": [], "household_ids": "", "individual_ids": ""}, self.dct_standard_hh_only)
