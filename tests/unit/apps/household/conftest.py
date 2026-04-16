from typing import Any, Callable

import pytest
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Household, Individual, Program


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def es_program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(business_area=afghanistan, status=Program.DRAFT)
    program.status = Program.ACTIVE
    program.save()
    return program


@pytest.fixture
def es_user(afghanistan: BusinessArea, create_user_role_with_permissions: Callable) -> Any:
    partner = PartnerFactory(name="ESSearchPartner")
    user = UserFactory(partner=partner)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    return user


@pytest.fixture
def es_client(api_client: Callable, es_user: Any) -> Any:
    return api_client(es_user)


@pytest.fixture
def individuals_list_url(afghanistan: BusinessArea, es_program: Program) -> str:
    return reverse(
        "api:households:individuals-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": es_program.code},
    )


@pytest.fixture
def individual_john_smith(es_program: Program) -> Individual:
    ind = IndividualFactory(program=es_program, full_name="John Smith")
    ind.unicef_id = "IND-0000001"
    ind.save(update_fields=["unicef_id"])
    return ind


@pytest.fixture
def household_with_address(es_program: Program) -> Household:
    return HouseholdFactory(program=es_program, address="Main Street 5, Aleppo")


@pytest.fixture
def individual_in_addressed_household(es_program: Program, household_with_address: Household) -> Individual:
    return IndividualFactory(
        program=es_program,
        household=household_with_address,
        full_name="Alice Aleppan",
    )
