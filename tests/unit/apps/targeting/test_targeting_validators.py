from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.models.data_collecting_type import DataCollectingType
from hope.models.flexible_attribute import FlexibleAttribute
from hope.models.household import Household
from hope.models.individual import Individual
from hope.models.program import Program
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.validators import (
    TargetingCriteriaInputValidator,
    TargetingCriteriaRuleFilterInputValidator,
)

pytestmark = pytest.mark.django_db


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

    def test_targeting_criteria_input_validator(self) -> None:
        validator = TargetingCriteriaInputValidator
        create_household({"unicef_id": "HH-1", "size": 1}, {"unicef_id": "IND-12"})
        self._update_program(self.program_standard)
        validator.validate(
            {
                "rules": [
                    {
                        "Rule1": {"test": "123"},
                        "household_ids": "HH-1",
                        "individual_ids": "IND-12",
                    }
                ]
            },
            self.program_standard,
        )

        with self.assertRaisesMessage(ValidationError, "Target criteria can only have individual ids"):
            self._update_program(self.program_standard_ind_only)
            validator.validate(
                {"rules": [{"household_ids": "HH-1", "individual_ids": "IND-12"}]},
                self.program_standard_ind_only,
            )

        with self.assertRaisesMessage(ValidationError, "There should be at least 1 rule in target criteria"):
            self._update_program(self.program_standard_hh_only)
            validator.validate(
                {"rules": [], "household_ids": "", "individual_ids": ""},
                self.program_standard_hh_only,
            )

        with self.assertRaisesMessage(ValidationError, "The given households do not exist in the current program"):
            self._update_program(self.program_standard)
            validator.validate(
                {"rules": [{"household_ids": "HH-666", "individual_ids": ""}]},
                self.program_standard,
            )

        with self.assertRaisesMessage(ValidationError, "The given individuals do not exist in the current program"):
            self._update_program(self.program_standard)
            validator.validate(
                {"rules": [{"household_ids": "", "individual_ids": "IND-666"}]},
                self.program_standard,
            )

    def _update_program(self, program: Program) -> None:
        Household.objects.all().update(program=program)
        Individual.objects.all().update(program=program)


class TestTargetingCriteriaRuleFilterInputValidator:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.program = MagicMock(spec=Program)
        self.program.name = "Test Program"
        self.field_name = "test_field"
        self.valid_rule_filter = {
            "flex_field_classification": FlexFieldClassification.NOT_FLEX_FIELD,
            "field_name": self.field_name,
            "comparison_method": "EQUAL",
            "arguments": [10],
        }

    def test_validation_error_core_field_not_found(self) -> None:
        with patch.object(FieldFactory, "from_scope", return_value=MagicMock(to_dict_by=lambda _: {})):
            with pytest.raises(
                ValidationError,
                match=f"Can't find any core field attribute associated with {self.field_name} field name",
            ):
                TargetingCriteriaRuleFilterInputValidator.validate(self.valid_rule_filter, self.program)

    def test_validation_error_flex_field_basic_not_found(self) -> None:
        rule_filter = self.valid_rule_filter.copy()
        rule_filter["flex_field_classification"] = FlexFieldClassification.FLEX_FIELD_BASIC

        with patch.object(FlexibleAttribute.objects, "get", side_effect=FlexibleAttribute.DoesNotExist):
            with pytest.raises(
                ValidationError,
                match=f"Can't find any flex field attribute associated with {self.field_name} field name",
            ):
                TargetingCriteriaRuleFilterInputValidator.validate(rule_filter, self.program)

    def test_validation_error_flex_field_pdu_not_found(self) -> None:
        rule_filter = self.valid_rule_filter.copy()
        rule_filter["flex_field_classification"] = "FLEX_FIELD_PDU"

        with patch.object(FlexibleAttribute.objects, "get", side_effect=FlexibleAttribute.DoesNotExist):
            with pytest.raises(
                ValidationError,
                match=f"Can't find PDU flex field attribute associated with {self.field_name} "
                f"field name in program {self.program.name}",
            ):
                TargetingCriteriaRuleFilterInputValidator.validate(rule_filter, self.program)
