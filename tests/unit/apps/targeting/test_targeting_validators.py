from unittest.mock import MagicMock, patch

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
)
from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.validators import (
    TargetingCriteriaInputValidator,
    TargetingCriteriaRuleFilterInputValidator,
)
from hope.models import DataCollectingType, FlexibleAttribute, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program_standard(business_area):
    return ProgramFactory(
        business_area=business_area,
        data_collecting_type=DataCollectingTypeFactory(
            type=DataCollectingType.Type.STANDARD,
            individual_filters_available=True,
            household_filters_available=True,
        ),
    )


@pytest.fixture
def program_standard_hh_only(business_area):
    return ProgramFactory(
        business_area=business_area,
        data_collecting_type=DataCollectingTypeFactory(
            type=DataCollectingType.Type.STANDARD,
            individual_filters_available=False,
            household_filters_available=True,
        ),
    )


@pytest.fixture
def program_standard_ind_only(business_area):
    return ProgramFactory(
        business_area=business_area,
        data_collecting_type=DataCollectingTypeFactory(
            type=DataCollectingType.Type.STANDARD,
            individual_filters_available=True,
            household_filters_available=False,
        ),
    )


@pytest.fixture
def program_social(business_area):
    return ProgramFactory(
        business_area=business_area,
        data_collecting_type=DataCollectingTypeFactory(
            type=DataCollectingType.Type.SOCIAL,
            individual_filters_available=True,
            household_filters_available=False,
        ),
    )


@pytest.fixture
def household(program_standard):
    return HouseholdFactory(unicef_id="HH-1", size=1, program=program_standard)


@pytest.fixture
def individual(program_standard, household):
    return IndividualFactory(unicef_id="IND-12", household=household, program=program_standard)


@pytest.fixture
def program_mock():
    program = MagicMock(spec=Program)
    program.name = "Test Program"
    return program


@pytest.fixture
def base_rule_filter():
    return {
        "flex_field_classification": FlexFieldClassification.NOT_FLEX_FIELD,
        "field_name": "test_field",
        "comparison_method": "EQUAL",
        "arguments": [10],
    }


def test_validate_accepts_valid_household_and_individual_ids(
    program_standard,
    household,
    individual,
):
    TargetingCriteriaInputValidator.validate(
        {
            "rules": [
                {
                    "Rule1": {"test": "123"},
                    "household_ids": "HH-1",
                    "individual_ids": "IND-12",
                }
            ]
        },
        program_standard,
    )


def test_validate_rejects_household_ids_when_only_individual_filters_allowed(
    program_standard_ind_only,
    household,
    individual,
):
    household.program = program_standard_ind_only
    household.save()
    individual.program = program_standard_ind_only
    individual.save()

    with pytest.raises(ValidationError, match="Target criteria can only have individual ids"):
        TargetingCriteriaInputValidator.validate(
            {"rules": [{"household_ids": "HH-1", "individual_ids": "IND-12"}]},
            program_standard_ind_only,
        )


def test_validate_rejects_empty_rules(program_standard_hh_only):
    with pytest.raises(ValidationError, match="There should be at least 1 rule in target criteria"):
        TargetingCriteriaInputValidator.validate(
            {"rules": [], "household_ids": "", "individual_ids": ""},
            program_standard_hh_only,
        )


def test_validate_rejects_nonexistent_household(program_standard):
    with pytest.raises(
        ValidationError,
        match="The given households do not exist in the current program",
    ):
        TargetingCriteriaInputValidator.validate(
            {"rules": [{"household_ids": "HH-666", "individual_ids": ""}]},
            program_standard,
        )


def test_validate_rejects_nonexistent_individual(program_standard):
    with pytest.raises(
        ValidationError,
        match="The given individuals do not exist in the current program",
    ):
        TargetingCriteriaInputValidator.validate(
            {"rules": [{"household_ids": "", "individual_ids": "IND-666"}]},
            program_standard,
        )


def test_rule_filter_validation_error_when_core_field_not_found(program_mock, base_rule_filter):
    with patch.object(FieldFactory, "from_scope", return_value=MagicMock(to_dict_by=lambda _: {})):
        with pytest.raises(
            ValidationError,
            match="Can't find any core field attribute associated with test_field field name",
        ):
            TargetingCriteriaRuleFilterInputValidator.validate(base_rule_filter, program_mock)


def test_rule_filter_validation_error_when_flex_field_basic_not_found(program_mock, base_rule_filter):
    rule_filter = base_rule_filter | {"flex_field_classification": FlexFieldClassification.FLEX_FIELD_BASIC}

    with patch.object(FlexibleAttribute.objects, "get", side_effect=FlexibleAttribute.DoesNotExist):
        with pytest.raises(
            ValidationError,
            match="Can't find any flex field attribute associated with test_field field name",
        ):
            TargetingCriteriaRuleFilterInputValidator.validate(rule_filter, program_mock)


def test_rule_filter_validation_error_when_flex_field_pdu_not_found(program_mock, base_rule_filter):
    rule_filter = base_rule_filter | {"flex_field_classification": "FLEX_FIELD_PDU"}

    with patch.object(FlexibleAttribute.objects, "get", side_effect=FlexibleAttribute.DoesNotExist):
        with pytest.raises(
            ValidationError,
            match=("Can't find PDU flex field attribute associated with test_field field name in program Test Program"),
        ):
            TargetingCriteriaRuleFilterInputValidator.validate(rule_filter, program_mock)
