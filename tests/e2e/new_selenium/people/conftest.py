from datetime import date

import pytest

from e2e.new_selenium.programme_population.conftest import create_pdu_attribute
from extras.test_utils.factories import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.const import HEAD, HOST, MALE, MARRIED, SEEING
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    Currency,
    DataCollectingType,
    FlexibleAttribute,
    Individual,
    Payment,
    Program,
    RegistrationDataImport,
)

PEOPLE_MENU = ("People",)


@pytest.fixture
def program(create_super_user: None, business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Worker Program",
        code="WORK",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingType.objects.filter(type=DataCollectingType.Type.SOCIAL).first(),
        beneficiary_group=BeneficiaryGroup.objects.get(name="People"),
    )


@pytest.fixture
def person(program: Program, business_area: BusinessArea) -> Individual:
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.MERGED, business_area=business_area, program=program
    )
    person = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        full_name="Stacey Freeman",
        given_name="Stacey",
        middle_name="",
        family_name="Freeman",
        sex=MALE,
        birth_date=date(1986, 1, 15),
        marital_status=MARRIED,
        pregnant=False,
        relationship=HEAD,
        observed_disability=[SEEING],
        email="stacey@example.com",
    )
    HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
        head_of_household=person,
        residence_status=HOST,
        village="Test Village",
        size=1,
    )
    # Document.country is nullable; a document without one must not break the person page or the grievance form.
    DocumentFactory(individual=person)
    person.refresh_from_db()
    return person


@pytest.fixture
def payment(person: Individual, program: Program) -> Payment:
    person.household.total_cash_received_usd = 21.36
    person.household.save()
    return PaymentFactory(
        parent=PaymentPlanFactory(
            name="TEST", program_cycle=program.cycles.first(), business_area=program.business_area
        ),
        household=person.household,
        collector=person,
        entitlement_quantity=21.36,
        delivered_quantity=21.36,
        currency=Currency.objects.get(code="PLN"),
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )


@pytest.fixture
def string_attribute(program: Program) -> FlexibleAttribute:
    return create_pdu_attribute(program, "Test String Attribute", FlexibleAttribute.STRING)


@pytest.fixture
def date_attribute(program: Program) -> FlexibleAttribute:
    return create_pdu_attribute(program, "Test Date Attribute", FlexibleAttribute.DATE)
